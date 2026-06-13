# SSH Brute Force Patterns and Classification

## RFC1918 Internal IP Ranges
- `10.0.0.0/8` (10.0.0.0 - 10.255.255.255)
- `172.16.0.0/12` (172.16.0.0 - 172.31.255.255)  
- `192.168.0.0/16` (192.168.0.0 - 192.168.255.255)

## Classification Guidelines

### P1 STALLED (External Attack)
- **External IPs** (not RFC1918 ranges)
- >5 failed attempts within last hour
- Pattern: rapid sequential attempts with common usernames (root, admin, user, test)
- **Example**: `103.230.153.91` (20 attempts in 2 minutes across multiple usernames)

### P2 WATCH (Internal Testing/Automation)
- **Internal IPs** (RFC1918 ranges)
- Any number of attempts
- Pattern: isolated or infrequent attempts, often from automation systems
- **Example**: `172.16.0.3` (testing/automation, not malicious)

### P3 INFO (Benign/Transient)
- Single isolated attempts
- Patterns that self-resolve quickly
- Failed attempts from known legitimate sources

## Response Actions

**P1 STALLED**: Consider IP banning via `fail2ban` or firewall rules
**P2 WATCH**: Monitor but don't alert — likely internal automation
**P3 INFO**: No action needed — transient or benign

## Log Analysis Commands

```bash
# Count attempts by IP in last hour
grep "Failed password" /var/log/auth.log | grep "$(date -d '1 hour ago' '+%Y-%m-%dT%H')'" | awk '{print $11}' | sort | uniq -c | sort -nr

# Check if IP is RFC1918 internal
function is_internal_ip() {
    local ip=$1
    [[ $ip =~ ^10\. ]] || [[ $ip =~ ^172\.(1[6-9]|2[0-9]|3[0-1])\. ]] || [[ $ip =~ ^192\.168\. ]]
}
```