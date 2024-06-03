#!/bin/bash

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y git python3.8 python3.8-venv

# Clone the stable-diffusion-webui repository
if [ ! -d "stable-diffusion-webui" ]; then
  git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
fi
cd stable-diffusion-webui

# Create a Python virtual environment using Python 3.8
if [ ! -d "venv" ]; then
  python3.8 -m venv venv
fi
source venv/bin/activate

# Install necessary Python packages
pip3 install --upgrade pip

# Create API key and write it to a file if it doesn't exist
if [ ! -f .env ]; then
  API_KEY=$(openssl rand -hex 16)
  echo "API_KEY=$API_KEY" > .env
fi

# Set the necessary environment variables
export COMMANDLINE_ARGS="--allow-code --no-half-vae --api --port 1024 --lowvram --precision full --no-half --skip-torch-cuda-test --share --xformers"
export PUBLIC_URL=""
export LITE_MODE=""

# Function to start the web UI
start_webui() {
  if [ -n "$PUBLIC_URL" ]; then
    COMMANDLINE_ARGS="$COMMANDLINE_ARGS --listen"
  fi
  if [ -n "$LITE_MODE" ]; then
    COMMANDLINE_ARGS="$COMMANDLINE_ARGS --no-half --no-progress-bar --skip-torch-cuda-test"
  fi
  nohup python3.8 launch.py $COMMANDLINE_ARGS > webui.log 2>&1 &
  echo $! > webui.pid
}

# Function to stop the web UI
stop_webui() {
  if [ -f webui.pid ]; then
    kill $(cat webui.pid)
    rm webui.pid
  else
    echo "Web UI is not running."
  fi
}

# Function to restart the web UI
restart_webui() {
  stop_webui
  start_webui
}

# Check and create necessary swap space if less than 4GB of RAM
check_and_create_swap() {
  if [ $(free -m | awk '/^Mem:/{print $2}') -lt 4000 ]; then
    if ! sudo swapon --show | grep -q 'swapfile'; then
      sudo fallocate -l 1G /swapfile
      sudo chmod 600 /swapfile
      sudo mkswap /swapfile
      sudo swapon /swapfile
      if [ $? -ne 0 ]; then
        echo "Failed to enable swap. Please check your system settings."
        exit 1
      fi
      echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi
  fi
}

# Simplified options using OR functionality
case "$1" in
  start|START)
    check_and_create_swap
    start_webui
    ;;
  stop|STOP)
    stop_webui
    echo "Web UI stopped."
    ;;
  restart|RESTART)
    check_and_create_swap
    restart_webui
    echo "Web UI restarted."
    ;;
  public|PUBLIC)
    PUBLIC_URL="1"
    check_and_create_swap
    start_webui
    ;;
  lite|LITE)
    LITE_MODE="1"
    check_and_create_swap
    start_webui
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|public|lite}"
    ;;
esac
