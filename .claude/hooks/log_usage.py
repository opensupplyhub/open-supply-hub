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
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def _identity():
    """A stable per-user string for hashing. Prefers git user.email, then
    git user.name, then the OS username — so we still get a token even when
    user.email isn't explicitly configured (git auto-derives the author then,
    leaving `git config user.email` empty)."""
    for cmd in (["git", "config", "user.email"], ["git", "config", "user.name"]):
        try:
            out = subprocess.run(
                cmd, capture_output=True, text=True, timeout=2,
            ).stdout.strip()
            if out:
                return out
        except Exception:
            pass
    try:
        import getpass
        return getpass.getuser() or None
    except Exception:
        return None


def _user_hash():
    """Pseudonymous, stable per-user token — lets the sink count DISTINCT users
    without storing identities. Same identity -> same hash, so distinct-user
    counts work across machines. Set OSHUB_USAGE_LOG_SALT (shared across the
    team) to make re-identification of the small, known identity set harder;
    without it this is pseudo-anonymous, not anonymous."""
    ident = _identity()
    if not ident:
        return None
    salt = os.environ.get("OSHUB_USAGE_LOG_SALT", "")
    return hashlib.sha256((salt + ident.lower()).encode("utf-8")).hexdigest()[:16]


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
        "user_hash": _user_hash(),
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
    url = os.environ.get("OSHUB_USAGE_LOG_URL")
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
