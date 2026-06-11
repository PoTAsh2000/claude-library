#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook.
Scans user prompts for Excel file references and injects converted markdown
as additionalContext so Claude can answer without needing to Read binary files.
"""
import datetime
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

MAX_CONTEXT_CHARS = 9500
EXCEL_KEYWORDS = re.compile(r"\b(excel|spreadsheet|worksheet|\.xlsx|\.xls|\.xlsm)\b", re.IGNORECASE)

# Path patterns ordered by specificity (quoted @ notation first to handle spaces)
EXCEL_PATH_PATTERNS = [
    re.compile(r"""@'([^']+\.(?:xlsx|xls|xlsm))'""", re.IGNORECASE),
    re.compile(r'''@"([^"]+\.(?:xlsx|xls|xlsm))"''', re.IGNORECASE),
    re.compile(r"""@([^\s'"]+\.(?:xlsx|xls|xlsm))""", re.IGNORECASE),
    re.compile(r"""(?<![/\\])([A-Za-z]:[/\\][^\s'"*?<>|]+\.(?:xlsx|xls|xlsm))""", re.IGNORECASE),
    re.compile(r"""(?<!['\"])(/[a-zA-Z]/[^\s'"]+\.(?:xlsx|xls|xlsm))""", re.IGNORECASE),
    re.compile(r"""(?<!['\"])(/(?![a-zA-Z]/)(?!c/)[^\s'"]+\.(?:xlsx|xls|xlsm))""", re.IGNORECASE),
]


def debug_log(message):
    try:
        tmp = os.path.join(
            os.environ.get("USERPROFILE", os.environ.get("HOME", "")),
            "AppData", "Local", "Temp"
        ) if os.name == "nt" else "/tmp"
        log_path = os.path.join(tmp, "excel-hook-debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} [UserPromptSubmit] {message}\n")
    except Exception:
        pass


def normalize_path(p):
    """Convert Git Bash POSIX /c/Users/... to C:/Users/... on Windows."""
    if not p:
        return p
    m = re.match(r"^/([a-zA-Z])/(.*)", p)
    if m:
        return m.group(1).upper() + ":/" + m.group(2)
    return p


def find_excel_paths(prompt):
    found = []
    seen = set()
    for pattern in EXCEL_PATH_PATTERNS:
        for match in pattern.finditer(prompt):
            path = match.group(1).strip()
            if path not in seen:
                seen.add(path)
                found.append(path)
    return found


def resolve_reader():
    plugin_root = normalize_path(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
    if plugin_root:
        reader = os.path.join(plugin_root, "scripts", "read_excel.py")
        if os.path.exists(reader):
            return reader
    hook_dir = normalize_path(os.path.dirname(__file__).replace("\\", "/"))
    reader = hook_dir.rsplit("/hooks", 1)[0] + "/scripts/read_excel.py"
    return reader if os.path.exists(reader) else None


def convert_excel(path, reader):
    debug_log(f"[script-called] python3 {reader} {path!r}")
    result = subprocess.run(
        ["python3", reader, path],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return None, result.stderr.strip() or "Unknown error"
    return result.stdout, None


def emit_context(context):
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def main():
    debug_log("hook fired")

    try:
        payload = json.load(sys.stdin)
    except Exception:
        debug_log("failed to parse stdin JSON")
        sys.exit(0)

    prompt = payload.get("prompt", "")
    if not prompt:
        sys.exit(0)

    paths = find_excel_paths(prompt)

    if not paths:
        # No Excel paths found; emit a hint only if the prompt contains Excel keywords
        if EXCEL_KEYWORDS.search(prompt):
            debug_log("no paths found but Excel keywords present — emitting hint")
            emit_context(
                "No Excel file paths were detected in this prompt. "
                "To read an Excel file, include a reference such as: "
                "@'/path/to/file.xlsx' or @'C:/path/to/file.xlsx'"
            )
        else:
            debug_log("no Excel paths or keywords — silent exit")
        sys.exit(0)

    debug_log(f"found {len(paths)} Excel path(s): {paths}")

    reader = resolve_reader()
    if not reader:
        debug_log("read_excel.py not found — silent exit")
        sys.exit(0)

    parts = []
    budget_per_file = MAX_CONTEXT_CHARS // max(len(paths), 1)

    for raw_path in paths:
        norm_path = normalize_path(raw_path)
        debug_log(f"processing: {raw_path!r} → {norm_path!r}")

        if not os.path.exists(norm_path):
            debug_log(f"file not found: {norm_path!r}")
            parts.append(f"[excel-reader] File not found: {raw_path}")
            continue

        content, error = convert_excel(norm_path, reader)
        if error:
            debug_log(f"conversion failed: {error}")
            parts.append(f"[excel-reader] Failed to read {os.path.basename(raw_path)}: {error}")
        else:
            debug_log(f"conversion success, {len(content)} chars")
            if len(content) > budget_per_file:
                content = content[:budget_per_file] + "\n\n[... content truncated to fit context limit ...]"
            parts.append(content)

    if not parts:
        sys.exit(0)

    context = "\n\n---\n\n".join(parts)
    debug_log(f"emitting additionalContext ({len(context)} chars)")
    emit_context(context)


if __name__ == "__main__":
    main()
