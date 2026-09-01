#!/usr/bin/env bash
# Stock the deployment shelf from assets/shelf — one short command on the
# VPS instead of a long paste that wraps into pieces on a small terminal.
# The signup gate's own rule is "unset means open" (qrme/auth.py), so the
# header rides only when .env actually holds a key.
set -u
cd /srv/qrme
KEY=$(grep -E '^QRME_SIGNUP_KEY=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"')
HDR=()
if [ -n "$KEY" ]; then HDR=(-H "x-signup-key: $KEY"); else echo "no key set — the door is open on this deployment"; fi
ok=0
for f in assets/shelf/david-*; do
  n=$(basename "$f" | cut -d- -f2 | cut -d. -f1)
  code=$(curl -s -o /tmp/stock_answer.json -w "%{http_code}" -X POST \
    "https://sntheticprofiles.com/avatars/library?provider=elevenlabs&provider_asset_id=Pa8eJnd8sLPAX5u88jZH&label=David%20Bianchi%20$n" \
    "${HDR[@]}" --data-binary @"$f")
  echo "$code  $f"
  if [ "$code" = "201" ]; then ok=$((ok+1)); else cat /tmp/stock_answer.json; echo; fi
done
echo "stocked $ok faces"
echo -n "elevenlabs rows on the shelf now: "
curl -s https://sntheticprofiles.com/avatars/library | grep -o elevenlabs | wc -l
