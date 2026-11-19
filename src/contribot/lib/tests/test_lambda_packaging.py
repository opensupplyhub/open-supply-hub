"""Check that each ContriBot Lambda's zip contains every file its code imports.

Each Lambda is deployed as a zip. The Makefile in
``deployment/terraform/lambda-functions/contribot_*`` decides which files go
into it, using a list of files to copy.

Our other tests import the handlers straight from ``src/contribot``, where every
file exists, so they can't tell if a Makefile forgot one. When that happens the
Lambda fails in AWS with ``Unable to import module 'handler': No module named
...`` before it reads any list. That is what happened in OSDEV-3884:
``lib/os_hub_api.py`` was missing from the ``process_list`` zip.

These tests build each zip with its real Makefile, open the handler inside it,
follow every import that points at our own code, and fail if any of those files
isn't in the zip. They don't check third-party packages like ``pandas``; those
are installed from ``requirements.txt`` when the zip is built.
"""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Callable

import pytest

CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = CONTRIBOT_DIR.parents[1]
LAMBDA_FUNCTIONS_DIR = REPO_ROOT / "deployment" / "terraform" / "lambda-functions"

EXPECTED_LAMBDAS = {
    "contribot_fetch_lists",
    "contribot_process_list",
    "contribot_notify",
    "contribot_retry_failed_lists",
}

LAMBDA_DIRS = sorted(
    path
    for path in LAMBDA_FUNCTIONS_DIR.glob("contribot_*")
    if (path / "Makefile").is_file()
)


def _packaged_path_for(module: str, handler_dir: Path) -> str | None:
    """Say where a module would sit inside the zip, if it's our own code.

    For example ``lib.os_hub_api`` becomes ``lib/os_hub_api.py``. A module counts
    as ours if its file exists in the Lambda's own folder (for example
    ``process_list/``) or under ``src/contribot``. Anything else, like ``boto3``
    or ``pandas``, returns ``None`` because we don't package it ourselves.
    """
    parts = module.split(".")
    for root in (handler_dir, CONTRIBOT_DIR):
        # An import can point at a plain file (a/b.py) or a package (a/b/__init__.py).
        for candidate in (
            Path(*parts[:-1]) / f"{parts[-1]}.py",
            Path(*parts) / "__init__.py",
        ):
            if (root / candidate).is_file():
                return candidate.as_posix()
    return None


