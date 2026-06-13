# Hermes Onboard — Check Quick Reference

> 10 validation checks for Hermes Agent setup. Each check has: what to verify, how to verify, and the fix command.

## 1. Core Files

**Verify:** `~/.hermes/config.yaml`, `~/.hermes/env.sh`, `~/.hermes/skills/` exist
```bash
test -f ~/.hermes/config.yaml && echo "config.yaml OK" || echo "MISSING"
test -f ~/.hermes/env.sh && echo "env.sh OK" || echo "MISSING"
find ~/.hermes/skills -name 'SKILL.md' | wc -l
```
**Fix:** `touch ~/.hermes/env.sh && chmod 600 ~/.hermes/env.sh`

## 2. API Keys

**Verify:** Source `~/.hermes/env.sh` and check keys
```bash
source ~/.hermes/env.sh
[ -n "$OPENROUTER_API_KEY" ] && echo "OPENROUTER_API_KEY OK" || echo "MISSING"
[ -n "$DEEPSEEK_API_KEY" ] && echo "DEEPSEEK_API_KEY OK" || echo "MISSING"
[ -n "$TELEGRAM_BOT_TOKEN" ] && echo "TELEGRAM_BOT_TOKEN OK" || echo "MISSING"
```
**Fix:** `nano ~/.hermes/env.sh` — add missing keys

## 3. Docker Services

**Verify:** All expected containers are Up
```bash
docker ps --format "{{.Names}}: {{.Status}}"
```
**Expected:** hermes-agent (Up), traefik (Up)
**Fix:** `docker compose -f /opt/hermes/docker-compose.yml up -d`

## 4. Telegram Connectivity

**Verify:** Bot token is valid and receiving
```bash
source ~/.hermes/env.sh
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq '.ok'
```
**Fix:** Verify token with @BotFather, check webhook/polling config

## 5. Cron Jobs

**Verify:** At least heartbeat cron job exists and is healthy
```bash
# Use Hermes: cronjob(action='list')
```
**Fix:** `cronjob(action='create', schedule='0 8,14,20 * * *', name='heartbeat', prompt='Run hermes-heartbeat skill')`

## 6. Skills Integrity

**Verify:** Stable skill count, no corrupt files
```bash
SKILL_COUNT=$(find ~/.hermes/skills -name 'SKILL.md' | wc -l)
echo "Skills: $SKILL_COUNT"
find ~/.hermes/skills -name 'SKILL.md' -size 0  # should be empty
```
**Fix:** `hermes skills update` or manually clone from taps

## 7. Memory System

**Verify:** Memory and Honcho are functional
```bash
# Test memory read/write via Hermes tool: memory(action='add', target='memory', content='onboard probe')
# Then: memory(action='remove', ...) to clean up
```
**Fix:** Check `~/.hermes/config.yaml` for memory/honcho configuration

## 8. Network / Firewall

**Verify:** Outbound internet, inbound webhooks, DNS
```bash
curl -s --max-time 5 https://api.openrouter.ai/api/v1/models > /dev/null && echo "Outbound OK" || echo "FAILED"
nslookup api.openrouter.ai > /dev/null 2>&1 && echo "DNS OK" || echo "FAILED"
```
**Fix:** `ufw allow 443/tcp`, check cloud firewall, verify DNS

## 9. SSH Security (Optional)

**Verify:** Key-only auth, fail2ban active
```bash
grep "^PasswordAuthentication" /etc/ssh/sshd_config
grep "Failed password" /var/log/auth.log | tail -5 | wc -l
```
**Fix:** Configure key-only auth, install fail2ban

## 10. Backup Strategy (Optional)

**Verify:** Backup cron jobs or scripts exist
```bash
cronjob(action='list') | grep -i backup
```
**Fix:** Configure rclone or rsync backup for `~/.hermes/` and `/opt/hermes/`

## Verdict Lines

| Condition | Verdict |
|-----------|---------|
| All pass, no warnings | "All set — Hermes is fully operational." |
| Only warnings, no failures | "Hermes will run, but N optional item(s) need attention." |
| Any failures | "Setup incomplete — N required item(s) need attention before Hermes can run." |
