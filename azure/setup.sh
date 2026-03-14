#!/bin/bash
# =============================================================================
# Transformation Coach — Azure VM Setup Script
# Target: Ubuntu 24.04 LTS, B1s (1 vCPU, 1 GB RAM), azureuser
#
# BEFORE RUNNING THIS SCRIPT — scp these 4 files to the VM:
#
#   scp .env azureuser@<VM_IP>:/opt/transformation-coach/.env
#   scp data/transformation.db azureuser@<VM_IP>:/opt/transformation-coach/data/transformation.db
#   scp credentials/google-service-account.json azureuser@<VM_IP>:/opt/transformation-coach/credentials/google-service-account.json
#   scp memory/memory.md azureuser@<VM_IP>:/opt/transformation-coach/memory/memory.md
#
# Then SSH in and run:
#   chmod +x setup.sh && ./setup.sh
# =============================================================================

set -euo pipefail

# ─── Variables ────────────────────────────────────────────────────────────────
REPO_URL="https://github.com/AshiishKarhade/nouri-personal-ai.git"
APP_DIR="/opt/transformation-coach"
APP_USER="ashiishk"
VENV="${APP_DIR}/.venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Colors ───────────────────────────────────────────────────────────────────
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BOLD="\033[1m"
RESET="\033[0m"

# ─── Helpers ──────────────────────────────────────────────────────────────────
print_step() {
    echo -e "\n${YELLOW}${BOLD}==> $1${RESET}"
}

print_ok() {
    echo -e "${GREEN}    [OK] $1${RESET}"
}

print_error() {
    echo -e "${RED}    [ERROR] $1${RESET}"
    exit 1
}

print_info() {
    echo -e "${CYAN}    [INFO] $1${RESET}"
}

print_banner() {
    echo -e "${BOLD}${CYAN}"
    echo "============================================================"
    echo "  Transformation Coach — Azure VM Deployment"
    echo "============================================================"
    echo -e "${RESET}"
}

