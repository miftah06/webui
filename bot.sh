#!/bin/bash

# Activate the virtual environment
source /root/webui/stable-diffusion-webui/venv/bin/activate

# Navigate to the directory where your bot script is located
cd bot

# Run the bot script
python3.11 -m pip install -r pip.txt
python3.11 bot.py

# Deactivate the virtual environment (optional)
deactivate
