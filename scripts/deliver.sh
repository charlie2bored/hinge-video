#!/usr/bin/env bash
# Final render pipeline, after the product-film skill's scripts/render.ts,
# adapted to HyperFrames (whose output is already BT.709, limited range):
#
#   1. a 240 fps master      hyperframes render --fps 240 --crf 8
#   2. motion blur           average each run of 4 subframes, keep one → 60 fps (ProRes 4444)
#   3. deliverables          muted H.264, H.264 with the score, VP9 WebM, poster
#   4. verify                scripts/verify.py from the skill (duration, background, probes)
#
# Usage: scripts/deliver.sh <out-dir> [poster-seconds]
# Needs a full ffmpeg (tmix/select), e.g. the one imageio-ffmpeg ships.
set -euo pipefail

OUT=${1:?out dir}
POSTER=${2:-22.6}
NAME=hinge-designed-to-be-deleted
ROOT=$(cd "$(dirname "$0")/.." && pwd)
FFMPEG=${FFMPEG:-ffmpeg}
mkdir -p "$OUT"
MASTER="$OUT/master-240.mp4"
BLURRED="$OUT/blurred-60.mov"

if [ ! -f "$MASTER" ]; then
  (cd "$ROOT" && npx --yes hyperframes@0.8.78 render -o "$MASTER" --fps 240 --crf 8 --quiet)
fi

# 2. Motion blur: tmix 4 equal subframes, keep every 4th, retime to 60 fps.
#    HyperFrames already tags BT.709 limited range, so no matrix conversion (tv → tv).
"$FFMPEG" -v error -y -i "$MASTER" -an \
  -vf "tmix=frames=4:weights='1 1 1 1',select='not(mod(n+1\,4))',setpts=N/(60*TB),scale=in_range=tv:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,format=yuv444p10le" \
  -r 60 -c:v prores_ks -profile:v 4444 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv "$BLURRED"

H264=(-c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p
  -x264-params colorprim=bt709:transfer=bt709:colormatrix=bt709
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -movflags +faststart)

# 3. Deliverables.
"$FFMPEG" -v error -y -i "$BLURRED" "${H264[@]}" -an "$OUT/$NAME-1080p60.mp4"
"$FFMPEG" -v error -y -i "$BLURRED" -i "$ROOT/assets/audio/score.mp3" "${H264[@]}" \
  -c:a aac -b:a 256k -shortest "$OUT/$NAME-1080p60-audio.mp4"
"$FFMPEG" -v error -y -i "$BLURRED" -c:v libvpx-vp9 -b:v 0 -crf 32 -row-mt 1 -pix_fmt yuv420p -an "$OUT/$NAME-1080p60.webm"
"$FFMPEG" -v error -y -ss "$POSTER" -i "$BLURRED" -frames:v 1 -q:v 2 "$OUT/poster.jpg"

# The film is not a loop, so there is no loop-seam sheet; verify.py's seam column is informational.
rm -f "$BLURRED" "$MASTER"
ls -lh "$OUT"
