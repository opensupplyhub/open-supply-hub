#!/bin/bash -x

# Specify the base branch (e.g., main)
BASE_BRANCH="main"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check if this is a release branch (releases/*)
if [[ "$CURRENT_BRANCH" != releases/* ]]; then
    echo "Branch $CURRENT_BRANCH is not a release branch. No check required."
    echo "skip=false" >> "$GITHUB_OUTPUT"
    exit 0
fi

# Ensure the local BASE_BRANCH exists
if ! git show-ref --verify --quiet "refs/heads/$BASE_BRANCH"; then
    echo "Fetching $BASE_BRANCH from origin..."
    git fetch origin "$BASE_BRANCH:$BASE_BRANCH"
fi

# Find the branch-off point
MERGE_BASE=$(git merge-base "$CURRENT_BRANCH" "$BASE_BRANCH")

if [[ -z "$MERGE_BASE" ]]; then
    echo "❌ Failed to find the divergence point with $BASE_BRANCH"
    echo "skip=false" >> "$GITHUB_OUTPUT"
    exit 1
fi

# Count commits after the branch-off point
COMMIT_COUNT=$(git rev-list --count "$CURRENT_BRANCH" ^"$MERGE_BASE")

if [ "$COMMIT_COUNT" -eq 0 ]; then
    echo "The branch does not contain any new commits yet"
    echo "skip=true" >> "$GITHUB_OUTPUT"
else
    echo "The branch contains new commits"
    echo "skip=false" >> "$GITHUB_OUTPUT"
fi