print_box() {
    local title="$1"
    shift
    echo -e "\n${BOLD}${GREEN}"
    echo "┌─────────────────────────────────────────────────────────────┐"
    printf "│  %-59s │\n" "$title"
    echo "├─────────────────────────────────────────────────────────────┤"
    for line in "$@"; do
        printf "│  %-59s │\n" "$line"
    done
    echo "└─────────────────────────────────────────────────────────────┘"
    echo -e "${RESET}"
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. PREFLIGHT CHECKS
# ─────────────────────────────────────────────────────────────────────────────
preflight() {
    print_step "1/15  Preflight checks"

    # Must not run as root
    if [[ "$EUID" -eq 0 ]]; then
        print_error "Run this script as ${APP_USER}, not root. (sudo is invoked internally where needed)"
    fi

    # Must be azureuser
    if [[ "$(whoami)" != "${APP_USER}" ]]; then
        print_error "Script must be run as '${APP_USER}', currently '$(whoami)'"
    fi
    print_ok "Running as ${APP_USER}"

    # Required files that must be scp'd before this script runs
    local required_files=(
        "${APP_DIR}/.env"
        "${APP_DIR}/data/transformation.db"
        "${APP_DIR}/credentials/google-service-account.json"
        "${APP_DIR}/memory/memory.md"
    )

    # Create parent dirs if not present so the checks give clean messages
    sudo mkdir -p "${APP_DIR}/data" "${APP_DIR}/credentials" "${APP_DIR}/memory"
    sudo chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

    local missing=0
    for f in "${required_files[@]}"; do
        if [[ ! -f "$f" ]]; then
            echo -e "${RED}    [MISSING] $f${RESET}"
            missing=1
        else
            print_ok "Found: $f"
        fi
    done

    if [[ "$missing" -eq 1 ]]; then
        echo ""
        echo -e "${RED}${BOLD}Missing required files. SCP them to the VM before continuing:${RESET}"
        echo ""
        echo "  scp .env                             ${APP_USER}@<VM_IP>:${APP_DIR}/.env"
        echo "  scp data/transformation.db           ${APP_USER}@<VM_IP>:${APP_DIR}/data/transformation.db"
        echo "  scp credentials/google-service-account.json \\"
        echo "                                       ${APP_USER}@<VM_IP>:${APP_DIR}/credentials/google-service-account.json"
        echo "  scp memory/memory.md                 ${APP_USER}@<VM_IP>:${APP_DIR}/memory/memory.md"
        exit 1
    fi

    # Source .env so we can use the values throughout the script
    set -a
    # shellcheck disable=SC1090
    source "${APP_DIR}/.env"
    set +a

    # Validate critical env vars are not placeholder values
    local required_vars=("TELEGRAM_BOT_TOKEN" "TELEGRAM_CHAT_ID" "ANTHROPIC_API_KEY")
    for var in "${required_vars[@]}"; do
        local val="${!var:-}"
        if [[ -z "$val" || "$val" == "REPLACE_ME" || "$val" == "sk-ant-api03-REPLACE_ME" ]]; then
            print_error "${var} is not set or still a placeholder in ${APP_DIR}/.env"
        fi
    done
    print_ok "All required env vars are set"

    # TELEGRAM_USER_ID falls back to TELEGRAM_CHAT_ID when not explicitly set
    TELEGRAM_USER_ID="${TELEGRAM_USER_ID:-${TELEGRAM_CHAT_ID}}"
    export TELEGRAM_USER_ID

    print_ok "Preflight passed"
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. SWAP FILE — critical on 1 GB RAM during npm/pip installs
# ─────────────────────────────────────────────────────────────────────────────
setup_swap() {
    print_step "2/15  Swap file (1 GB)"

    if swapon --show | grep -q '/swapfile'; then
        print_ok "Swap already active at /swapfile — skipping"
        return
    fi

    if [[ -f /swapfile ]]; then
        print_info "/swapfile exists but is not active — activating"
    else
        sudo fallocate -l 1G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
    fi

    sudo swapon /swapfile

    # Persist across reboots
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
    fi

    # Tune swappiness for a mostly-RAM workload
    sudo sysctl -w vm.swappiness=10 > /dev/null
    if ! grep -q 'vm.swappiness' /etc/sysctl.conf; then
        echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf > /dev/null
    fi

    print_ok "1 GB swap active at /swapfile"
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. SYSTEM PACKAGES
# ─────────────────────────────────────────────────────────────────────────────
install_system_packages() {
    print_step "3/15  System packages"

    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update -q
    sudo apt-get upgrade -y -q

    sudo apt-get install -y -q \
        build-essential \
        git \
        curl \
        sqlite3 \
        nginx \
        certbot \
        python3-certbot-nginx \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3-pip \
        ufw \
        fail2ban

    print_ok "System packages installed"
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. UFW FIREWALL
# ─────────────────────────────────────────────────────────────────────────────
configure_firewall() {
    print_step "4/15  UFW firewall"

    sudo ufw --force reset > /dev/null
    sudo ufw default deny incoming > /dev/null
    sudo ufw default allow outgoing > /dev/null

    sudo ufw allow 22/tcp comment 'SSH'
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'

    # Port 18789 (OpenClaw UI) is NOT opened publicly.
    # Access it via SSH tunnel:  ssh -L 18789:localhost:18789 azureuser@<VM_IP>
    print_info "Port 18789 (OpenClaw UI) is loopback-only. Use SSH tunnel to access it."

    sudo ufw --force enable > /dev/null

    print_ok "UFW enabled: 22, 80, 443 open. 18789 internal only."
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. NODE.JS 22
# ─────────────────────────────────────────────────────────────────────────────
install_nodejs() {
    print_step "5/15  Node.js 22"

    if node --version 2>/dev/null | grep -q '^v22'; then
        print_ok "Node.js 22 already installed: $(node --version)"
        return
    fi

    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - > /dev/null 2>&1
    sudo apt-get install -y -q nodejs
    print_ok "Node.js installed: $(node --version)  npm: $(npm --version)"
}

# ─────────────────────────────────────────────────────────────────────────────
# 6. OPENCLAW INSTALL + CONFIG
# ─────────────────────────────────────────────────────────────────────────────
install_openclaw() {
    print_step "6/15  OpenClaw install + configuration"

    # Install via npm global (falls back to install.sh if npm install fails)
    if ! command -v openclaw &>/dev/null; then
        print_info "Installing OpenClaw via npm..."
        if ! npm install -g openclaw 2>/dev/null; then
            print_info "npm install failed, trying official install.sh..."
            curl -fsSL https://openclaw.ai/install.sh | bash
        fi
    fi

    # Ensure openclaw is on PATH for the current session
    export PATH="${HOME}/.local/bin:${HOME}/.openclaw/bin:${PATH}"

    if ! command -v openclaw &>/dev/null; then
        print_error "openclaw binary not found after install. Check PATH."
    fi
    print_ok "OpenClaw installed: $(openclaw --version 2>/dev/null || echo 'version unknown')"

    # Write openclaw.json
    print_info "Writing ~/.openclaw/openclaw.json..."
    mkdir -p "${HOME}/.openclaw"

    # TELEGRAM_USER_ID is set in preflight (falls back to TELEGRAM_CHAT_ID)
    cat > "${HOME}/.openclaw/openclaw.json" <<EOF
{
  "meta": {
    "lastTouchedVersion": "2026.3.13"
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai-codex/gpt-5.3-codex"
      },
      "workspace": "${APP_DIR}/openclaw"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "${TELEGRAM_BOT_TOKEN}",
      "dmPolicy": "allowlist",
      "allowFrom": ["${TELEGRAM_USER_ID}"],
      "streaming": "partial"
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token"
    }
  },
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true
      }
    }
  }
}
EOF
    print_ok "~/.openclaw/openclaw.json written"

    # Skip onboard (heavy interactive wizard — OOMs on small VMs).
    # Config is already written above. Just install the systemd service and start.
    print_info "Installing OpenClaw gateway as systemd user service..."
    NODE_OPTIONS="--max-old-space-size=400" openclaw gateway install

    print_info "Starting OpenClaw gateway..."
    NODE_OPTIONS="--max-old-space-size=400" openclaw gateway start || \
        print_info "Gateway start returned non-zero (may already be running)"

    print_ok "OpenClaw setup done"
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. APP DIRECTORY — clone or pull
# ─────────────────────────────────────────────────────────────────────────────
setup_app_directory() {
    print_step "7/15  Application directory"

    sudo mkdir -p "${APP_DIR}"
    sudo chown "${APP_USER}:${APP_USER}" "${APP_DIR}"

    if [[ -d "${APP_DIR}/.git" ]]; then
        print_info "Repo already cloned — pulling latest"
        git -C "${APP_DIR}" pull --ff-only
    else
        print_info "Cloning repo from ${REPO_URL}..."
        # Clone into a temp location then move, so we don't destroy the scp'd files
        local tmp_clone
        tmp_clone="$(mktemp -d)"
        git clone "${REPO_URL}" "${tmp_clone}"

        # Copy repo files into APP_DIR, skipping files that already exist (scp'd data)
        rsync -a --ignore-existing "${tmp_clone}/" "${APP_DIR}/"
        rm -rf "${tmp_clone}"
    fi

    # Ensure required data directories exist
    mkdir -p \
        "${APP_DIR}/data" \
        "${APP_DIR}/credentials" \
        "${APP_DIR}/memory" \
        "${APP_DIR}/backups" \
        "${APP_DIR}/openclaw/skills"

    print_ok "App directory ready at ${APP_DIR}"
}

# ─────────────────────────────────────────────────────────────────────────────
# 8. PYTHON VENV + DEPENDENCIES
# ─────────────────────────────────────────────────────────────────────────────
setup_python_venv() {
    print_step "8/15  Python 3.12 venv + dependencies"

    if [[ ! -d "${VENV}" ]]; then
        python3.12 -m venv "${VENV}"
        print_ok "Venv created at ${VENV}"
    else
        print_info "Venv already exists — updating packages"
    fi

    "${VENV}/bin/pip" install --quiet --upgrade pip
    "${VENV}/bin/pip" install --quiet -r "${APP_DIR}/requirements.txt"

    print_ok "Python dependencies installed"
}

# ─────────────────────────────────────────────────────────────────────────────
# 9. REACT DASHBOARD BUILD
# ─────────────────────────────────────────────────────────────────────────────
build_dashboard() {
    print_step "9/15  React dashboard build"

    if [[ ! -d "${APP_DIR}/dashboard" ]]; then
        print_info "No dashboard/ directory found — skipping frontend build"
        return
    fi

    cd "${APP_DIR}/dashboard"
    npm ci --prefer-offline
    npm run build
    cd "${APP_DIR}"

    print_ok "Dashboard built successfully"
}

# ─────────────────────────────────────────────────────────────────────────────
# 10. COACH-API SYSTEMD SERVICE
# ─────────────────────────────────────────────────────────────────────────────
install_systemd_service() {
    print_step "10/15  Systemd service (coach-api)"

    # Write the service file directly — including the extended PATH so that
    # APScheduler can call 'openclaw message send' from cron/scheduler jobs.
    sudo tee /etc/systemd/system/coach-api.service > /dev/null <<EOF
[Unit]
Description=Transformation Coach API
After=network.target
Documentation=https://github.com/YOUR_USERNAME/YOUR_REPO

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV}/bin:/home/${APP_USER}/.local/bin:/home/${APP_USER}/.openclaw/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV}/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=coach-api

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable coach-api
    sudo systemctl restart coach-api

    print_info "Waiting for service to come up..."
    sleep 3

    if systemctl is-active --quiet coach-api; then
        print_ok "coach-api.service is active"
    else
        echo -e "${RED}    [WARN] coach-api.service did not start cleanly. Check: journalctl -u coach-api -n 50${RESET}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# 11. NGINX REVERSE PROXY
