# Local parity test — MongoDB 9.0 template — 2026-11-02

## Result: PASSED locally. Not proven on Railway.

`scripts/local-test.sh` exited 0. Full phase responses are in
`local-test-evidence-2026-11-02.json` in this folder. No passwords are
in the evidence file; the test credentials were generated fresh for
this run only and discarded with the test data directory.

## Environment

- Host: Ubuntu 24.04.5 LTS, x86_64. No Docker available in this VM,
  so the test did **not** run the `mongo:9.0.4` Docker image itself.
- Binary under test: official MongoDB Community tarball for Ubuntu
  24.04, `mongodb-linux-x86_64-ubuntu2404-9.0.4.tgz`, verified by
  `mongod --version`: `db version v9.0.4`, gitVersion
  `64ade602b836c9adeffba7fa038c887ffab56196`, distmod `ubuntu2404`.
- Driver: pymongo 4.19.0 (pip, test-only, not part of the template).
- Server flags: `--bind_ip 127.0.0.1 --port 27099 --auth
  --setParameter diagnosticDataCollectionEnabled=false` — the same
  auth mode and diagnostic parameter as the Railway start command,
  but bound to localhost for a local test instead of Railway's
  `::,0.0.0.0` private-network bind.

## What passed (read the full responses in the evidence file)

1. Root user creation via the localhost exception: `{"ok": 1.0}`.
2. `server_info` version `9.0.4` (twice — once per server start).
3. Authenticated `ping`: `{"ok": 1.0}` (twice).
4. Insert acknowledged, document read back field-for-field:
   `{"_id": "parity-2026-11-02", "template": "mongodb-9.0", "value": 42}`.
5. Unauthenticated read rejected: code 13, `Unauthorized`,
   "Command find requires authentication".
6. Server stopped, restarted on the same data directory, document
   read back intact (persistence), then deleted; collection count
   after delete: 0.

## What this test does NOT prove (do not claim otherwise)

- **Live Railway deploy:** untested. It waits for Ahmed's paid Railway
  plan to be active. This is the main open item before the template
  can be called fully proven.
- **The Docker image itself:** untested (no Docker in this VM). The
  binary is the same 9.0.4 release, but the image's entrypoint
  behaviour — creating the root user from `MONGO_INITDB_*` on first
  start against an empty `/data/db` — was replicated manually here
  (localhost-exception user creation), not run through
  `docker-entrypoint.sh`.
- **Railway's IPv6 private-network bind** (`--ipv6 --bind_ip
  ::,0.0.0.0`): not run locally; the local bind was 127.0.0.1.
  The flag combination is copied verbatim from Railway's own MongoDB
  service documentation.
- **Replica set / HA / backups:** not part of this template and not
  tested.

## Re-running the test

```bash
curl -fsSL -o mongodb.tgz https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2404-9.0.4.tgz
tar -xzf mongodb.tgz
pip install pymongo   # test driver only
MONGOD_BIN=$PWD/mongodb-linux-x86_64-ubuntu2404-9.0.4/bin/mongod \
  MONGO_PYMONGO_PATH=$(python3 -c "import pymongo, os; print(os.path.dirname(pymongo.__file__))" 2>/dev/null || echo "") \
  ./scripts/local-test.sh
```

(If pymongo is installed system-wide, `MONGO_PYMONGO_PATH` can be
omitted; the script only uses it to find a venv/target install.)

## Secret scan

2026-11-02: searched the whole template folder for passwords, keys,
tokens, and the per-run test credential. Result: no real values found.
`.env.example` and `docker-compose.yml` carry placeholders only, and
compose refuses to start without `MONGO_INITDB_ROOT_PASSWORD` set.
