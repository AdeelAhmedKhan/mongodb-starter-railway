#!/usr/bin/env bash
# Local Railway-parity test for the MongoDB 9.0 template.
# Requires: a mongod 9.0.4 binary (MONGOD_BIN, or `mongod` on PATH)
# and pymongo (pip install pymongo). Docker is NOT required.
# Test credentials are generated fresh for this run only and are never
# written to the evidence file or the repo.
set -euo pipefail

cd "$(dirname "$0")/.."
MONGOD_BIN="${MONGOD_BIN:-$(command -v mongod || true)}"
if [ -z "$MONGOD_BIN" ]; then
  echo "FAIL: no mongod binary found. Set MONGOD_BIN to a mongod 9.0.4 binary." >&2
  exit 1
fi

PORT="${MONGO_TEST_PORT:-27099}"
WORKDIR="$(mktemp -d)"
DBPATH="$WORKDIR/data"
LOG="$WORKDIR/mongod.log"
EVIDENCE="docs/local-test-evidence-2026-11-02.json"
export MONGO_TEST_PORT="$PORT"
export MONGO_EVIDENCE_JSON="$EVIDENCE"
# Fresh test-only credentials for this run; never a repo value.
export MONGO_TEST_USER="parity_root"
export MONGO_TEST_PASSWORD="parity-test-only-$(date +%s)"
export PYTHONPATH="${MONGO_PYMONGO_PATH:-}"

rm -f "$EVIDENCE"
"$MONGOD_BIN" --version | head -1

start_mongod() {
  mkdir -p "$DBPATH"
  "$MONGOD_BIN" --dbpath "$DBPATH" --bind_ip 127.0.0.1 --port "$PORT" \
    --auth --fork --logpath "$LOG" \
    --setParameter diagnosticDataCollectionEnabled=false
}
stop_mongod() {
  "$MONGOD_BIN" --dbpath "$DBPATH" --shutdown || true
}

cleanup() {
  stop_mongod || true
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

start_mongod
python3 scripts/roundtrip.py setup
python3 scripts/roundtrip.py roundtrip
python3 scripts/roundtrip.py unauth
stop_mongod
# Persistence check: same data directory, fresh process.
start_mongod
python3 scripts/roundtrip.py verify
stop_mongod
trap - EXIT
rm -rf "$WORKDIR"

echo "LOCAL PARITY TEST PASSED. Evidence: $EVIDENCE"
