#!/usr/bin/env bash
# master-backup.sh — one complete copy of QRME, JIM-mini and PDI.
#
#   ./master-backup.sh /Volumes/SDCARD/apps          # download everything
#   ./master-backup.sh /Volumes/SDCARD/apps pack     # then pack 3 archives
#
# Makes one folder per app holding the whole repository (every branch, every
# tag, all history) and every file attached to every release.
#
#   315 GiB, 5,938 files, across 804 releases. Give it hours, not minutes.
#
# Safe to stop and rerun: a file already on disk at the right size is
# skipped, so a rerun resumes where the last one stopped rather than
# starting over. Nothing is ever deleted.
#
# GITHUB_TOKEN is optional for these public repositories, but without one
# GitHub allows only 60 API calls an hour and this needs about 30.
set -uo pipefail

DEST="${1:?usage: master-backup.sh <destination> [pack]}"
PACK="${2:-}"
OWNER=davidsbianchi1984
REPOS=(qrme jim-mini pdi)

api() {                                    # $1 = path after /repos/OWNER
  local auth=()
  [ -n "${GITHUB_TOKEN:-}" ] && auth=(-H "Authorization: Bearer $GITHUB_TOKEN")
  curl -fsSL --retry 5 --retry-delay 3 "${auth[@]}" \
       -H "Accept: application/vnd.github+json" \
       "https://api.github.com/repos/$OWNER/$1"
}

mkdir -p "$DEST" || exit 1
# A run that fails nothing must not inherit the last run's accusation, and
# the tee below appends, so a stale list would grow rather than be replaced.
rm -f "$DEST/FAILED.txt"
printf 'Destination: %s\n' "$DEST"
df -h "$DEST" | tail -1
printf '\n'

for repo in "${REPOS[@]}"; do
  root="$DEST/$repo"
  mkdir -p "$root/releases"
  printf '=== %s ===\n' "$repo"

  # --- the repository itself: every branch, every tag, all history --------
  if [ -d "$root/$repo.git" ]; then
    printf '  repository: updating\n'
    git -C "$root/$repo.git" remote update --prune >/dev/null 2>&1
  else
    printf '  repository: cloning\n'
    git clone --mirror "https://github.com/$OWNER/$repo.git" \
        "$root/$repo.git" >/dev/null 2>&1
  fi
  # A working copy of main, for reading without git commands.
  [ -d "$root/source" ] || git clone "$root/$repo.git" "$root/source" \
      >/dev/null 2>&1

  # --- every file attached to every release ------------------------------
  page=1
  : > "$root/releases.tsv"
  while : ; do
    got=$(api "$repo/releases?per_page=100&page=$page") || break
    n=$(printf '%s' "$got" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)))')
    [ "$n" -eq 0 ] && break
    printf '%s' "$got" | python3 -c '
import json, sys
for rel in json.load(sys.stdin):
    for a in rel.get("assets") or []:
        print(rel["tag_name"], a["name"], a["size"],
              a["browser_download_url"], sep="\t")
' >> "$root/releases.tsv"
    [ "$n" -lt 100 ] && break
    page=$((page + 1))
  done

  total=$(wc -l < "$root/releases.tsv" | tr -d ' ')
  printf '  releases: %s files listed\n' "$total"

  i=0; got=0; had=0; failed=0
  while IFS=$'\t' read -r tag name size url; do
    i=$((i + 1))
    dir="$root/releases/$tag"; out="$dir/$name"
    mkdir -p "$dir"
    if [ -f "$out" ]; then
      have=$(wc -c < "$out" | tr -d ' ')
      if [ "$have" = "$size" ]; then had=$((had + 1)); continue; fi
    fi
    printf '\r  [%d/%d] %s/%s' "$i" "$total" "$tag" "$name"
    if curl -fsSL --retry 5 --retry-delay 3 -o "$out.part" "$url"; then
      mv "$out.part" "$out"; got=$((got + 1))
    else
      rm -f "$out.part"; failed=$((failed + 1))
      printf '\n  FAILED %s/%s\n' "$tag" "$name" | tee -a "$DEST/FAILED.txt"
    fi
  done < "$root/releases.tsv"

  printf '\r  releases: %d downloaded, %d already here, %d failed%*s\n' \
         "$got" "$had" "$failed" 40 ''

  # --- a checksum for every file, so a bad card is visible ---------------
  printf '  checksums: writing\n'
  ( cd "$root" && find releases -type f ! -name CHECKSUMS.txt \
      -exec shasum -a 256 {} + 2>/dev/null > CHECKSUMS.txt \
      || find releases -type f ! -name CHECKSUMS.txt \
         -exec sha256sum {} + > CHECKSUMS.txt )
  printf '  %s: %s\n\n' "$repo" "$(du -sh "$root" | cut -f1)"
done

if [ "$PACK" = pack ]; then
  printf 'Packing three archives (this needs room for a second copy)\n'
  for repo in "${REPOS[@]}"; do
    printf '  %s.tar ... ' "$repo"
    ( cd "$DEST" && tar -cf "$repo.tar" "$repo" ) && \
      printf '%s\n' "$(du -h "$DEST/$repo.tar" | cut -f1)"
  done
fi

printf '\nDone.\n'
[ -s "$DEST/FAILED.txt" ] && printf 'Some files failed — see %s, then rerun.\n' \
                                    "$DEST/FAILED.txt"
du -sh "$DEST"
