#!/usr/bin/env python3
"""
Claude Code PreToolUse hook for the Read tool.
Intercepts reads of .xlsx/.xls/.xlsm files and returns markdown content instead.
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # Not valid JSON, allow

    file_path = payload.get("tool_input", {}).get("file_path", "")
    ext = os.path.splitext(file_path.lower())[1]

    if ext not in (".xlsx", ".xls", ".xlsm"):
        sys.exit(0)  # Not an Excel file, allow normal read

    # Locate read_excel.py relative to this hook script
    hook_dir = os.path.dirname(os.path.abspath(__file__))
    reader = os.path.normpath(os.path.join(hook_dir, "..", "scripts", "read_excel.py"))

    result = subprocess.run(
        ["python3", reader, file_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        # Reader failed; let Claude attempt the raw read and see the error
        sys.exit(0)

    response = {"decision": "block", "reason": result.stdout}
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
