#!/bin/bash
# Re-attach the three working trees to their remotes after a container rebuild.
#
# ## What this is for
#
# The container's disk is not persistent: it is restored from an image, and
# the image can be older than the work. On 2026-08-09 every rebuild came back
# with all three trees at 0.59.4, two stale uncommitted files, and no reflog
# entry for a day of releases -- `.git/HEAD` on disk was dated 2026-08-08
# 20:17, seconds after that round's merges. The remotes had every commit; the
# disk had none of them.
#
#     asked     did something reset these repositories
#     mattered  is this disk the same disk the work was done on
#
# So this is not a repair. It is a re-attach: the remote is the record, and a
# restored tree is a stale copy of it.
#
# ## Fast-forward only, and nothing is discarded
#
# The tree is moved only when HEAD is an ancestor of the remote branch -- when
# the remote strictly contains it. A tree carrying commits the remote does not
# have is left exactly as it is and named in the output, because that is work
# nobody else holds. Uncommitted changes are stashed rather than dropped, so
# `git stash list` can always get them back.
set -uo pipefail

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

sync() {
  local dir="$1" name branch head remote
  name=$(basename "$dir")
  [ -d "$dir/.git" ] || return 0

  branch=$(git -C "$dir" symbolic-ref --quiet --short HEAD 2>/dev/null) || {
    echo "  $name: detached HEAD, left alone"; return 0; }
  git -C "$dir" fetch -q origin "$branch" 2>/dev/null || {
    echo "  $name: cannot reach origin/$branch, left alone"; return 0; }

  head=$(git -C "$dir" rev-parse HEAD)
  remote=$(git -C "$dir" rev-parse "origin/$branch" 2>/dev/null) || return 0

  if [ "$head" = "$remote" ]; then
    echo "  $name: current at ${head:0:8} ($branch)"
    return 0
  fi
  if ! git -C "$dir" merge-base --is-ancestor "$head" "$remote"; then
    echo "  $name: HEAD ${head:0:8} is not on origin/$branch -- it holds commits" \
         "the remote does not. Left alone."
    return 0
  fi

  if [ -n "$(git -C "$dir" status --porcelain)" ]; then
    git -C "$dir" stash push -u -q -m "resync $(date -u +%FT%TZ)" 2>/dev/null \
      && echo "  $name: uncommitted changes stashed (git stash list)"
  fi
  git -C "$dir" reset -q --hard "origin/$branch"
  echo "  $name: ${head:0:8} -> ${remote:0:8} (the disk was behind the remote)"
}

# Overridable so the logic can be exercised against throwaway clones rather
# than against the three trees it exists to protect.
TREES="${RESYNC_TREES:-/home/user/QRME /workspace/jim-mini /workspace/pdi}"

echo "resync: working trees against their remotes"
for tree in $TREES; do sync "$tree"; done
