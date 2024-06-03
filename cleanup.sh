#!/bin/bash
#!/bin/bash

# Hapus cache pip
echo "Menghapus cache pip..."
pip3 cache purge

# Hapus __pycache__ directories
echo "Menghapus direktori __pycache__..."
find . -type d -name "__pycache__" -exec rm -r {} +

# Hapus file .pyc dan .pyo
echo "Menghapus file .pyc dan .pyo..."
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Hapus file log yang tidak diinginkan
echo "Menghapus file log yang tidak diinginkan..."
find . -type f -name "*.log" -delete

# Konfirmasi selesai
echo "Pembersihan cache dan file sampah Python selesai."

# Fungsi untuk membersihkan cache APT
clean_apt_cache() {
    echo "Cleaning APT cache..."
    sudo apt-get clean
}

# Fungsi untuk menghapus paket-paket yang tidak diperlukan
autoremove_packages() {
    echo "Removing unnecessary packages..."
    sudo apt-get autoremove -y
}

# Fungsi untuk menghapus file konfigurasi yang tidak digunakan
purge_configs() {
    echo "Purging removed package configuration files..."
    sudo apt-get purge -y
}

# Fungsi untuk menghapus log lama
clean_old_logs() {
    echo "Removing old journal logs..."
    sudo journalctl --vacuum-time=2weeks
}

# Fungsi untuk menghapus cache pengguna
clean_user_cache() {
    echo "Removing user cache..."
    rm -rf ~/.cache/*
}

# Fungsi untuk membersihkan swap space
clean_swap() {
    echo "Cleaning swap space..."
    sudo swapoff -a
    sudo swapon -a
}

# Fungsi untuk membersihkan sistem secara keseluruhan
clean_system() {
    clean_apt_cache
    autoremove_packages
    purge_configs
    clean_old_logs
    clean_user_cache
    clean_swap
}

# Fungsi utama untuk menjalankan skrip pembersihan
main() {
    echo "Starting system cleanup..."
    clean_system
    echo "System cleanup complete."
}

# Menampilkan pilihan kepada pengguna
echo "Pilih opsi:"
echo "1. Terapan: Jalankan pembersihan sistem"
echo "2. None: Tidak melakukan apapun"
read -p "Masukkan pilihan Anda (1 atau 2): " choice

case $choice in
    1)
        main
        ;;
    2)
        echo "Tidak ada tindakan yang dilakukan."
        ;;
    *)
        echo "Pilihan tidak valid. Silakan coba lagi."
        ;;
esac
