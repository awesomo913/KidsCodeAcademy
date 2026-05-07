#!/usr/bin/env bash
# setup_remote.sh — install Tailscale SSH + GitHub Actions self-hosted runner.
#
# One-shot bootstrap so I (Claude) can drive this Pi from any future
# conversation. Idempotent: re-run any time. Detects existing installs and
# skips them. Safe.
#
# Usage (paste into the Pi's terminal — no GUI needed):
#
#     curl -fsSL https://raw.githubusercontent.com/awesomo913/KidsCodeAcademy/main/scripts/setup_remote.sh | bash
#
# What it does
# ------------
# 1. Tailscale: installs if missing, runs `tailscale up --ssh` if not connected.
#    User clicks the printed magic auth URL once. Pi gets a stable tailnet IP +
#    DNS name. From any tailnet machine: `ssh pipc@<hostname>` — done.
# 2. GitHub Actions runner: downloads the right linux/arm[64] runner from
#    GitHub releases, configures it for the awesomo913/KidsCodeAcademy repo,
#    installs as a systemd service so it auto-starts on boot.
#
# Re-running the script
# ---------------------
# - Tailscale install: skipped if `command -v tailscale` succeeds.
# - Tailscale auth: skipped if `tailscale status` shows the Pi connected.
# - Runner install: skipped if ~/actions-runner/.runner config exists.
# - Runner service: re-checked + restarted if not active.

set -euo pipefail

# ===== Config =====
REPO_OWNER="awesomo913"
REPO_NAME="KidsCodeAcademy"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"
RUNNER_NAME="${KCA_RUNNER_NAME:-kids-code-academy-pi}"
RUNNER_LABELS="self-hosted,Linux,raspberry-pi,kids-code-academy"
RUNNER_DIR="${HOME}/actions-runner"
TAILSCALE_HOSTNAME="${KCA_TAILSCALE_HOSTNAME:-kids-code-academy-pi}"

echo "==> Kids Code Academy — Pi remote-control bootstrap"
echo "    repo:        ${REPO_URL}"
echo "    runner:      ${RUNNER_NAME}  (${RUNNER_DIR})"
echo "    tailscale:   --ssh hostname=${TAILSCALE_HOSTNAME}"
echo

if [ "$(id -u)" -eq 0 ]; then
    echo "FATAL: do NOT run this as root. Run as the regular Pi user (e.g. pipc)."
    echo "       The script uses sudo only where needed."
    exit 1
fi

# Sanity: user must be able to sudo (tailscale up + svc.sh install need root)
if ! sudo -nv 2>/dev/null && ! sudo -v; then
    echo "FATAL: this user cannot sudo. Need a sudoer for tailscale + runner service."
    exit 1
fi

# ============================================================
# Part 1 — Tailscale
# ============================================================
echo "==> [1/2] Tailscale"

if ! command -v tailscale >/dev/null 2>&1; then
    echo "    installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "    tailscale already installed: $(tailscale version | head -n1)"
fi

# Tailscale daemon must be running before `tailscale up`
sudo systemctl enable --now tailscaled

# Connected check: `tailscale status` returns 0 + non-empty state when up.
if tailscale status --json 2>/dev/null | grep -q '"BackendState": "Running"'; then
    TS_IP="$(tailscale ip -4 2>/dev/null | head -n1 || true)"
    TS_DNS="$(tailscale status --json 2>/dev/null | grep -o '"DNSName": "[^"]*"' | head -n1 | cut -d'"' -f4 || true)"
    echo "    already connected: ${TS_DNS:-?} (${TS_IP:-?})"
else
    echo "    NOT connected — running 'tailscale up --ssh' now."
    echo "    Click the magic URL printed below to authorize this Pi to your tailnet."
    echo
    sudo tailscale up --ssh --hostname="${TAILSCALE_HOSTNAME}" --accept-routes --reset
    TS_IP="$(tailscale ip -4 2>/dev/null | head -n1 || true)"
    TS_DNS="$(tailscale status --json 2>/dev/null | grep -o '"DNSName": "[^"]*"' | head -n1 | cut -d'"' -f4 || true)"
fi

echo
echo "    Tailscale IP:   ${TS_IP:-<not yet assigned>}"
echo "    Tailscale DNS:  ${TS_DNS:-<not yet assigned>}"
echo "    SSH from any tailnet machine:  ssh $(whoami)@${TS_DNS:-${TAILSCALE_HOSTNAME}}"
echo

# ============================================================
# Part 2 — GitHub Actions self-hosted runner
# ============================================================
echo "==> [2/2] GitHub Actions self-hosted runner"

# Pi OS bookworm 32-bit reports `armhf` from dpkg, `armv7l` from uname -m.
# Pi OS 64-bit reports `arm64` / `aarch64`. GitHub publishes both.
DEB_ARCH="$(dpkg --print-architecture 2>/dev/null || echo unknown)"
case "$DEB_ARCH" in
    arm64)  RUNNER_ARCH="arm64" ;;
    armhf)  RUNNER_ARCH="arm"   ;;
    amd64)  RUNNER_ARCH="x64"   ;;
    *)
        echo "FATAL: unsupported architecture ${DEB_ARCH}"
        exit 1
        ;;
