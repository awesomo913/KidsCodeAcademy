#!/usr/bin/env bash
# build_pi.sh — one-shot installer + builder for Raspberry Pi.
#
# Usage (paste this into Pi Connect remote shell or a Pi terminal):
#
#   curl -fsSL https://raw.githubusercontent.com/awesomo913/KidsCodeAcademy/main/scripts/build_pi.sh | bash
#
# Or, if the repo is already cloned at ~/KidsCodeAcademy:
#
#   bash ~/KidsCodeAcademy/scripts/build_pi.sh
#
# What it does
# ------------
# 1. Installs system deps (python3, pip, GTK + WebKit2 backend for pywebview)
# 2. Clones (or updates) the repo at ~/KidsCodeAcademy
# 3. Creates a virtualenv at ~/KidsCodeAcademy/.venv
# 4. Installs Python deps (pywebview, pillow, pyinstaller — NO pyttsx3 on Pi;
#    audio is pre-baked + committed)
# 5. Runs `python build.py --target=pi` which produces a single binary at
#    ~/Desktop/KidsCodeAcademy (or ~/KidsCodeAcademy if Desktop missing)
# 6. Optionally creates a .desktop launcher for easier double-click
#
# Safe to re-run: idempotent.

set -euo pipefail

REPO_URL="${KCA_REPO_URL:-https://github.com/awesomo913/KidsCodeAcademy.git}"
REPO_DIR="${KCA_REPO_DIR:-$HOME/KidsCodeAcademy}"
BRANCH="${KCA_BRANCH:-main}"

echo "==> Kids Code Academy — Raspberry Pi build"
echo "    repo:   $REPO_URL"
echo "    target: $REPO_DIR"
echo "    branch: $BRANCH"
echo

# ---------------------------------------------------------------- 1. apt deps
echo "==> [1/5] Installing system packages (sudo apt)..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    gir1.2-webkit2-4.1 \
    libgirepository-2.0-dev \
    libcairo2-dev \
    pkg-config

# Older Pi OS images have webkit2-4.0 instead of 4.1; install the older one as a
# fallback so pywebview can find at least one supported WebKit2GTK ABI.
sudo apt-get install -y --no-install-recommends gir1.2-webkit2-4.0 || true

# --------------------------------------------------------------- 2. clone/pull
echo "==> [2/5] Fetching repo..."
if [ -d "$REPO_DIR/.git" ]; then
    git -C "$REPO_DIR" fetch --depth 1 origin "$BRANCH"
    git -C "$REPO_DIR" reset --hard "origin/$BRANCH"
else
    git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# ----------------------------------------------------------------- 3. venv
echo "==> [3/5] Creating Python venv at .venv..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip wheel

# ---------------------------------------------------------------- 4. py deps
echo "==> [4/5] Installing Python packages (pywebview + pillow + pyinstaller)..."
# pyttsx3 deliberately omitted: TTS is pre-baked on Windows and the wavs ship
# with the repo. Skipping pyttsx3 avoids pulling espeak's robotic voice fallback.
pip install --no-input \
    "pywebview>=5.0" \
    "pillow>=10.0" \
    "pyinstaller>=6.0"

# --------------------------------------------------------------- 5. build
echo "==> [5/5] Building Pi binary..."
python build.py --target=pi --no-audio

BIN_PATH=""
if [ -f "$HOME/Desktop/KidsCodeAcademy" ]; then
    BIN_PATH="$HOME/Desktop/KidsCodeAcademy"
elif [ -f "$HOME/KidsCodeAcademy/dist/KidsCodeAcademy" ]; then
    BIN_PATH="$HOME/KidsCodeAcademy/dist/KidsCodeAcademy"
fi

# Optional .desktop launcher for kid-friendly double-click
if [ -n "$BIN_PATH" ] && [ -d "$HOME/.local/share/applications" ]; then
    LAUNCHER="$HOME/.local/share/applications/kidscodeacademy.desktop"
    cat > "$LAUNCHER" <<EOF
[Desktop Entry]
Type=Application
Name=Kids Code Academy
Comment=Sandboxed coding tutorial for ages 7+
Exec="$BIN_PATH"
Icon=$REPO_DIR/icons/icon-512.png
Terminal=false
Categories=Education;Game;
EOF
    chmod +x "$LAUNCHER" || true
    echo "    desktop launcher: $LAUNCHER"
fi

echo
echo "================================================================"
echo "  ✓ Build complete"
if [ -n "$BIN_PATH" ]; then
    echo "    binary: $BIN_PATH"
    echo "    run:    \"$BIN_PATH\""
else
    echo "    binary: not found at expected location — check $REPO_DIR/dist/"
fi
echo "================================================================"
