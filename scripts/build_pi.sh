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
# Core deps that exist on every Debian/Pi OS release.
sudo apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    libcairo2-dev \
    pkg-config

# WebKit2GTK ABI: bookworm ships 4.1, older images have 4.0 only.
# Install whichever is available — pywebview accepts either.
sudo apt-get install -y --no-install-recommends gir1.2-webkit2-4.1 \
    || sudo apt-get install -y --no-install-recommends gir1.2-webkit2-4.0 \
    || { echo "FATAL: neither gir1.2-webkit2-4.1 nor 4.0 available"; exit 1; }

# girepository headers: bookworm uses 1.0, trixie/Ubuntu 24.04 use 2.0.
# Try both — only one needs to succeed.
sudo apt-get install -y --no-install-recommends libgirepository1.0-dev \
    || sudo apt-get install -y --no-install-recommends libgirepository-2.0-dev \
    || { echo "FATAL: neither libgirepository1.0-dev nor 2.0-dev available"; exit 1; }

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
# CRITICAL on Pi: --system-site-packages lets the venv inherit the OS-installed
# python3-gi (GObject introspection bindings). Without it, the venv's Python
# can't `import gi`, PyInstaller skips it, and the resulting binary errors on
# launch with "ModuleNotFoundError: No module named 'gi'".
#
# Always nuke + recreate the venv so we never inherit a previous run's bad
# config (e.g. one created without --system-site-packages from an earlier
# version of this script).
echo "==> [3/5] Creating Python venv at .venv (with --system-site-packages)..."
if [ -d ".venv" ]; then
    # If existing venv lacks gi, rebuild it. Otherwise reuse for speed.
    if ! .venv/bin/python3 -c "import gi" 2>/dev/null; then
        echo "    existing venv cannot import gi — rebuilding..."
        rm -rf .venv
    fi
fi
if [ ! -d ".venv" ]; then
    python3 -m venv --system-site-packages .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip wheel

# Sanity check before we waste time on PyInstaller
if ! python3 -c "import gi; from gi.repository import WebKit2" 2>/dev/null; then
    echo "FATAL: gi.repository.WebKit2 still not importable after venv setup"
    echo "       Check: dpkg -l | grep -E 'python3-gi|webkit2'"
    exit 1
fi
echo "    gi + WebKit2 imports OK in venv"

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

# Install icon to user pixmaps + create .desktop launchers (Apps menu + Desktop)
if [ -n "$BIN_PATH" ]; then
    # Copy the PNG icon to a stable location so the .desktop entry can find it
    mkdir -p "$HOME/.local/share/icons" "$HOME/.local/share/applications"
    cp -f "$REPO_DIR/icons/icon-512.png" "$HOME/.local/share/icons/kidscodeacademy.png"

    DESKTOP_BODY="[Desktop Entry]
Type=Application
Version=1.0
Name=Kids Code Academy
Comment=Sandboxed coding tutorial for ages 7+
Exec=\"$BIN_PATH\"
Icon=$HOME/.local/share/icons/kidscodeacademy.png
Terminal=false
Categories=Education;Game;
StartupNotify=true"

    # 1. Apps menu entry
    LAUNCHER="$HOME/.local/share/applications/kidscodeacademy.desktop"
    printf '%s\n' "$DESKTOP_BODY" > "$LAUNCHER"
    chmod +x "$LAUNCHER" || true
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

    # 2. Desktop double-click launcher (with icon — Pi file manager reads
    #    .desktop files, not raw ELF binary metadata, so the icon shows up here)
    if [ -d "$HOME/Desktop" ]; then
        DESK_LAUNCHER="$HOME/Desktop/Kids Code Academy.desktop"
        printf '%s\n' "$DESKTOP_BODY" > "$DESK_LAUNCHER"
        chmod +x "$DESK_LAUNCHER" || true
        # Pi OS bookworm: marking trusted via gio so it runs on first double-click
        gio set "$DESK_LAUNCHER" "metadata::trusted" true 2>/dev/null || true
        echo "    desktop launcher: $DESK_LAUNCHER (with icon)"
    fi
    echo "    apps menu entry:  $LAUNCHER"
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
