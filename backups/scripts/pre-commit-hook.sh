#!/usr/bin/env bash
# Git pre-commit hook — runs backup validation before allowing commit.
# If validation fails, the commit is blocked.

echo ""
echo "🔒 Running pre-commit backup validation..."
echo ""

REPO_ROOT="$(git rev-parse --show-toplevel)"
"$REPO_ROOT/scripts/validate-backups.sh"

EXIT_CODE=$?
if [ "$EXIT_CODE" -ne 0 ]; then
  echo ""
  echo "🚫 Commit blocked — fix the errors above and try again."
  exit 1
fi
