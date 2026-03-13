#!/bin/bash
set -euo pipefail

# ─── 1. System packages ───
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git nginx certbot python3-certbot-nginx sqlite3 curl

# ─── 2. Node.js 22 (for OpenClaw) ───
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt install -y nodejs
node --version  # should be 22.x

# ─── 3. Python 3.12 ───
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
python3.12 --version

# ─── 4. OpenClaw ───
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
# Follow prompts: set Anthropic API key, configure Telegram

# ─── 5. Application ───
sudo mkdir -p /opt/transformation-coach
sudo chown $USER:$USER /opt/transformation-coach
cd /opt/transformation-coach
git clone <your-repo-url> .

# Python venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create data directories
mkdir -p data memory credentials

# Copy env file and edit
cp .env.example .env
nano .env  # Fill in API keys, Telegram token, Sheets ID

# ─── 6. Build React dashboard ───
cd dashboard
npm ci
npm run build
cd ..

# ─── 7. Systemd service for Python backend ───
sudo tee /etc/systemd/system/coach-api.service > /dev/null <<'EOF'
[Unit]
Description=Transformation Coach FastAPI
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/opt/transformation-coach
Environment="PATH=/opt/transformation-coach/.venv/bin:/usr/bin"
EnvironmentFile=/opt/transformation-coach/.env
ExecStart=/opt/transformation-coach/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable coach-api
sudo systemctl start coach-api

# ─── 8. Nginx reverse proxy ───
sudo tee /etc/nginx/sites-available/coach > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    # React dashboard + API
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/coach /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ─── 9. SQLite daily backup cron ───
mkdir -p /opt/transformation-coach/backups
(crontab -l 2>/dev/null; echo "0 3 * * * sqlite3 /opt/transformation-coach/data/transformation.db '.backup /opt/transformation-coach/backups/coach-\$(date +\%Y\%m\%d).db'") | crontab -
# Keep only last 14 backups
(crontab -l 2>/dev/null; echo "0 4 * * * find /opt/transformation-coach/backups -name '*.db' -mtime +14 -delete") | crontab -

echo "Setup complete!"
echo "Dashboard: http://$(curl -s ifconfig.me)"
echo "OpenClaw Control UI: http://localhost:18789 (internal only)"
