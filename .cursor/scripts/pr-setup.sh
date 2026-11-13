#!/usr/bin/env bash
# Assigns the pull request's author, adds the PR to the Gamaliel Roadmap
# project, and sets Status to In progress, Sprint to the current iteration,
# and Project Start date to today.
#
# GH_PROJECT_TOKEN, when set, is a fine-grained token owned by the belovedbot
# machine user, with Projects, Pull requests, and Issues read/write on
# gamaliel-ai. Pass it only to assignment and Roadmap project commands:
#   GH_TOKEN="$GH_PROJECT_TOKEN" gh ...
# Never export it for the rest of the script. If one of those commands fails,
# print an error and exit non-zero. Do not retry with another token.
#
# Usage: .cursor/scripts/pr-setup.sh [pr-url-or-number]
#        (defaults to the PR for the current branch)
set -euo pipefail

OWNER="${GAMALIEL_PROJECT_OWNER:-gamaliel-ai}"
PROJECT_NUMBER="${GAMALIEL_PROJECT_NUMBER:-1}"

# Prefixes a single gh command. The assignment stays in this command's
# environment and is not exported to the rest of the script.
project_gh() {
  if [[ -n "${GH_PROJECT_TOKEN:-}" ]]; then
    GH_TOKEN="$GH_PROJECT_TOKEN" gh "$@"
  else
    gh "$@"
  fi
}

die() {
  printf '%s\n' "$1" >&2
  exit 1
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

PR_REF="${1:-}"
if [[ -n "$PR_REF" ]]; then
  if ! pr_json=$(gh pr view "$PR_REF" --json url,number,author); then
    die "Failed to read the pull request."
  fi
else
  if ! pr_json=$(gh pr view --json url,number,author); then
    die "Failed to read the pull request."
  fi
fi

# NUL-delimited values. Do not eval API data: a title or login can contain
# $(...), backticks, or ${VAR}, and a GitHub token may be in the environment.
printf '%s' "$pr_json" | python3 -c '
import json, re, sys
data = json.load(sys.stdin)
author = data.get("author") or {}
login = author.get("login") or ""
url = (data.get("url") or "").split("?", 1)[0].split("#", 1)[0]
number = data.get("number")
parts = url.split("/")
# https://github.com/<owner>/<repo>/pull/<number>
if (
    len(parts) < 7
    or parts[0] != "https:"
    or parts[2] != "github.com"
    or parts[5] != "pull"
    or not isinstance(number, int)
    or str(number) != parts[6]
    or not login
):
    sys.exit("Could not read the PR author from gh pr view.")
owner, repo = parts[3], parts[4]
login_re = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\[bot\])?")
owner_re = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?")
repo_re = re.compile(r"[A-Za-z0-9_.-]+")
if login_re.fullmatch(login) is None:
    sys.exit("PR author login from gh pr view is not a GitHub login.")
if owner in {".", ".."} or owner_re.fullmatch(owner) is None:
    sys.exit("Could not read the repository owner from the pull request URL.")
if repo in {".", ".."} or repo_re.fullmatch(repo) is None:
    sys.exit("Could not read the repository name from the pull request URL.")

def emit(value):
    sys.stdout.write(str(value) + "\0")

emit(url)
emit(number)
emit(login)
emit(owner)
emit(repo)
' >"$tmp_dir/pr"

{
  IFS= read -r -d '' PR_URL || exit 1
  IFS= read -r -d '' PR_NUMBER || exit 1
  IFS= read -r -d '' AUTHOR_LOGIN || exit 1
  IFS= read -r -d '' REPO_OWNER || exit 1
  IFS= read -r -d '' REPO_NAME || exit 1
} <"$tmp_dir/pr"

# Issue assignees API. The login is the PR author from gh pr view --json author.
if ! python3 -c 'import json,sys; json.dump({"assignees":[sys.argv[1]]}, sys.stdout)' \
  "$AUTHOR_LOGIN" \
  | project_gh api --method POST --input - \
    "repos/${REPO_OWNER}/${REPO_NAME}/issues/${PR_NUMBER}/assignees" >/dev/null
then
  die "Failed to assign ${AUTHOR_LOGIN} to ${PR_URL}."
fi
printf 'Assigned %s to %s\n' "$AUTHOR_LOGIN" "$PR_URL"

if ! project_json=$(project_gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json); then
  die "Failed to read Gamaliel Roadmap project ${PROJECT_NUMBER}."
fi
PROJECT_ID=$(printf '%s' "$project_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

if ! item_json=$(project_gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$PR_URL" --format json); then
  die "Failed to add ${PR_URL} to Gamaliel Roadmap project ${PROJECT_NUMBER}."
fi
ITEM_ID=$(printf '%s' "$item_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
printf 'Added to project %s as item %s\n' "$PROJECT_NUMBER" "$ITEM_ID"

if ! FIELDS_JSON=$(project_gh api graphql -f owner="$OWNER" -F number="$PROJECT_NUMBER" -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      sprint: field(name: "Sprint") {
        ... on ProjectV2IterationField {
          id
          configuration { iterations { id title startDate duration } }
        }
      }
      status: field(name: "Status") {
        ... on ProjectV2SingleSelectField {
          id
          options { id name }
        }
      }
      start: field(name: "Project Start date") {
        ... on ProjectV2Field { id }
      }
    }
  }
}'); then
  die "Failed to read Gamaliel Roadmap fields."
fi

printf '%s' "$FIELDS_JSON" | python3 -c '
import datetime, json, sys
proj = json.load(sys.stdin)["data"]["organization"]["projectV2"]
today = datetime.date.today()

def emit(value):
    sys.stdout.write(str(value) + "\0")

sprint = proj["sprint"]
for it in sprint["configuration"]["iterations"]:
    start = datetime.date.fromisoformat(it["startDate"])
    if start <= today < start + datetime.timedelta(days=it["duration"]):
        emit(sprint["id"])
        emit(it["id"])
        emit(it["title"])
        break
else:
    sys.exit("No Sprint iteration covers " + today.isoformat())

status = proj["status"]
for opt in status["options"]:
    if opt["name"] == "In progress":
        emit(status["id"])
        emit(opt["id"])
        break
else:
    sys.exit("Status option \"In progress\" not found")

emit(proj["start"]["id"])
emit(today.isoformat())
' >"$tmp_dir/fields"

{
  IFS= read -r -d '' SPRINT_FIELD_ID || exit 1
  IFS= read -r -d '' ITERATION_ID || exit 1
  IFS= read -r -d '' ITERATION_TITLE || exit 1
  IFS= read -r -d '' STATUS_FIELD_ID || exit 1
  IFS= read -r -d '' STATUS_OPTION_ID || exit 1
  IFS= read -r -d '' START_FIELD_ID || exit 1
  IFS= read -r -d '' TODAY || exit 1
} <"$tmp_dir/fields"

if ! project_gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$STATUS_FIELD_ID" --single-select-option-id "$STATUS_OPTION_ID" >/dev/null
then
  die "Failed to set Status to In progress."
fi
printf 'Set Status to In progress\n'

if ! project_gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$SPRINT_FIELD_ID" --iteration-id "$ITERATION_ID" >/dev/null
then
  die "Failed to set Sprint."
fi
printf 'Set Sprint to %s\n' "$ITERATION_TITLE"

if ! project_gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$START_FIELD_ID" --date "$TODAY" >/dev/null
then
  die "Failed to set Project Start date."
fi
printf 'Set Project Start date to %s\n' "$TODAY"