# ─────────────────────────────────────────────────────────────────────────────
configure_nginx() {
    print_step "11/15  Nginx reverse proxy"

    sudo tee /etc/nginx/sites-available/coach > /dev/null <<'NGINXEOF'
server {
    listen 80;
    server_name _;

    # Increase body size for food photo uploads (up to 20 MB)
    client_max_body_size 20M;

    # React dashboard + FastAPI
    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # OpenClaw Control UI — loopback only, never exposed publicly.
    # To access: ssh -L 18789:localhost:18789 azureuser@<VM_IP>
    # then open http://localhost:18789 in your browser.
    # This block is intentionally absent from the public nginx config.
}
NGINXEOF

    sudo ln -sf /etc/nginx/sites-available/coach /etc/nginx/sites-enabled/coach
    sudo rm -f /etc/nginx/sites-enabled/default

    sudo nginx -t
    sudo systemctl reload nginx

    print_ok "Nginx configured and reloaded"
}

# ─────────────────────────────────────────────────────────────────────────────
# 12. SQLITE BACKUP CRON
# ─────────────────────────────────────────────────────────────────────────────
setup_backup_cron() {
    print_step "12/15  SQLite backup cron"

    mkdir -p "${APP_DIR}/backups"

    # Remove any stale backup cron entries for this app before re-adding
    local tmpfile
    tmpfile="$(mktemp)"
    crontab -l 2>/dev/null | grep -v 'transformation-coach backup' > "${tmpfile}" || true

    # 21:30 UTC = 03:00 IST — daily backup
    echo "30 21 * * *  sqlite3 ${APP_DIR}/data/transformation.db \".backup ${APP_DIR}/backups/coach-\$(date +\%Y\%m\%d).db\" # transformation-coach backup" >> "${tmpfile}"

    # Prune backups older than 14 days (runs 22:00 UTC, after backup completes)
    echo "0 22 * * *   find ${APP_DIR}/backups -name '*.db' -mtime +14 -delete # transformation-coach backup" >> "${tmpfile}"

    crontab "${tmpfile}"
    rm -f "${tmpfile}"

    print_ok "Backup cron set: daily at 21:30 UTC (03:00 IST). Pruning >14 days at 22:00 UTC."
}

