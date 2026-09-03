#!/bin/sh
# Load the AppArmor profile the assistant's box needs, on the host.
#
# The seccomp half of the box (docker/jim-box.seccomp.json) rides with the
# container: compose reads the file and hands it to the engine. The AppArmor
# half lives in the host's kernel, so it has to be loaded here, once — and
# this script is idempotent, so the deploy page runs it on every update and
# a reboot finds the profile in /etc/apparmor.d where AppArmor reloads it.
#
# AppArmor 4 (Ubuntu 24.04) mediates user namespaces and takes the profile
# as written: abi 4.0 and the `userns,` rule. An older parser refuses those
# two lines; they are stripped, and the kernel restriction they answer does
# not exist on such a host. A host without AppArmor has nothing to load.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
SRC="$HERE/jim-box.apparmor"
DST=/etc/apparmor.d/jim-box

if ! command -v apparmor_parser >/dev/null 2>&1; then
  echo "jim-box: no apparmor_parser on this host, so AppArmor is not in the way; nothing to load"
  exit 0
fi
if command -v aa-enabled >/dev/null 2>&1 && ! aa-enabled >/dev/null 2>&1; then
  echo "jim-box: AppArmor is not enabled on this host; nothing to load"
  exit 0
fi

if apparmor_parser -Q "$SRC" >/dev/null 2>&1; then
  cp "$SRC" "$DST"
  how="with user-namespace mediation (AppArmor 4)"
else
  grep -v -e '^abi <abi/4.0>,' -e '^  userns,' "$SRC" > "$DST"
  if ! apparmor_parser -Q "$DST"; then
    echo "jim-box: the profile does not parse on this host; nothing was loaded" >&2
    rm -f "$DST"
    exit 1
  fi
  how="without the userns rule (AppArmor 3; the restriction it answers does not exist here)"
fi

apparmor_parser -r "$DST"
echo "jim-box: profile loaded $how"
if command -v aa-status >/dev/null 2>&1; then
  aa-status 2>/dev/null | grep -q 'jim-box' && echo "jim-box: in the kernel" || echo "jim-box: not listed by aa-status" >&2
fi
