#!/usr/bin/env python3
"""
Claude Code PreToolUse hook for the Read tool.
Intercepts reads of .xlsx/.xls/.xlsm files and returns markdown content instead.
"""
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

EXCEL_EXTENSIONS = (".xlsx", ".xls", ".xlsm")


def normalize_path(p):
    """Convert Git Bash POSIX path /c/Users/... to C:/Users/... for Windows Python."""
    if not p:
        return p
    m = re.match(r"^/([a-zA-Z])/(.*)", p)
    if m:
        return m.group(1).upper() + ":/" + m.group(2)
    return p


def block_with_message(message):
    print(json.dumps({"decision": "block", "reason": message}))
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = payload.get("tool_input", {}).get("file_path", "")
    ext = os.path.splitext(file_path.lower())[1]

    if ext not in EXCEL_EXTENSIONS:
        sys.exit(0)

    file_path = normalize_path(file_path)

    # Resolve reader script via CLAUDE_PLUGIN_ROOT (set by Claude Code to the
    # install cache path with forward slashes, e.g. C:/Users/.../<hash>).
    plugin_root = normalize_path(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
    if plugin_root:
        reader = os.path.join(plugin_root, "scripts", "read_excel.py")
    else:
        # Fallback: derive from __file__ without os.path.abspath (which mangles POSIX paths)
        hook_dir = os.path.dirname(__file__).replace("\\", "/")
        hook_dir = normalize_path(hook_dir)
        reader = hook_dir.rsplit("/hooks", 1)[0] + "/scripts/read_excel.py"

    if not os.path.exists(reader):
        block_with_message(
            f"[excel-reader] Cannot locate read_excel.py at: {reader}\n"
            f"CLAUDE_PLUGIN_ROOT={os.environ.get('CLAUDE_PLUGIN_ROOT', '(not set)')}"
        )

    result = subprocess.run(
        ["python3", reader, file_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        error_detail = result.stderr.strip() or "Unknown error (no stderr output)"
        block_with_message(
            f"[excel-reader] Failed to read Excel file.\n\n"
            f"File: {file_path}\n"
            f"Error: {error_detail}\n\n"
            f"If openpyxl is missing: pip install openpyxl\n"
            f"For .xls legacy files: pip install xlrd"
        )

    print(json.dumps({"decision": "block", "reason": result.stdout}))
    sys.exit(0)


if __name__ == "__main__":
    main()
