#!/usr/bin/env bash
# Installs the `x-search` wrapper onto the bun PATH so the CLI runs from any cwd.
# Idempotent — safe to re-run. Run this after a host rebuild if `which x-search`
# comes up empty.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUN_BIN="/home/claw/.bun/bin"
WRAPPER="${BUN_BIN}/x-search"

if [ ! -x "${BUN_BIN}/bun" ]; then
  echo "error: bun not found at ${BUN_BIN}/bun" >&2
  exit 1
fi

cat > "${WRAPPER}" <<EOF
#!/usr/bin/env bash
# Wrapper so the x-research CLI runs from any working directory.
# The script itself is cwd-independent (resolves .env/cache/watchlist via
# import.meta.dir); only the invocation needed a stable path.
exec ${BUN_BIN}/bun run ${SKILL_DIR}/x-search.ts "\$@"
EOF
chmod +x "${WRAPPER}"

echo "installed: ${WRAPPER} -> ${SKILL_DIR}/x-search.ts"
