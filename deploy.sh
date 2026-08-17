#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/custom_components/virtual_switch"
VERSION_FILE="$SCRIPT_DIR/VERSION"
MANIFEST="$SRC_DIR/manifest.json"
CONTAINER="homeassistant"
DEST_IN_CONTAINER="/config/custom_components/virtual_switch"

RESTART=1
if [[ "${1:-}" == "--no-restart" ]]; then
  RESTART=0
fi

current="$(cat "$VERSION_FILE")"
major_minor="${current%.*}"
build="${current##*.}"
new_build="$(printf "%04d" $((10#$build + 1)))"
new_version="${major_minor}.${new_build}"
echo "$new_version" > "$VERSION_FILE"

python3 - "$MANIFEST" "$new_version" <<'PYEOF'
import json
import sys

path, version = sys.argv[1], sys.argv[2]
with open(path) as file:
    data = json.load(file)
data["version"] = version
with open(path, "w") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)
    file.write("\n")
PYEOF

echo "== Verzió: $new_version =="
find "$SRC_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
docker exec "$CONTAINER" rm -rf "$DEST_IN_CONTAINER"
docker cp "$SRC_DIR" "$CONTAINER:$DEST_IN_CONTAINER"
echo "== Deployolva: $CONTAINER:$DEST_IN_CONTAINER =="

if [[ "$RESTART" -eq 1 ]]; then
  docker restart "$CONTAINER" >/dev/null
  echo "== Home Assistant újraindítva =="
else
  echo "== --no-restart: a konténer nem lett újraindítva =="
fi
