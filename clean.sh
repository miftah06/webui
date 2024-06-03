#!/bin/bash -eux

# Make sure Udev doesn't block our network
echo "Cleaning up udev rules"
rm -rf /dev/.udev/
# Better fix that persists package updates
# This may not be necessary for all distributions
# touch /etc/udev/rules.d/75-persistent-net-generator.rules

echo "Cleaning up leftover dhcp leases"
if [ -d "/var/lib/dhcp" ]; then
    rm -f /var/lib/dhcp/*
fi

echo "Cleaning up tmp"
rm -rf /tmp/*

# Cleanup apt cache
echo "Cleaning up apt cache"
if command -v apt-get &>/dev/null; then
    apt-get -y autoremove --purge
    apt-get -y clean
    apt-get -y autoclean
elif command -v yum &>/dev/null; then
    yum -y clean all
elif command -v dnf &>/dev/null; then
    dnf -y clean all
elif command -v zypper &>/dev/null; then
    zypper --non-interactive clean --all
fi

echo "Cleaning up snap packages"
# Snap cleanup may not be relevant for all distributions
# snap set system refresh.retain=2 # Keep last 2 revisions
# snap refresh
# snap set system refresh.retain=

echo "Installed packages:"
if command -v dpkg &>/dev/null; then
    dpkg --get-selections | grep -v deinstall
elif command -v rpm &>/dev/null; then
    rpm -qa
fi

DISK_USAGE_BEFORE_CLEANUP=$(df -h)

# Remove Bash history
unset HISTFILE
rm -f /root/.bash_history
# User bash history removal may not be necessary for all distributions
# rm -f /home/vagrant/.bash_history

# Clean up log files
echo "Cleaning up log files"
find /var/log -type f -exec truncate --size 0 {} \;

echo "Clearing last login information"
>/var/log/lastlog
>/var/log/wtmp
>/var/log/btmp

# Whiteout root
echo "Clearing root filesystem"
count=$(df --sync -kP / | tail -n1  | awk '{print $4}')
dd if=/dev/zero of=/zerofile bs=1M count=$count || echo "dd exit code $? is suppressed"
sync
rm -f /zerofile

# Whiteout /boot
echo "Clearing /boot"
count=$(df --sync -kP /boot | tail -n1 | awk '{print $4}')
dd if=/dev/zero of=/boot/zerofile bs=1M count=$count || echo "dd exit code $? is suppressed"
sync
rm -f /boot/zerofile

echo "Clearing swap and disabling until reboot"
set +e
swapoff -a
# Removing swap entry from fstab may not be necessary for all distributions
# sed -i '/swap/s/^/#/' /etc/fstab
set -e

# Make sure we wait until all the data is written to disk
sync

echo "Disk usage before cleanup:"
echo "${DISK_USAGE_BEFORE_CLEANUP}"

echo "Disk usage after cleanup:"
df -h
