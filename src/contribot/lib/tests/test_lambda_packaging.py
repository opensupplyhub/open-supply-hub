"""Check that each ContriBot Lambda zip ships every module its handler needs.

Each Lambda is built from a Makefile in
``deployment/terraform/lambda-functions/contribot_*`` that copies an explicit
list of files into a zip. The unit tests import the handlers from the full
source tree, so they pass even when a Makefile forgets a file. The Lambda then
fails in AWS with ``Unable to import module 'handler': No module named ...``
before it reads any list data (OSDEV-3884: ``lib/os_hub_api.py`` was missing
from the ``process_list`` zip).

These tests close that gap. They build every Lambda zip with its real Makefile
(``pip`` is stubbed out, so nothing is downloaded), read the handler out of the
zip, follow every import that points at ContriBot's own code, and fail if any
of those files is not in the zip. Third-party packages are not checked here;
they come from ``requirements.txt`` at build time.
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
    """Return where ``module`` sits in a Lambda zip, if it is ContriBot code.

    A module is ContriBot's own code when it resolves to a file under the
    handler's folder (shipped at the zip root) or under ``src/contribot`` (so
    ``lib.x`` is shipped as ``lib/x.py``). Anything else, such as ``boto3`` or
    ``pandas``, returns ``None`` because it is not ours to package.
    """
    parts = module.split(".")
    for root in (handler_dir, CONTRIBOT_DIR):
        for candidate in (
            Path(*parts[:-1]) / f"{parts[-1]}.py",
            Path(*parts) / "__init__.py",
        ):
            if (root / candidate).is_file():
                return candidate.as_posix()
    return None


def _imported_modules(source: str, package: str) -> set[str]:
    """List every module a file imports, including lazy imports in functions.

    ``package`` is the dotted package the file lives in inside the zip
    (``""`` for a file at the zip root, ``"lib"`` for ``lib/x.py``). It is
    needed to turn ``from .utils import x`` into ``lib.utils``. For
    ``from lib import x`` the name ``lib.x`` is listed too, since ``x`` may be a
    module and not an attribute.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".") if package else []
                base = base[: len(base) - (node.level - 1)]
                module = ".".join(base + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            if not module:
                continue
            found.add(module)
            found.update(f"{module}.{alias.name}" for alias in node.names)
    return found


def missing_from_zip(
    zip_names: set[str],
    read_source: Callable[[str], str],
    handler_dir: Path,
) -> dict[str, set[str]]:
    """Find ContriBot files the handler needs that the zip does not contain.

    Starting from ``handler.py``, follow every import that points at ContriBot
    code (and the ``__init__.py`` of each package it sits in), reading each
    file's own imports in turn. Returns ``{missing zip path: {files that import
    it}}``; an empty dict means the package is complete.
    """
    missing: dict[str, set[str]] = {}
    seen: set[str] = set()
    queue = ["handler.py"]
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        seen.add(path)
        package = ".".join(Path(path).parent.parts)
        for module in _imported_modules(read_source(path), package):
            needed = _packaged_path_for(module, handler_dir)
            if needed is None:
                continue
            required = [needed]
            for ancestor in Path(needed).parents:
                init = (ancestor / "__init__.py").as_posix()
                if ancestor.parts and (CONTRIBOT_DIR / init).is_file():
                    required.append(init)
            for item in required:
                if item in zip_names:
                    queue.append(item)
                else:
                    missing.setdefault(item, set()).add(path)
    return missing


@pytest.fixture(scope="module")
def build_lambda_zip(tmp_path_factory):
    """Return a function that builds one Lambda's zip and gives back its path.

    The Makefile is copied into a throwaway folder and pointed at the real
    source with ``CONTRIBOT_SRC``, so nothing is written into the repository.
    A do-nothing ``pip`` is put first on ``PATH`` so the build needs no network;
    the dependency install is not what these tests are about.
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
    """Make sure the parametrised check below is not silently empty.

    The test over ``LAMBDA_DIRS`` passes trivially if the folder moves and the
    glob finds nothing, so this pins the four Lambdas it must cover. Add a new
    Lambda here when one is created.
    """
    assert {path.name for path in LAMBDA_DIRS} == EXPECTED_LAMBDAS


@pytest.mark.parametrize("lambda_dir", LAMBDA_DIRS, ids=lambda path: path.name)
def test_zip_contains_every_module_the_handler_imports(lambda_dir, build_lambda_zip):
    """Build the real zip and check it can import everything it ships a handler for.

    This is the regression test for OSDEV-3884. If a handler (or a ``lib``
    module it uses) imports a ContriBot file that the Makefile does not copy,
    the failure names the file and who imports it, instead of the Lambda
    breaking in AWS.
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
    """Pin the exact file whose absence broke list #9809.

    The generic check above would also catch it; this keeps the original
    failure visible by name.
    """
    lambda_dir = LAMBDA_FUNCTIONS_DIR / "contribot_process_list"
    with zipfile.ZipFile(build_lambda_zip(lambda_dir)) as zf:
        assert "lib/os_hub_api.py" in zf.namelist()


def test_checker_reports_a_module_missing_from_the_zip():
    """Show the checker fails when a handler import is not in the zip.

    A made-up handler imports ``lib.os_hub_api`` but the made-up zip does not
    contain it, which is exactly the OSDEV-3884 situation. Without this, a bug
    in the checker could make the real tests pass while checking nothing.
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
    """Show the checker also catches a file needed by a file the handler needs.

    The handler imports ``lib.contribot`` (present), which itself imports
    ``.utils`` with a relative import (absent). The checker has to read
    ``lib/contribot.py`` and notice, since the handler never names ``utils``.
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
