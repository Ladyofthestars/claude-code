#!/usr/bin/env bash
# Renders every part of a long video (public/videos/<video>/p0, p1, ...) to out/<video>/pN.mp4.
# Usage: tools/render_parts.sh made-of-stars [first-part] [last-part]
set -euo pipefail
video="$1"; first="${2:-0}"; last="${3:-99}"
mkdir -p "out/$video"
for d in public/videos/$video/p*/; do
  n=$(basename "$d"); n=${n#p}
  if [ "$n" -lt "$first" ] || [ "$n" -gt "$last" ]; then continue; fi
  echo "rendering part $n"
  npx remotion render Video "out/$video/p$n.mp4" --props="{\"video\":\"$video/p$n\"}" --concurrency=4 --log=error
done
echo "RENDER_DONE"
