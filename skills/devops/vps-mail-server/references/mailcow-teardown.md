# Mailcow Teardown — Session Log (2026-06-12)

Specifics from the Mailcow → Poste.io migration on the Hermes VPS.

## What Was Running

14 containers in `mailcow-dockerized`:
nginx-mailcow, dovecot-mailcow, postfix-mailcow, sogo-mailcow,
rspamd-mailcow, clamd-mailcow, php-fpm-mailcow, redis-mailcow,
mysql-mailcow, memcached-mailcow, unbound-mailcow, netfilter-mailcow,
olefy-mailcow, dockerapi-mailcow, ofelia-mailcow, watchdog-mailcow,
acme-mailcow, postfix-tlspol-mailcow

## Tear Down

```bash
cd /root/mailcow-dockerized
docker compose down -v    # stops containers + removes volumes
cd /root
rm -rf /root/mailcow-dockerized
```

## Docker Image Cleanup

After teardown, 14 `ghcr.io/mailcow/*` images were still cached (~3-4GB):

```bash
docker rmi $(docker images --filter "reference=ghcr.io/mailcow/*" -q)
docker image prune -a --force
```

Also cleaned dangling images: mariadb:10.11, memcached:alpine, redis:7.4.6-alpine, mcuadros/ofelia:latest.

## Postfix Cleanup

Host-level Postfix was installed alongside Mailcow. Service showed `active (exited)` but port 25 was still bound:

```bash
systemctl stop postfix
systemctl disable postfix
```
