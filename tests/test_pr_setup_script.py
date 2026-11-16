"""Tests for .cursor/scripts/pr-setup.sh token routing and start date.

The parent environment may contain a real GH_PROJECT_TOKEN. These tests pass
an explicit env and never forward that value into the script.
"""

import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".cursor" / "scripts" / "pr-setup.sh"
PR_URL = "https://github.com/gamaliel-ai/gamaliel-prompts/pull/999"
ASSIGN_CMD = (
    "api --method POST --input - "
    "repos/gamaliel-ai/gamaliel-prompts/issues/999/assignees"
)
START_DATE_CMD = (
    "project item-edit --id PVTI_item --project-id PVT_project "
    "--field-id start-field --date 2026-11-13"
)

FAKE_GH = """#!/usr/bin/env bash
set -euo pipefail
token="${GH_TOKEN-<unset>}"
printf '%s\\t%s\\n' "$token" "$*" >> "$GH_LOG"

cmd="$1"
sub="${2:-}"

if [[ "$cmd" == "pr" && "$sub" == "view" ]]; then
  if [[ "${FAIL_PR_VIEW:-}" == "1" ]]; then
    echo "view failed" >&2
    exit 1
  fi
  project_token="${GH_PROJECT_TOKEN-}"
  if [[ "${FAIL_PR_VIEW_DEFAULT:-}" == "1" \
    && "$token" != "$project_token" ]]; then
    echo "default auth cannot view pr" >&2
    exit 1
  fi
  if [[ "${BAD_PR_URL:-}" == "1" ]]; then
    echo '{"url":"not-a-github-url","number":999,"author":{"login":"octocat"}}'
    exit 0
  fi
  login="octocat"
  if [[ "${EMPTY_AUTHOR:-}" == "1" ]]; then
    login=""
  fi
  PR_JSON_URL="https://github.com/gamaliel-ai/gamaliel-prompts/pull/999" \\
    AUTHOR_LOGIN="$login" python3 -c 'import json, os, sys
login = os.environ["AUTHOR_LOGIN"]
author = None if login == "" else {"login": login}
json.dump(
    {"url": os.environ["PR_JSON_URL"], "number": 999, "author": author},
    sys.stdout,
)
print()
'
  exit 0
fi

if [[ "$cmd" == "api" && "$sub" == "--method" ]]; then
  cat >/dev/null
  if [[ "${FAIL_ASSIGN:-}" == "1" ]]; then
    echo "assign failed" >&2
    exit 1
  fi
  exit 0
fi

if [[ "$cmd" == "project" && "$sub" == "view" ]]; then
  echo '{"id":"PVT_project"}'
  exit 0
fi

if [[ "$cmd" == "project" && "$sub" == "item-add" ]]; then
  echo '{"id":"PVTI_item"}'
  exit 0
fi

if [[ "$cmd" == "project" && "$sub" == "item-edit" ]]; then
  exit 0
fi

if [[ "$cmd" == "api" && "$sub" == "graphql" ]]; then
  # Title comes from the environment so a malicious value is not expanded
  # by this stub before the script under test ever sees it.
  ITERATION_TITLE_OVERRIDE="${ITERATION_TITLE_OVERRIDE-Sprint 42}" \\
    python3 -c 'import json, os, sys
title = os.environ["ITERATION_TITLE_OVERRIDE"]
iteration = {
    "id": "iter-1",
    "title": title,
    "startDate": "2020-01-01",
    "duration": 100000,
}
sprint = {
    "id": "sprint-field",
    "configuration": {"iterations": [iteration]},
}
status = {
    "id": "status-field",
    "options": [{"id": "opt-ip", "name": "In progress"}],
}
proj = {
    "sprint": sprint,
    "status": status,
    "start": {"id": "start-field"},
}
body = {"data": {"organization": {"projectV2": proj}}}
json.dump(body, sys.stdout)
'
  exit 0
fi

echo "unexpected gh command: $*" >&2
exit 1
"""

# Returns the Pacific calendar date only when the caller sets TZ. A UTC
# fallback makes a missing TZ prefix fail the start-date test.
FAKE_DATE = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\t%s\\n' "${TZ-<unset>}" "$*" >> "$DATE_LOG"
if [[ "${TZ:-}" == "America/Los_Angeles" && "$*" == "+%Y-%m-%d" ]]; then
  echo "2026-11-13"
  exit 0
