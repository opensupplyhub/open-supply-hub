#!/usr/bin/env python3
"""Usage logger for Claude Code skills, sub-agents, and slash commands.

Wired up via .claude/settings.json hooks:
  - PreToolUse  (matcher Skill|Agent|Task) -> skills + sub-agents
  - UserPromptSubmit                        -> slash commands (lines starting "/")

Reads the hook payload as JSON on stdin and:
  1. ALWAYS appends one JSON line to .claude/usage-log.jsonl (fast, offline-safe,
     authoritative). This file is gitignored.
  2. If the OSHUB_USAGE_LOG_URL env var is set, best-effort POSTs the same line
     to that URL (e.g. a Google Apps Script web app that appends a row to a
     Sheet). The POST is backgrounded and fail-soft, so a slow/offline/missing
     endpoint never blocks or breaks a session.

The repo is PUBLIC, so no endpoint or secret is committed here — the sink URL
comes only from OSHUB_USAGE_LOG_URL. See .claude/hooks/README.md for setup.

This hook never blocks a tool call: it writes locally, optionally fires a
detached POST, prints nothing, and always exits 0.
"""
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone

_CFG = None


def _local_config():
    """Parse the optional, gitignored .claude/usage-sink.local (KEY=VALUE lines).

    Lets the central-sink URL live on the machine without being committed to this
    (public) repo and without each dev editing their shell profile — write it once
    (the /setup-usage-logging command does this) and it's picked up.
    """
    path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "usage-sink.local")
    )
    cfg = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                cfg[key.strip()] = val.strip().strip('"').strip("'")
    except Exception:
        pass
    return cfg


def _setting(key):
    """Env var wins; otherwise fall back to .claude/usage-sink.local."""
    global _CFG
    env = os.environ.get(key)
    if env:
        return env
    if _CFG is None:
        _CFG = _local_config()
    return _CFG.get(key)


def _user_token():
    """A stable, RANDOM per-user token — minted once, then reused forever.

    It's not derived from any identity (email/name/username), so there's nothing
    to reverse and no salt needed — it's genuinely anonymous, while still letting
    the sink count distinct users. 128 bits, so collisions are negligible.

    Persisted per OS user at ~/.claude/oshub-usage-uid (so it's stable across
    checkouts on this machine), falling back to a gitignored .claude/usage-uid in
    the repo if home isn't writable.
    """
    paths = []
    try:
        paths.append(os.path.join(os.path.expanduser("~/.claude"),
                                  "oshub-usage-uid"))
    except Exception:
        pass
    paths.append(os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "usage-uid")))

    for path in paths:  # reuse the first token we find
        try:
            with open(path, encoding="utf-8") as fh:
                tok = fh.read().strip()
            if tok:
                return tok
        except Exception:
            pass

    tok = secrets.token_hex(16)  # mint one and persist it
    for path in paths:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(tok + "\n")
            return tok
        except Exception:
            continue
    return tok  # couldn't persist (rare) — still usable for this run


def _classify(payload):
    """Return (kind, identifier) or (None, None) if this event isn't logged."""
    event = payload.get("hook_event_name")
    if event == "PreToolUse":
        tool = payload.get("tool_name")
        ti = payload.get("tool_input") or {}
        if tool == "Skill":
            # field name varies by CC version; check both
            return "skill", ti.get("skill") or ti.get("skill_name")
        if tool in ("Agent", "Task"):
            return "subagent", ti.get("subagent_type") or ti.get("agent_type")
        return None, None
    if event == "UserPromptSubmit":
        prompt = (payload.get("prompt") or "").strip()
        # UserPromptSubmit fires BEFORE slash-command expansion, so the raw
        # "/command ..." text is visible here.
        if prompt.startswith("/") and len(prompt) > 1:
            return "command", prompt[1:].split()[0]
        return None, None
    return None, None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # malformed input — never break the session

    kind, identifier = _classify(payload)
    if not kind:
        return  # not a skill/subagent/command event

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "id": identifier,
        "user_token": _user_token(),
        "session_id": payload.get("session_id"),
        "cwd": payload.get("cwd"),
    }
    line = json.dumps(entry, ensure_ascii=False)

    # 1. Local append — authoritative, offline-safe. Resolve the path relative
    # to this script so it works regardless of the hook's cwd.
    log_path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "usage-log.jsonl")
    )
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass

    # 2. Optional best-effort POST to a central sink (e.g. Google Sheet via an
    # Apps Script web app). Backgrounded + fail-soft; never blocks the tool.
    # URL comes from the env var or .claude/usage-sink.local (never committed).
    url = _setting("OSHUB_USAGE_LOG_URL")
    if url:
        try:
            subprocess.Popen(
                ["curl", "-s", "-m", "5", "-X", "POST",
                 "-H", "Content-Type: application/json",
                 "-d", line, url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
