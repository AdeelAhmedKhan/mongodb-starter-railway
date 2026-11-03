# MongoDB 9.0 — Single-Node Database Template for Railway

**Template card description (49 characters):**
> Single-node MongoDB 9.0 database, ready to deploy

One-click MongoDB 9.0 on Railway, pinned to the official image, with
auth on, a persistent volume, and the same start command Railway's own
MongoDB service uses. No app code, no replica set, nothing to configure
beyond the root credentials.

## Deploy

Template page: https://railway.com/deploy/mongodb-90
Source: https://github.com/AdeelAhmedKhan/mongodb-starter-railway

1. Open the template page and deploy it into your Railway project.
2. Railway generates the root username and password at deploy time.
   Save them; they are shown once.
3. Connect another service in the same project with `MONGO_URL`
   (private domain), or use the TCP proxy host and port from outside
   Railway.

## Who this is for

Developers who need a current MongoDB 9 database on Railway and want
the official image with nothing extra: no app code, no replica set,
no backup job. If you need high availability or managed backups, this
single node template is not the right choice; the scope section below
says so plainly.

## Why this template exists

Railway's main MongoDB template still pins `mongo:8.0` (40,372 total /
29,003 active projects, checked 2026-11-01). The only standalone Mongo 9
entry found on the marketplace was a 0-project community template using
a custom image, not the official one. There was no one-click, official
image, single-node MongoDB 9.0 template.

Do **not** build or deploy MongoDB 8.2 from this template's history:
8.2 was a rapid release whose support ended 31 Jul 2026.

## Pinned versions (verified 2026-11-02)

- **MongoDB 9.0.4** — official `mongo:9.0.4` image. 9.0 GA 29 Sep 2026,
  supported to 31 Oct 2031 (endoflife.date, MongoDB release notes).
  9.0.4 is the latest patch (14 Oct 2026); do not stay on 9.0.0, which
  predates CVE fixes shipped in 9.0.1 and 9.0.4.
- No app runtime, no driver, no framework is pinned here — this is a
  bare database service. Connect with any MongoDB 9.0-compatible driver.

## What the template deploys (exact Railway Template Composer settings)

This is a database service, not a repo service, so there is no
`railway.toml` to read. `railway-template.json` in this folder is the
exact transcription of the Composer settings to enter when publishing;
it is not a file Railway reads automatically.

| Setting | Value |
|---|---|
| Service name | `MongoDB` |
| Image | `mongo:9.0.4` (official Docker Hub image) |
| Start command | `docker-entrypoint.sh mongod --ipv6 --bind_ip ::,0.0.0.0 --setParameter diagnosticDataCollectionEnabled=false` |
| Volume | Mounted at `/data/db` (persistent — without it, data is lost on redeploy) |
| Restart policy | On failure |
| Public networking | Off by default. Database traffic stays on the Railway private network. Add TCP proxying only if you need outside access. |

### Variables (set in the Composer)

| Variable | Value / source |
|---|---|
| `MONGO_INITDB_ROOT_USERNAME` | Generated at deploy time (do not ship a real value in this repo) |
| `MONGO_INITDB_ROOT_PASSWORD` | Generated at deploy time (do not ship a real value in this repo) |
| `MONGO_INITDB_DATABASE` | Optional. Leave unset for the default, or set your app database name. |
| `MONGO_URL` | Railway reference variable: `mongodb://${{MongoDB.MONGO_INITDB_ROOT_USERNAME}}:${{MongoDB.MONGO_INITDB_ROOT_PASSWORD}}@${{MongoDB.RAILWAY_PRIVATE_DOMAIN}}:27017` |
| `MONGO_HOST` | Railway reference variable: `${{MongoDB.RAILWAY_PRIVATE_DOMAIN}}:27017` |

The root user is created by the official image's entrypoint on first
start, only when `/data/db` is empty. Changing the password afterwards
does not change the existing root user — rotate it inside MongoDB, not
by editing the variable on a live volume.

## Connect from another service in the same project

```
MONGO_URL=mongodb://${{MongoDB.MONGO_INITDB_ROOT_USERNAME}}:${{MongoDB.MONGO_INITDB_ROOT_PASSWORD}}@${{MongoDB.RAILWAY_PRIVATE_DOMAIN}}:27017
```

Point your driver at `MONGO_URL`. From outside Railway, use the TCP
proxy host/port instead of the private domain.

## Local parity test

`docker-compose.yml` is the local equivalent of the Composer settings
above (same image, same start command, same volume path, same variable
names). Docker is not available in every test VM; `scripts/local-test.sh`
runs the same checks against a local `mongod` 9.0.4 binary instead and
writes its evidence to `docs/`.

```
./scripts/local-test.sh
```

The test proves, with full command responses (not just a 200 or a
"connected" line): authenticated `ping`, insert + read + delete of a
document, unauthenticated read rejected, and the document surviving a
server restart (persistence via the data directory).

## Honest scope — what is verified and what is not

- **Verified locally 2026-11-02 and re-verified 2026-11-03:**
  `mongod` 9.0.4 starts, auth works, a real document round-trips,
  unauthenticated access is rejected, and data survives a restart.
  See `docs/local-test-2026-11-02.md` and
  `docs/local-test-2026-11-03.md`.
- **Not tested:** a live Railway deploy of this template. That waits
  for a paid Railway plan to be active. Until then, do not claim this
  template is proven on Railway itself.
- **Not included:** a replica set, high availability, automatic
  failover, or backups. This is a single node. Railway's own MongoDB
  service can be converted to high availability from its Database
  settings; this community pin does not add that for you.
- **Support scope warning (from Railway's docs):** Railway maintains
  its own MongoDB template. Changing the image, start command, or
  variables — which this template does by pinning 9.0.4 — makes the
  database yours to manage, including future upgrades. Plan the 9.x
  patch upgrades yourself; do not assume Railway will bump this pin.

## Backups

There is no backup job in this template. Snapshot the volume, or run
`mongodump` against `MONGO_URL` on a schedule from another service,
before you depend on this database for anything you cannot rebuild.

## License

MIT — see `LICENSE`.
