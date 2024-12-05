#!/bin/bash

# Skrip ini memasang layanan systemd untuk menjalankan server Python,
# memforward port 80 ke 899, dan memastikan layanan tetap hidup.

SERVICE_NAME="python-fw.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

# Langkah 1: Periksa izin root
if [ "$(id -u)" -ne 0 ]; then
    echo "Skrip ini harus dijalankan sebagai root. Gunakan 'sudo' untuk menjalankannya."
    exit 1
fi

echo "1. Membuat file unit systemd untuk layanan..."

# Langkah 2: Membuat konfigurasi layanan systemd
cat <<EOF > $SERVICE_PATH
[Unit]
Description=Python HTTP Server with Port Forwarding
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'fuser -k 80/tcp || true && \
  mkdir -p /tmp/python_server && \
  echo "<h1>Server Python Aktif</h1>" > /tmp/python_server/index.html && \
  python3 -m http.server 899 --directory /tmp/python_server & \
  iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 899'
ExecStop=/bin/bash -c 'fuser -k 899/tcp || true && \
  iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 899'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "File unit layanan berhasil dibuat di $SERVICE_PATH."

# Langkah 3: Reload systemd untuk mengenali layanan baru
echo "2. Reload systemd dan mengaktifkan layanan..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Langkah 4: Memulai layanan
echo "3. Memulai layanan..."
systemctl start $SERVICE_NAME

echo "Layanan telah diaktifkan. Anda dapat memeriksa status dengan 'systemctl status $SERVICE_NAME'."
echo "Jika Anda ingin menghentikan layanan, gunakan 'sudo systemctl stop $SERVICE_NAME'."
echo "Untuk menghapus layanan, gunakan 'sudo systemctl disable $SERVICE_NAME' dan hapus file di $SERVICE_PATH."
