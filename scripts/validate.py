#!/usr/bin/env python3
"""
validate.py - Validate a file or directory of files against theological guidelines using the remote API.

Usage:
  python validate.py <file_or_directory> [-fix] [-h/-H HOST]

- If a file is given, validate that file.
- If a directory is given, recursively validate all .yml, .yaml, .j2, and .md files.
- Use -fix to automatically fix violations using the edit endpoint.
- Use -h/-H/--host to override the API host (default: https://gamaliel.ai)
- Exits 1 if any violations are found, 0 if all are compliant.
"""
import sys
import os
import json
import argparse
import urllib.request
from pathlib import Path

class HostAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

def detect_files(target):
    p = Path(target)
    if p.is_file():
        return [p]
    elif p.is_dir():
        return [f for f in p.rglob("*") if f.suffix in VALID_EXTENSIONS]
    else:
        print(f"Target {target} not found.")
        sys.exit(2)

def validate_file(filepath, validation_endpoint):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    data = json.dumps({"content": content, "file_type": guess_file_type(filepath)})
    req = urllib.request.Request(
        validation_endpoint,
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

def fix_file(filepath, validation_result, edit_endpoint):
    """Fix violations in a file using the edit endpoint."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    data = json.dumps({
        "content": content,
        "validation_result": validation_result,
        "file_type": guess_file_type(filepath)
    })
    
    req = urllib.request.Request(
        edit_endpoint,
        data=data.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            return result.get("edited_content")
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return None

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

VALID_EXTENSIONS = {".yml", ".yaml", ".j2", ".md"}

def main():
    parser = argparse.ArgumentParser(description="Validate files against theological guidelines")
    parser.add_argument("target", help="File or directory to validate")
    parser.add_argument("-fix", action="store_true", help="Automatically fix violations")
    parser.add_argument("-H", "--host", action=HostAction, dest="host", default="https://gamaliel.ai", help="API host (default: https://gamaliel.ai)")
    
    # Handle -h as an alias for --host
    args, unknown = parser.parse_known_args()
    
    # Check if -h was used in unknown args
    for i, arg in enumerate(unknown):
        if arg == "-h" and i + 1 < len(unknown):
            args.host = unknown[i + 1]
            break
    
    api_base_url = args.host.rstrip("/")
    validation_endpoint = f"{api_base_url}/api/validate"
    edit_endpoint = f"{api_base_url}/api/edit"
    
    print(f"Using API: {api_base_url}")
    files = detect_files(args.target)
    any_violations = False
    fixed_files = []
    
    for f in files:
        result = validate_file(f, validation_endpoint)
        if not result.get("compliant", False):
            any_violations = True
            print(f"\nViolations in {f}:")
            for v in result.get("violations", []):
                print(f"- {v}")
            print(f"Summary: {result.get('summary','')}")
            
            if args.fix:
                print(f"Attempting to fix {f}...")
                edited_content = fix_file(f, result, edit_endpoint)
                if edited_content:
                    # Create backup
                    backup_path = f.with_suffix(f.suffix + ".backup")
                    with open(f, "r", encoding="utf-8") as original:
                        with open(backup_path, "w", encoding="utf-8") as backup:
                            backup.write(original.read())
                    
                    # Write fixed content
                    with open(f, "w", encoding="utf-8") as fixed:
                        fixed.write(edited_content)
                    
                    print(f"Fixed {f} (backup saved to {backup_path})")
                    fixed_files.append(f)
                else:
                    print(f"Failed to fix {f}")
        else:
            print(f"{f}: compliant.")
    
    if args.fix and fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for f in fixed_files:
            print(f"  - {f}")
        print("\nBackup files created with .backup extension")
    
    if any_violations:
        sys.exit(1)
    else:
        print("All files compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main() 