#!/bin/bash
# Git commit helper - non-interactive
# Usage: ./scripts/git-commit.sh "commit message" [files...]

set -e

MESSAGE="$1"
shift

if [ $# -eq 0 ]; then
    git add -A
else
    git add "$@"
fi

git commit -m "$MESSAGE" --no-verify --no-gpg-sign
git push origin main --no-verify

echo "✅ Committed and pushed: $MESSAGE"
exit 0