fi
echo "2026-11-14"
"""


def _run(tmp_path, extra_env, args=None):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh_path = bin_dir / "gh"
    gh_path.write_text(FAKE_GH)
    gh_path.chmod(0o755)
    date_path = bin_dir / "date"
    date_path.write_text(FAKE_DATE)
    date_path.chmod(0o755)
    log_path = tmp_path / "gh.log"
    date_log_path = tmp_path / "date.log"
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "GH_LOG": str(log_path),
        "DATE_LOG": str(date_log_path),
        "HOME": str(tmp_path),
        "LANG": "C.UTF-8",
        "TMPDIR": str(tmp_path),
    }
    env.update(extra_env)
    result = subprocess.run(
        ["bash", str(SCRIPT), *(args if args is not None else [PR_URL])],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    calls = []
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            token, _, command = line.partition("\t")
            calls.append((token, command))
    return result, calls


def _tokens(calls, prefix):
    return [token for token, command in calls if command.startswith(prefix)]


def _commands(calls, prefix):
    return [command for _, command in calls if command.startswith(prefix)]


def _assign_commands(calls):
    return [command for _, command in calls if "assignees" in command]


def test_unset_token_uses_ambient_auth(tmp_path):
    result, calls = _run(tmp_path, {})

    assert result.returncode == 0, result.stderr
    assert _tokens(calls, "pr view") == ["<unset>"]
    assert _commands(calls, "pr edit") == []
    assert _assign_commands(calls) == [ASSIGN_CMD]
    assert _tokens(calls, "api --method POST") == ["<unset>"]
    assert _tokens(calls, "project view") == ["<unset>"]
    assert _tokens(calls, "project item-add") == ["<unset>"]
    assert _tokens(calls, "api graphql") == ["<unset>"]
    assert _tokens(calls, "project item-edit") == [
        "<unset>",
        "<unset>",
        "<unset>",
    ]
    assert "Assigned octocat to" in result.stdout
    assert "@me" not in result.stdout
    assert "jglovier" not in result.stdout
    joined = " ".join(command for _, command in calls)
    assert "@me" not in joined
    assert "jglovier" not in joined
    assert "Set Sprint to Sprint 42" in result.stdout
    assert "Set Status to In progress" in result.stdout
    assert "Set Project Start date to 2026-11-13" in result.stdout


def test_start_date_uses_los_angeles_calendar_date(tmp_path):
    """Pacific evening is already the next UTC day. Use Los Angeles."""
    result, calls = _run(tmp_path, {"TZ": "UTC"})

    assert result.returncode == 0, result.stderr
    assert "Set Project Start date to 2026-11-13" in result.stdout
    assert "2026-11-14" not in result.stdout
    date_edits = [command for _, command in calls if "--date " in command]
    assert date_edits == [START_DATE_CMD]
    date_log = (tmp_path / "date.log").read_text().splitlines()
    assert date_log == ["America/Los_Angeles\t+%Y-%m-%d"]


def test_project_token_is_used_for_pr_read_and_roadmap(tmp_path):
    result, calls = _run(
        tmp_path,
        {"GH_TOKEN": "ambient-token", "GH_PROJECT_TOKEN": "project-token"},
    )

    assert result.returncode == 0, result.stderr
    assert _tokens(calls, "pr view") == ["project-token"]
    view = f"pr view {PR_URL} --json url,number,author"
    assert _commands(calls, "pr view") == [view]
    assert _commands(calls, "pr edit") == []
    assert _assign_commands(calls) == [ASSIGN_CMD]
    assert _tokens(calls, "api --method POST") == ["project-token"]
    assert _tokens(calls, "project view") == ["project-token"]
    assert _tokens(calls, "project item-add") == ["project-token"]
    assert _tokens(calls, "api graphql") == ["project-token"]
    assert _tokens(calls, "project item-edit") == [
        "project-token",
        "project-token",
        "project-token",
    ]
    assert "project-token" not in result.stdout
    assert "project-token" not in result.stderr
    assert "ambient-token" not in result.stdout
    assert "ambient-token" not in result.stderr


def test_project_token_reads_pr_when_ambient_cannot(tmp_path):
    """The cloud-agent token cannot read pull requests."""
    result, calls = _run(
        tmp_path,
        {
            "GH_TOKEN": "ambient-token",
            "GH_PROJECT_TOKEN": "project-token",
            "FAIL_PR_VIEW_DEFAULT": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    assert _tokens(calls, "pr view") == ["project-token"]
    assert "ambient-token" not in result.stdout
    assert "ambient-token" not in result.stderr
    assert _assign_commands(calls) == [ASSIGN_CMD]
    assert "Assigned octocat to" in result.stdout
    assert "Set Sprint to Sprint 42" in result.stdout
    assert "project-token" not in result.stdout
    assert "project-token" not in result.stderr


def test_pr_lookup_failure_does_not_retry_with_ambient_token(tmp_path):
    result, calls = _run(
        tmp_path,
        {
            "GH_TOKEN": "ambient-token",
            "GH_PROJECT_TOKEN": "project-token",
            "FAIL_PR_VIEW": "1",
        },
    )

    assert result.returncode != 0
    assert _tokens(calls, "pr view") == ["project-token"]
    assert _assign_commands(calls) == []
    assert _tokens(calls, "project ") == []
    assert "Failed to read the pull request." in result.stderr
    assert "view failed" in result.stderr
    assert "ambient-token" not in result.stdout
    assert "ambient-token" not in result.stderr
    assert "project-token" not in result.stdout
    assert "project-token" not in result.stderr
    assert "Added to project" not in result.stdout


def test_assignee_failure_exits_without_another_token(tmp_path):
    result, calls = _run(
        tmp_path,
        {
            "GH_TOKEN": "ambient-token",
            "GH_PROJECT_TOKEN": "project-token",
            "FAIL_ASSIGN": "1",
        },
    )

    assert result.returncode != 0
    assert "Failed to assign octocat" in result.stderr
    assert "assign failed" in result.stderr
    assert "Assigned octocat" not in result.stdout
    assert _commands(calls, "pr edit") == []
    assert _assign_commands(calls) == [ASSIGN_CMD]
    assert _tokens(calls, "api --method POST") == ["project-token"]
    assert _tokens(calls, "project ") == []
    assert "Set Sprint to Sprint 42" not in result.stdout
    assert "ambient-token" not in result.stdout
    assert "ambient-token" not in result.stderr
    assert "project-token" not in result.stdout
    assert "project-token" not in result.stderr


def test_empty_author_exits(tmp_path):
    result, calls = _run(tmp_path, {"EMPTY_AUTHOR": "1"})

    assert result.returncode != 0
    assert "Could not read the PR author from gh pr view." in result.stderr
    assert _assign_commands(calls) == []
    assert _tokens(calls, "project ") == []
    assert "Set Sprint to Sprint 42" not in result.stdout


def test_unparsed_pr_url_exits(tmp_path):
    result, calls = _run(tmp_path, {"BAD_PR_URL": "1"})

    assert result.returncode != 0
    assert "Could not read the PR author from gh pr view." in result.stderr
    assert _assign_commands(calls) == []
    assert _tokens(calls, "project ") == []
    assert "Set Sprint to Sprint 42" not in result.stdout


def test_iteration_title_is_not_evaluated(tmp_path):
    """A sprint title is data. It must not run as shell or expand the token."""
    payload = "$(touch %s)${GH_TOKEN}`touch %s`" % (
        tmp_path / "pwned",
        tmp_path / "pwned-backtick",
    )
    command_file = tmp_path / "pwned"
    backtick_file = tmp_path / "pwned-backtick"
    token = "super-secret-token"
    result, calls = _run(
        tmp_path,
        {"GH_TOKEN": token, "ITERATION_TITLE_OVERRIDE": payload},
    )

    assert result.returncode == 0, result.stderr
    assert f"Set Sprint to {payload}" in result.stdout
    assert token not in result.stdout
    assert token not in result.stderr
    assert not command_file.exists()
    assert not backtick_file.exists()
    edited = _commands(calls, "project item-edit")
    assert edited[1].endswith("--iteration-id iter-1")