def _imported_modules(source: str, package: str) -> set[str]:
    """List every module that a piece of Python code imports.

    This includes imports tucked inside functions, since those fail at runtime
    too. ``package`` is the folder the file sits in inside the zip: ``""`` for a
    file at the top, ``"lib"`` for ``lib/utils.py``. We need it to work out what
    a relative import means, for example ``from .utils import x`` in a ``lib``
    file is ``lib.utils``.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                # Relative import: each extra dot climbs one package up.
                base = package.split(".") if package else []
                base = base[: len(base) - (node.level - 1)]
                module = ".".join(base + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            if not module:
                continue
            found.add(module)
            # "from lib import utils" could mean the module lib.utils, so list
            # that too and let the caller check whether the file exists.
            found.update(f"{module}.{alias.name}" for alias in node.names)
    return found


def missing_from_zip(
    zip_names: set[str],
    read_source: Callable[[str], str],
    handler_dir: Path,
) -> dict[str, set[str]]:
    """Find our own files that the handler needs but the zip doesn't contain.

    Start at ``handler.py`` and follow its imports. Then open each file it
    imports and follow that file's imports too, so a file needed only by another
    file is still caught. The result maps each missing file to the files that
    import it, for example ``{"lib/os_hub_api.py": {"handler.py"}}``. An empty
    result means the zip is complete.

    ``zip_names`` is the list of paths inside the zip, and ``read_source`` gives
    back the code of one of them.
    """
    missing: dict[str, set[str]] = {}
    seen: set[str] = set()
    to_check = ["handler.py"]
    while to_check:
        path = to_check.pop()
        if path in seen:
            continue
        seen.add(path)
        package = ".".join(Path(path).parent.parts)
        for module in _imported_modules(read_source(path), package):
            needed = _packaged_path_for(module, handler_dir)
            if needed is None:
                continue
            # Python also needs the __init__.py of every package on the way
            # down, so require those as well (for example lib/__init__.py).
            required = [needed]
            for ancestor in Path(needed).parents:
                init = (ancestor / "__init__.py").as_posix()
                if ancestor.parts and (CONTRIBOT_DIR / init).is_file():
                    required.append(init)
            for item in required:
                if item in zip_names:
                    to_check.append(item)
                else:
                    missing.setdefault(item, set()).add(path)
    return missing


@pytest.fixture(scope="module")
def build_lambda_zip(tmp_path_factory):
    """Give tests a function that builds one Lambda's zip and returns its path.

    The Makefile is copied to a temporary folder and pointed at the real source
    with ``CONTRIBOT_SRC``, so the build leaves nothing behind in the repo. We
    also put a fake ``pip`` that does nothing at the front of ``PATH``. The
    Makefile normally runs ``pip install`` to fetch dependencies, and these tests
    only care which of our files end up in the zip, so skipping that keeps the
    tests quick and means they don't need internet access.
    """
    if shutil.which("make") is None or shutil.which("zip") is None:
        pytest.skip("make and zip are needed to build the Lambda zips")

    def build(lambda_dir: Path) -> Path:
        workdir = tmp_path_factory.mktemp(lambda_dir.name)
        shutil.copy(lambda_dir / "Makefile", workdir / "Makefile")
        stub_bin = workdir / "stub-bin"
        stub_bin.mkdir()
        pip = stub_bin / "pip"
        pip.write_text("#!/bin/sh\nexit 0\n")
        pip.chmod(0o755)
        env = {**os.environ, "PATH": f"{stub_bin}{os.pathsep}{os.environ['PATH']}"}
        result = subprocess.run(
            ["make", "-C", str(workdir), f"CONTRIBOT_SRC={CONTRIBOT_DIR}"],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        zips = list(workdir.glob("*.zip"))
        assert len(zips) == 1, f"expected one zip, found {zips}"
        return zips[0]

    return build


def test_every_contribot_lambda_is_covered():
    """Make sure the zip check below is actually running on all four Lambdas.

    That check is generated from whatever Lambda folders it finds. If the folder
    moved or got renamed, it would find none and pass without testing anything.
    This test fails in that case. When you add a new ContriBot Lambda, add it to
    ``EXPECTED_LAMBDAS`` too.
    """
    assert {path.name for path in LAMBDA_DIRS} == EXPECTED_LAMBDAS


@pytest.mark.parametrize("lambda_dir", LAMBDA_DIRS, ids=lambda path: path.name)
def test_zip_contains_every_module_the_handler_imports(lambda_dir, build_lambda_zip):
    """Build each Lambda's zip and check nothing its code imports is missing.

    This is the test that would have caught OSDEV-3884. If the handler, or any
    file it uses, imports one of our files that the Makefile doesn't copy, the
    test fails and names the missing file and what imports it. That way we find
    out here and not when the Lambda fails in AWS.
    """
    handler_dir = CONTRIBOT_DIR / lambda_dir.name.removeprefix("contribot_")
    with zipfile.ZipFile(build_lambda_zip(lambda_dir)) as zf:
        names = set(zf.namelist())
        assert "handler.py" in names, "the zip has no handler.py at its root"
        missing = missing_from_zip(
            names, lambda path: zf.read(path).decode("utf-8"), handler_dir
        )
    report = {path: sorted(users) for path, users in missing.items()}
    assert not missing, (
        f"{lambda_dir.name} is missing files its code imports "
        f"(add them to its Makefile): {report}"
    )


def test_process_list_zip_ships_os_hub_api(build_lambda_zip):
    """Check the one file whose absence broke list #9809, by name.

    The general test above would catch this too. This one is here so the
    original failure stays easy to find if someone ever searches for it.
    """
    lambda_dir = LAMBDA_FUNCTIONS_DIR / "contribot_process_list"
    with zipfile.ZipFile(build_lambda_zip(lambda_dir)) as zf:
        assert "lib/os_hub_api.py" in zf.namelist()


def test_checker_reports_a_module_missing_from_the_zip():
    """Check that the checker really does report a missing file.

    We fake the OSDEV-3884 situation: a handler that imports ``lib.os_hub_api``
    and a zip without that file. Without this test, a bug in the checker could
    make the real tests pass while quietly checking nothing.
    """
    sources = {
        "handler.py": "from lib.os_hub_api import OSHubAPI\n",
        "lib/__init__.py": "",
    }
    names = {"handler.py", "lib/__init__.py"}
    missing = missing_from_zip(
        names, sources.__getitem__, CONTRIBOT_DIR / "process_list"
    )
    assert missing == {"lib/os_hub_api.py": {"handler.py"}}


def test_checker_follows_imports_between_lib_modules():
    """Check that the checker catches a file needed by another file, not the handler.

    We fake a handler that imports ``lib.contribot``, which is in the zip. That
    file in turn imports ``.utils``, which isn't. The handler never mentions
    ``utils``, so the checker has to open ``lib/contribot.py`` to notice.
    """
    sources = {
        "handler.py": "from lib.contribot import ContriBot\n",
        "lib/__init__.py": "",
        "lib/contribot.py": "from .utils import helper\n",
    }
    names = {"handler.py", "lib/__init__.py", "lib/contribot.py"}
    missing = missing_from_zip(
        names, sources.__getitem__, CONTRIBOT_DIR / "process_list"
    )
    assert missing == {"lib/utils.py": {"lib/contribot.py"}}