esac
echo "    detected arch: ${DEB_ARCH} → runner tarball linux-${RUNNER_ARCH}"

# Pre-existing runner?
if [ -f "${RUNNER_DIR}/.runner" ]; then
    echo "    runner already configured at ${RUNNER_DIR}"
    cd "${RUNNER_DIR}"
    # Make sure service is running
    if sudo ./svc.sh status 2>&1 | grep -q "active (running)"; then
        echo "    service is active — done."
    else
        echo "    service not running — starting..."
        sudo ./svc.sh start || sudo ./svc.sh install "$(whoami)" && sudo ./svc.sh start
    fi
else
    echo "    fresh install — fetching latest runner..."

    # Resolve latest runner version from GitHub's public release JSON
    RUNNER_VERSION="$(curl -fsSL https://api.github.com/repos/actions/runner/releases/latest \
        | grep -o '"tag_name": "v[^"]*"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')"
    if [ -z "${RUNNER_VERSION}" ]; then
        echo "FATAL: could not resolve latest runner version from GitHub API"
        exit 1
    fi
    echo "    latest runner: v${RUNNER_VERSION}"

    mkdir -p "${RUNNER_DIR}"
    cd "${RUNNER_DIR}"

    TARBALL="actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${TARBALL}"
    echo "    downloading ${TARBALL}..."
    curl -fL --retry 3 -o "${TARBALL}" "${DOWNLOAD_URL}"
    tar xzf "${TARBALL}"
    rm -f "${TARBALL}"

    # ----- Get a registration token (1-hour TTL) -----
    REG_TOKEN=""
    if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
        echo "    gh CLI authed — fetching registration token via API..."
        REG_TOKEN="$(gh api -X POST "repos/${REPO_OWNER}/${REPO_NAME}/actions/runners/registration-token" --jq .token 2>/dev/null || true)"
    fi

    if [ -z "${REG_TOKEN}" ]; then
        echo
        echo "    -------- MANUAL STEP REQUIRED --------"
        echo "    1. On any browser, open:"
        echo "         ${REPO_URL}/settings/actions/runners/new"
        echo "    2. Skip the OS picker (we already downloaded the runner)."
        echo "    3. Copy ONLY the long token after './config.sh ... --token'."
        echo "    4. Paste it below + press Enter."
        echo
        read -r -p "    Paste registration token: " REG_TOKEN
        REG_TOKEN="$(echo -n "${REG_TOKEN}" | tr -d '[:space:]')"
        if [ -z "${REG_TOKEN}" ]; then
            echo "FATAL: empty token — aborting."
            exit 1
        fi
    fi

    echo "    configuring runner..."
    ./config.sh \
        --url "${REPO_URL}" \
        --token "${REG_TOKEN}" \
        --name "${RUNNER_NAME}" \
        --labels "${RUNNER_LABELS}" \
        --work "_work" \
        --unattended \
        --replace

    echo "    installing systemd service (runs as $(whoami))..."
    sudo ./svc.sh install "$(whoami)"
    sudo ./svc.sh start
fi

# Verify final state
echo
echo "    ---- runner status ----"
cd "${RUNNER_DIR}"
sudo ./svc.sh status || true
echo

# ============================================================
# Final report
# ============================================================
echo "================================================================"
echo "  ✓ Pi remote channels ready"
echo
echo "  Tailscale SSH (live):"
echo "    ssh $(whoami)@${TS_DNS:-${TAILSCALE_HOSTNAME}}"
echo "    (or via IP: ssh $(whoami)@${TS_IP:-<unknown>})"
echo
echo "  GitHub Actions runner (durable async):"
echo "    Status:  ${REPO_URL}/settings/actions/runners"
echo "    Workflow: ${REPO_URL}/actions/workflows/pi-build.yml"
echo
echo "  From any conversation, dispatch a Pi build with:"
echo "    gh workflow run pi-build.yml --ref main"
echo "    gh run watch    # follow live"
echo "    gh run view <id> --log    # diagnostic"
echo "================================================================"