# ─────────────────────────────────────────────────────────────────────────────
# 13. OPENCLAW WORKSPACE VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
verify_openclaw_workspace() {
    print_step "13/15  OpenClaw workspace verification"

    local skills_dir="${APP_DIR}/openclaw/skills"

    if [[ -d "${skills_dir}" ]]; then
        local skill_count
        skill_count=$(find "${skills_dir}" -name 'SKILL.md' | wc -l)
        print_ok "OpenClaw skills directory found: ${skills_dir}"
        print_ok "Skill files found: ${skill_count}"
        if [[ "$skill_count" -gt 0 ]]; then
            find "${skills_dir}" -name 'SKILL.md' | while read -r sf; do
                print_info "  Skill: ${sf#${skills_dir}/}"
            done
        fi
    else
        echo -e "${YELLOW}    [WARN] ${skills_dir} not found.${RESET}"
        echo -e "${YELLOW}           Create it from the repo or copy manually.${RESET}"
        mkdir -p "${skills_dir}"
    fi

    local agents_file="${APP_DIR}/openclaw/AGENTS.md"
    if [[ -f "${agents_file}" ]]; then
        print_ok "AGENTS.md found at ${agents_file}"
    else
        echo -e "${YELLOW}    [WARN] AGENTS.md not found at ${agents_file}${RESET}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# 14. HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────
run_health_checks() {
    print_step "14/15  Health checks"

    local all_ok=1

    # FastAPI direct
    print_info "Checking FastAPI /health (direct port 8000)..."
    if curl -sf --max-time 5 http://127.0.0.1:8000/health > /dev/null 2>&1; then
        print_ok "FastAPI /health: OK"
    else
        echo -e "${RED}    [FAIL] FastAPI /health did not respond. Check: journalctl -u coach-api -n 30${RESET}"
        all_ok=0
    fi

    # FastAPI through Nginx
    print_info "Checking FastAPI /health through Nginx (port 80)..."
    if curl -sf --max-time 5 http://127.0.0.1:80/health > /dev/null 2>&1; then
        print_ok "Nginx proxy /health: OK"
    else
        echo -e "${RED}    [FAIL] Nginx proxy /health did not respond. Check: nginx -t && systemctl status nginx${RESET}"
        all_ok=0
    fi

    # OpenClaw gateway status
    print_info "Checking OpenClaw gateway status..."
    if openclaw gateway status 2>/dev/null | grep -qi 'running'; then
        print_ok "OpenClaw gateway: running"
    else
        echo -e "${YELLOW}    [WARN] OpenClaw gateway status unclear. Run: openclaw gateway status${RESET}"
    fi

    # systemd service
    print_info "Checking coach-api.service..."
    if systemctl is-active --quiet coach-api; then
        print_ok "coach-api.service: active"
    else
        echo -e "${RED}    [FAIL] coach-api.service is not active${RESET}"
        all_ok=0
    fi

    if [[ "$all_ok" -eq 1 ]]; then
        print_ok "All health checks passed"
    else
        echo -e "${YELLOW}    [WARN] Some checks failed — review output above${RESET}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# 15. FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print_summary() {
    print_step "15/15  Deployment summary"

    local public_ip
    public_ip=$(curl -sf --max-time 5 https://ifconfig.me 2>/dev/null || \
                curl -sf --max-time 5 https://api.ipify.org 2>/dev/null || \
                echo "<VM_PUBLIC_IP>")

    print_box "Transformation Coach is deployed!" \
        "" \
        "Dashboard:       http://${public_ip}/" \
        "API docs:        http://${public_ip}/docs" \
        "API redoc:       http://${public_ip}/redoc" \
        "" \
        "OpenClaw UI (SSH tunnel required):" \
        "  ssh -L 18789:localhost:18789 ${APP_USER}@${public_ip}" \
        "  then open: http://localhost:18789" \
        "" \
        "Logs:" \
        "  journalctl -u coach-api -f" \
        "  openclaw gateway logs" \
        "" \
        "Manual backup:" \
        "  sqlite3 ${APP_DIR}/data/transformation.db \".backup ${APP_DIR}/backups/manual-\$(date +%Y%m%d).db\""

    echo -e "${CYAN}Tip: Assign a domain and run 'sudo certbot --nginx' for HTTPS.${RESET}"
    echo ""
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
main() {
    print_banner

    echo -e "${BOLD}Before this script runs, the following files must already be on the VM:${RESET}"
    echo ""
    echo "  ${APP_DIR}/.env"
    echo "  ${APP_DIR}/data/transformation.db"
    echo "  ${APP_DIR}/credentials/google-service-account.json"
    echo "  ${APP_DIR}/memory/memory.md"
    echo ""
    echo -e "${YELLOW}If any are missing, the script will exit with instructions.${RESET}"
    echo ""
    echo -e "${BOLD}Continuing in 5 seconds — Ctrl+C to abort...${RESET}"
    sleep 5

    preflight
    setup_swap
    install_system_packages
    configure_firewall
    install_nodejs
    install_openclaw
    setup_app_directory
    setup_python_venv
    build_dashboard
    install_systemd_service
    configure_nginx
    setup_backup_cron
    verify_openclaw_workspace
    run_health_checks
    print_summary
}

main "$@"
