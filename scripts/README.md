# Gamaliel Prompts Scripts

This directory contains utility scripts for contributors and maintainers of the Gamaliel Prompts repository.

### `validate.py`: Validate Files Against Theological Guardrails

`validate.py` is a zero-dependency Python 3 script that checks YAML, Markdown, and Jinja2 files for compliance with the core theological guardrails defined by the Gamaliel project. It uses the remote validator API to ensure all content aligns with essential Christian doctrines and project standards.

Use this tool to validate any content you are authoring. We will not consider any 
contributions that fail validation.

---

## Usage

You must have Python 3 installed. No other dependencies are required.

### Validate a Single File

```sh
python scripts/validate.py theologies/anglican.yml
```

### Validate All Files in a Directory (Recursively)

```sh
python scripts/validate.py theologies
```

This will check all `.yml`, `.yaml`, `.j2`, and `.md` files in the directory and its subdirectories.

---

## Output

- If all files are compliant:
  ```
  theologies/anglican.yml: compliant.
  All files compliant.
  ```
- If violations are found:
  ```
  Violations in profiles/problematic_profile.yml:
  - Trinity Denial
  - Universalist Claims
  Summary: Profile contains violations of core guardrails.
  ```
  The script will exit with code 1 if any violations are found, or 0 if all files are compliant.

---

## When to Use

- Before submitting a pull request, to ensure your changes comply with theological guidelines
- In CI workflows (already integrated in `.github/workflows/theological-review.yml`)
- For local development and content review

---

## Notes

- Only `.yml`, `.yaml`, `.j2`, and `.md` files are checked.
- If the API is unavailable, the script will exit with an error.

---

For more information, see the main [README](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md). 