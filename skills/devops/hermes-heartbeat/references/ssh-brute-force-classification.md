# SSH Brute Force Classification Guidelines

## Priority Tiers

### P1 STALLED (External Attack Patterns)
- **External IPs**: Any IP not in RFC1918 ranges (not 172.16.x.x, 192.168.x.x, 10.x.x.x)
- **High frequency**: >5 failed attempts in last hour
- **Rapid sequencing**: Attempts <10 seconds apart
- **Multiple users**: Targeting user, user2, admin, root, invalid users
- **Coordinated patterns**: Systematic username cycling, port scanning behavior

**Example P1 patterns**:
- `103.230.153.91` - 20+ attempts in 2 minutes, targeting user/user2/admin/root
- Multiple external IPs with similar attack patterns within short timeframe

### P2 WATCH (Internal/Testing Patterns)
- **RFC1918 internal IPs**: 172.16.x.x, 192.168.x.x, 10.x.x.x ranges
- **Slower frequency**: 1-5 attempts per hour
- **Same user patterns**: Repeated attempts against same username (e.g., "yoga")
- **Testing behavior**: Patterns suggesting automation or testing rather than attack

**Example P2 patterns**:
- `172.16.0.3` - Repeated "yoga" user attempts, slower frequency
- Internal network IPs with consistent testing patterns

### P3 INFO (Isolated/Non-Threatening)
- **Single isolated attempts**: One-off failures
- **Diverse IPs**: No pattern across different sources
- **Self-resolving**: No recurrence after initial attempt
- **Low impact**: No evidence of systematic attack

## Response Guidelines
- **P1**: Consider IP banning, investigate source, monitor closely
- **P2**: Monitor but don't alert — likely internal testing/automation
- **P3**: Log for awareness, no action required

## RFC1918 Internal Ranges
- `10.0.0.0/8` (10.0.0.0 - 10.255.255.255)
- `172.16.0.0/12` (172.16.0.0 - 172.31.255.255) 
- `192.168.0.0/16` (192.168.0.0 - 192.168.255.255)

Any IP in these ranges should default to P2 WATCH classification unless showing clear attack patterns.

## Concrete Session Example (This Session — 2026-05-24)

**SSH auth.log check**: `grep "Failed password" /var/log/auth.log | tail -20`
**Result**: No entries found
**Classification**: P3 INFO — no recent failures detected

**Pattern observed in prior sessions**: Single or zero failures per 48h window

**Action**: No action required unless SSH failures exceed 5 in last hour from external IPs.

**Pitfall**: Internal IP `172.16.0.3` SSH failures in prior sessions were correctly classified as P2 WATCH (testing/automation) rather than P1 STALLED (external attack). This pattern is **always** P2 unless showing attack behavior.