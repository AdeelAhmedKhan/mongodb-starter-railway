#!/usr/bin/env python3
"""MongoDB 9.0 parity round-trip test (pymongo driver, no app code).

Modes:
  setup     -- create the root user via the localhost exception (no users
               exist yet). Prints the createUser command result.
  roundtrip -- authenticated ping (full response), insert one document,
               read it back, verify field-for-field. Leaves it in place
               so the restart-persistence check can find it.
  verify    -- authenticated read of the round-trip document, then
               delete it and verify the collection is empty.
  unauth    -- attempt an unauthenticated read; PASS only if MongoDB
               rejects it (OperationFailure). A successful read is FAIL.

Credentials come from the environment only (MONGO_TEST_USER,
MONGO_TEST_PASSWORD, MONGO_TEST_PORT). There is no default password.
Results are appended as JSON to the file in MONGO_EVIDENCE_JSON.
Passwords are never written to the evidence file.
"""
import json
import os
import sys

from pymongo import MongoClient
from pymongo.errors import OperationFailure


def env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"missing required environment variable: {name}")
    return value


def evidence_path():
    return os.environ.get("MONGO_EVIDENCE_JSON", "docs/local-test-evidence.json")


def record(phase, result):
    path = evidence_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data = []
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
    data.append({"phase": phase, "result": result})
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(json.dumps({"phase": phase, "result": result}, indent=2, default=str))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    port = env("MONGO_TEST_PORT")
    db_name = "parity_check"
    coll = "roundtrip"

    if mode == "setup":
        client = MongoClient(f"mongodb://127.0.0.1:{port}/", serverSelectionTimeoutMS=10000)
        result = client.admin.command(
            "createUser",
            env("MONGO_TEST_USER"),
            pwd=env("MONGO_TEST_PASSWORD"),
            roles=[{"role": "root", "db": "admin"}],
        )
        record("setup_create_root_user", result)
        return

    if mode == "unauth":
        client = MongoClient(f"mongodb://127.0.0.1:{port}/", serverSelectionTimeoutMS=10000)
        try:
            list(client[db_name][coll].find({}))
        except OperationFailure as exc:
            record("unauth_read_rejected", {"code": exc.code, "details": str(exc)})
            return
        record("unauth_read_rejected", {"error": "UNAUTHENTICATED READ SUCCEEDED — FAIL"})
        sys.exit(1)

    user = env("MONGO_TEST_USER")
    password = env("MONGO_TEST_PASSWORD")
    client = MongoClient(
        f"mongodb://{user}:{password}@127.0.0.1:{port}/admin",
        serverSelectionTimeoutMS=10000,
    )
    server_info = client.server_info()
    record("server_info", {"version": server_info["version"], "gitVersion": server_info.get("gitVersion")})
    ping = client.admin.command("ping")
    record("authenticated_ping", ping)
    collection = client[db_name][coll]

    if mode == "roundtrip":
        doc = {"_id": "parity-2026-11-02", "template": "mongodb-9.0", "value": 42}
        inserted = collection.insert_one(doc)
        record("insert", {"inserted_id": str(inserted.inserted_id), "acknowledged": inserted.acknowledged})
        found = collection.find_one({"_id": "parity-2026-11-02"})
        record("read_back", found)
        if found != doc:
            print("READ-BACK MISMATCH", file=sys.stderr)
            sys.exit(1)
        return

    if mode == "verify":
        found = collection.find_one({"_id": "parity-2026-11-02"})
        record("read_after_restart", found)
        if not found or found.get("value") != 42:
            print("PERSISTENCE CHECK FAILED — document missing after restart", file=sys.stderr)
            sys.exit(1)
        deleted = collection.delete_one({"_id": "parity-2026-11-02"})
        record("delete", {"deleted_count": deleted.deleted_count})
        remaining = collection.count_documents({})
        record("collection_empty_after_delete", {"count": remaining})
        if remaining != 0:
            sys.exit(1)
        return

    raise SystemExit(f"unknown mode: {mode}")


if __name__ == "__main__":
    main()
