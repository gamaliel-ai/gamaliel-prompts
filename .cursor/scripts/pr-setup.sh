#!/usr/bin/env bash
# Assigns the current user to a PR, adds it to the Gamaliel Roadmap project,
# and sets the project's Sprint field to whichever iteration covers today.
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

SPRINT_JSON=$(gh api graphql -f owner="$OWNER" -F number="$PROJECT_NUMBER" -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      field(name: "Sprint") {
        ... on ProjectV2IterationField {
          id
          configuration { iterations { id title startDate duration } }
        }
      }
    }
  }
}')

read -r FIELD_ID ITERATION_ID ITERATION_TITLE <<<"$(echo "$SPRINT_JSON" | python3 -c '
import datetime, json, sys
field = json.load(sys.stdin)["data"]["organization"]["projectV2"]["field"]
today = datetime.date.today()
for it in field["configuration"]["iterations"]:
    start = datetime.date.fromisoformat(it["startDate"])
    if start <= today < start + datetime.timedelta(days=it["duration"]):
        print(field["id"], it["id"], it["title"])
        break
else:
    sys.exit("No Sprint iteration covers " + today.isoformat())
')"

gh project item-edit --id "$ITEM_ID" --project-id "$PROJECT_ID" \
  --field-id "$FIELD_ID" --iteration-id "$ITERATION_ID" >/dev/null
echo "Set Sprint to $ITERATION_TITLE"
