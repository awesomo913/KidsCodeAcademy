#!/bin/bash
# Install repo-local git hooks.
#
# Run once per fresh clone:
#   bash scripts/install_hooks.sh
#
# Currently installs:
#   * pre-commit  -> scripts/check_no_wav_commit.sh   (blocks wav re-track + >50MB files)
#
# Idempotent: safe to re-run. Overwrites existing hooks of the same name.

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$ROOT/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "ERROR: $HOOKS_DIR does not exist — are you in a git repo?" >&2
    exit 1
fi

mkdir -p "$HOOKS_DIR"

# pre-commit hook: shells out to scripts/check_no_wav_commit.sh
cat > "$HOOKS_DIR/pre-commit" <<'EOF'
#!/bin/bash
# Auto-installed by scripts/install_hooks.sh — DO NOT edit by hand.
# Edit scripts/check_no_wav_commit.sh instead.
set -e
ROOT="$(git rev-parse --show-toplevel)"
exec bash "$ROOT/scripts/check_no_wav_commit.sh"
EOF
chmod +x "$HOOKS_DIR/pre-commit"

echo "OK installed pre-commit hook at $HOOKS_DIR/pre-commit"
echo "    -> guards against assets/audio/*.wav re-track + >50MB single-file commits"
