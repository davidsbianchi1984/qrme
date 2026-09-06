#!/bin/sh
# What the three public names answer, checked against what this checkout
# carries — from the host, as the last line of the deploy block.
#
# The runbook's step 5 checks the three names from your own machine, which
# is the path a visitor takes and the only place reachability can be
# proven. That check has two shells and a choice between them, and the
# choice has been made wrong three times running: a Windows handheld SSH'd
# into Ubuntu is sitting at a Unix prompt, `curl.exe` is not a program
# there, and the deploy reads as broken after it went perfectly. This line
# has no choice in it. It runs where the deploy block already put you.
#
# It answers the question that check was actually catching: did the pull
# fetch the thing you are releasing. A checkout left on another branch
# pulls that branch, prints `Already up to date`, builds, and comes up
# healthy — the version the name answers is the only thing that says so,
# and it once said so two releases late. So the number is not just printed;
# it is compared with the version in this checkout's pyproject, and a
# disagreement is an exit status rather than something to notice.
#
# The three URLs come from the same .env the compose line uses, so this
# reads whatever names the stack was told it has. Give it another env file
# as the first argument to check a different one.
set -u

HERE=$(cd "$(dirname "$0")" && pwd)
ENV_FILE="${1:-$HERE/../.env}"
PYPROJECT="$HERE/../pyproject.toml"

if [ ! -f "$ENV_FILE" ]; then
  echo "beta-versions: no env file at $ENV_FILE" >&2
  exit 2
fi

expected=$(sed -n 's/^version = "\([^"]*\)".*/\1/p' "$PYPROJECT" | head -n 1)
if [ -z "$expected" ]; then
  echo "beta-versions: no version in $PYPROJECT" >&2
  exit 2
fi

# A value read from .env without sourcing it: the file holds the master
# key, and `.`-ing it would put every secret in this shell's environment.
value() {
  sed -n "s/^$1=//p" "$ENV_FILE" | head -n 1 | sed 's/[[:space:]]*$//; s#/*$##'
}

status=0
for pair in "QRME:QRME_PUBLIC_URL" "JIM:JIM_PUBLIC_URL" "PDI:PDI_PUBLIC_URL"; do
  name=${pair%%:*}
  var=${pair#*:}
  url=$(value "$var")
  if [ -z "$url" ]; then
    printf '%-5s %-32s %s\n' "$name" "($var is not set)" "-"
    status=1
    continue
  fi
  host=${url#*://}
  body=$(curl -sS --max-time 15 "$url/health" 2>&1) || {
    printf '%-5s %-32s %s\n' "$name" "$host" "unreachable: $body"
    status=1
    continue
  }
  got=$(printf '%s' "$body" | sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  if [ -z "$got" ]; then
    printf '%-5s %-32s %s\n' "$name" "$host" "no version in: $body"
    status=1
  elif [ "$got" = "$expected" ]; then
    printf '%-5s %-32s %s\n' "$name" "$host" "$got"
  else
    printf '%-5s %-32s %s\n' "$name" "$host" "$got  <- this checkout is $expected"
    status=1
  fi
done

if [ "$status" -eq 0 ]; then
  echo "all three answer $expected"
else
  echo "a name is not answering $expected: a container that did not rebuild, or a pull that fetched another branch" >&2
fi
exit "$status"
