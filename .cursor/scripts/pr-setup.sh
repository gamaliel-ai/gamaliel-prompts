#!/usr/bin/env bash
# Assigns the current user to a PR, adds it to the Gamaliel Roadmap project,
# and sets Status to In progress, Sprint to the current iteration, and
# Project Start date to today.
#
# Usage: .cursor/scripts/pr-setup.sh [pr-url-or-number]
#        (defaults to the PR for the current branch)
set -euo pipefail

OWNER="${GAMALIEL_PROJECT_OWNER:-gamaliel-ai}"
PROJECT_NUMBER="${GAMALIEL_PROJECT_NUMBER:-1}"

PR_REF="${1:-}"
if [[ -n "$PR_REF" ]]; then
  PR_URL=$(gh pr view "$PR_REF" --json url -q .url)
else
  PR_URL=$(gh pr view --json url -q .url)
fi

gh pr edit "$PR_URL" --add-assignee @me >/dev/null
echo "Assigned @me to $PR_URL"

PROJECT_ID=$(gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

ITEM_ID=$(gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$PR_URL" --format json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
echo "Added to project $PROJECT_NUMBER as item $ITEM_ID"

FIELDS_JSON=$(gh api graphql -f owner="$OWNER" -F number="$PROJECT_NUMBER" -f query='
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
}')

eval "$(echo "$FIELDS_JSON" | python3 -c '
import datetime, json, sys
proj = json.load(sys.stdin)["data"]["organization"]["projectV2"]
today = datetime.date.today()

sprint = proj["sprint"]
for it in sprint["configuration"]["iterations"]:
    start = datetime.date.fromisoformat(it["startDate"])
    if start <= today < start + datetime.timedelta(days=it["duration"]):
        print("SPRINT_FIELD_ID=" + sprint["id"])
        print("ITERATION_ID=" + it["id"])
        print("ITERATION_TITLE=" + json.dumps(it["title"]))
        break
else:
    sys.exit("No Sprint iteration covers " + today.isoformat())

status = proj["status"]
for opt in status["options"]:
    if opt["name"] == "In progress":
        print("STATUS_FIELD_ID=" + status["id"])
        print("STATUS_OPTION_ID=" + opt["id"])
        break
else:
    sys.exit("Status option \"In progress\" not found")

print("START_FIELD_ID=" + proj["start"]["id"])
print("TODAY=" + today.isoformat())
')"

gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$STATUS_FIELD_ID" --single-select-option-id "$STATUS_OPTION_ID" >/dev/null
echo "Set Status to In progress"

gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$SPRINT_FIELD_ID" --iteration-id "$ITERATION_ID" >/dev/null
echo "Set Sprint to $ITERATION_TITLE"

gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$START_FIELD_ID" --date "$TODAY" >/dev/null
echo "Set Project Start date to $TODAY"
