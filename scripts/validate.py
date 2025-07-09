#!/usr/bin/env python3
"""
validate.py - Validate a file or directory of files against theological guardrails using the remote API.

Usage:
  python validate.py <file_or_directory>

- If a file is given, validate that file.
- If a directory is given, recursively validate all .yml, .yaml, .j2, and .md files.
- Exits 1 if any violations are found, 0 if all are compliant.
"""
import sys
import os
import json
import urllib.request
from pathlib import Path

API_BASE_URL = "https://gameliel-staging-client-nmwtd.ondigitalocean.app"
VALIDATION_ENDPOINT = f"{API_BASE_URL}/api/validate"

VALID_EXTENSIONS = {".yml", ".yaml", ".j2", ".md"}

def detect_files(target):
    p = Path(target)
    if p.is_file():
        return [p]
    elif p.is_dir():
        return [f for f in p.rglob("*") if f.suffix in VALID_EXTENSIONS]
    else:
        print(f"Target {target} not found.")
        sys.exit(2)

def validate_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    data = json.dumps({"content": content, "file_type": guess_file_type(filepath)})
    req = urllib.request.Request(
        VALIDATION_ENDPOINT,
        data=data.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            return result
    except Exception as e:
        print(f"Error validating {filepath}: {e}")
        sys.exit(2)

def guess_file_type(filepath):
    name = filepath.name.lower()
    if "profile" in name:
        return "User Profile"
    if "theology" in name:
        return "Theology"
    if name.endswith(".j2"):
        return "Prompt Template"
    if name.endswith(".md"):
        return "Markdown"
    return "Other"

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py <file_or_directory>")
        sys.exit(2)
    files = detect_files(sys.argv[1])
    any_violations = False
    for f in files:
        result = validate_file(f)
        if not result.get("compliant", False):
            any_violations = True
            print(f"\nViolations in {f}:")
            for v in result.get("violations", []):
                print(f"- {v}")
            print(f"Summary: {result.get('summary','')}")
        else:
            print(f"{f}: compliant.")
    if any_violations:
        sys.exit(1)
    else:
        print("All files compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main() 