#!/bin/bash

# Define variables
VENV_PATH="/root/webui/stable-diffusion-webui/venv/bin/activate"
BOT_SCRIPT_DIR="/root/webui/my_telegram_bot"
BOT_SCRIPT_PATH="$BOT_SCRIPT_DIR/bot.py"
SYSTEMD_SERVICE_PATH="/etc/systemd/system/ssh.service"

# Create bot.sh script
echo "Creating bot.sh script..."
cat <<EOL > /root/bot.sh
#!/bin/bash

# Activate the virtual environment
source $VENV_PATH

# Navigate to the directory where your bot script is located
cd $BOT_SCRIPT_DIR

# Run the bot script
python bot.py

# Deactivate the virtual environment (optional)
deactivate
EOL

# Make bot.sh executable
chmod +x /root/bot.sh
echo "bot.sh script created and made executable."

# Create systemd service file
echo "Creating systemd service file..."
cat <<EOL > $SYSTEMD_SERVICE_PATH
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
ExecStart=/root/bot.sh
WorkingDirectory=$BOT_SCRIPT_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd daemon to recognize new service
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable and start the systemd service
echo "Enabling and starting ssh.service..."
systemctl enable ssh.service
systemctl start ssh.service

# Check the status of the service
echo "Checking the status of ssh.service..."
systemctl status ssh.service

python3.11 install torch torchvision
bash webui.sh lite
