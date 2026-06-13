# Quick Fix: Change SSH Port to 2222
#
# When SSH port 22 is blocked (Hostinger or hotel Wi-Fi), run this on VPS.
# Handles both "Port 22" (active) and "#Port 22" (commented) in sshd_config.

# Detect which pattern exists and fix it
if grep -q '^Port 22$' /etc/ssh/sshd_config; then
    sudo sed -i 's/^Port 22$/Port 2222/' /etc/ssh/sshd_config
elif grep -q '^#Port 22$' /etc/ssh/sshd_config; then
    sudo sed -i 's/^#Port 22$/Port 2222/' /etc/ssh/sshd_config
else
    echo "ERROR: Neither 'Port 22' nor '#Port 22' found in /etc/ssh/sshd_config"
    grep -n 'Port' /etc/ssh/sshd_config
    exit 1
fi

# systemd socket requires reload after port change
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket ssh

# Verify: port 22 should be GONE, port 2222 should be LISTEN
echo "---"
ss -tlnp | grep -E ':(22|2222)\s'
echo "---"
echo "DONE: SSH now on port 2222"
echo ""
echo "⚠️  MANDATORY: Open port 2222 TCP in Hostinger firewall panel:"
echo "   panel.hostinger.com → VPS → Firewall → Add rule: port 2222 TCP"
echo ""
echo "Then connect from Ubuntu:"
echo "   ssh -p 2222 root@VPS_IP_REDACTED"
echo ""
echo "Or add to ~/.ssh/config (Ubuntu side):"
echo "   Host hermes-vps"
echo "       HostName VPS_IP_REDACTED"
echo "       Port 2222"
echo "       User root"
echo "       IdentityFile ~/.ssh/id_ed25519"
echo ""
echo "Then just: ssh hermes-vps"
