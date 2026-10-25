# Holdover Calculator — published table data

Static files the Holdover Calculator app can fetch to update its holdover
tables without an App Store release.

Design, threat model and phasing live in the app repo:
`docs/holdover-data-updates-plan.md` in `kilolimallc/holdover-calculator`.

**Nothing reads these yet.** No shipped app version fetches them. They exist so
the publishing workflow and the manifest generator are exercised before anything
depends on them (Phase 1).

## Files

| File | What it is |
|---|---|
| `manifest.json` | Points at the current payload and describes it |
| `holdover_fluids-<n>.json` | A payload. `<n>` is its `dataVersion` |

## Rules — read before editing anything here

**1. Payload files are immutable. Never rewrite one in place.**

Publishing a correction means uploading `holdover_fluids-<n+1>.json` and
repointing `manifest.json` at it. The old file stays. This is what makes
rollback a one-line edit, and what lets the `sha256` be trusted as a cache key.
Editing a payload in place breaks both.

**2. `dataVersion` only ever increases.**

The app refuses a payload whose `dataVersion` is not greater than the one it has
already adopted. A rollback therefore publishes a *new* version containing the
*old* bytes — to undo `-17`, publish `-18` holding `-16`'s content. Do not
decrement.

**3. Generate the manifest, never hand-write it.**

    python3 tools/make-table-manifest.py --data-version <n> > manifest.json

in the app repo. It computes `sha256` and `bytes`, and it reads the accepted
schema versions out of the app's own Swift source so the two cannot drift. A
hand-edited `sha256` is a payload no device will accept.

**4. The manifest must be signed before any app version reads it.**

The current `manifest.json` is **unsigned**, which is safe only because nothing
consumes it. A hash proves the payload matches the manifest; it does not prove
who published them, and both come from this same repository. Anyone who can
write here can write a consistent lie.

Before the app gains a fetch path, the manifest becomes an Ed25519-signed
envelope with the payload hash and `dataVersion` *inside* the signed region, and
the private key stays off GitHub. See the plan's "Threat model" section.

**5. The app always keeps a copy of the tables in its bundle.**

If these files are missing, malformed, unreachable or refused, the app falls back
to the tables it shipped with and behaves exactly as it did before. Deleting
everything here degrades updates; it does not break the app.
