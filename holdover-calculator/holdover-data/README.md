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

**3. Generate the manifest, then sign it. Never hand-write either.**

Two commands in the app repo:

    python3 tools/make-table-manifest.py --data-version <n> > /tmp/m.json
    swift tools/table-data-tool.swift sign --manifest /tmp/m.json \
        --out .../holdover-data/manifest.json

The generator computes `sha256` and `bytes`, and reads the accepted schema
versions out of the app's own Swift source so the two cannot drift. The signer
refuses a key the app does not carry, and refuses a manifest missing any field
the signature has to cover. A hand-edited `sha256` is a payload no device will
accept.

**4. `manifest.json` is a signed envelope, not a readable manifest.**

It looks like this:

    { "keyID": "...", "payload": "<base64>", "signature": "<base64>" }

The signed region is the manifest bytes **verbatim**, which is why they are
carried base64-encoded rather than inline: nothing re-serializes them, so key
order, whitespace and number formatting cannot drift between the signer and the
app. To read what a published manifest actually says:

    curl -s <url>/manifest.json | python3 -c \
      'import json,base64,sys;print(base64.b64decode(json.load(sys.stdin)["payload"]).decode())'

Signing is what makes this repository untrusted infrastructure. A hash proves
the payload matches the manifest; it does not prove who published them, and both
come from here. Anyone who can write to this repo can write a consistent lie —
but not a signed one, because **the private key is never on GitHub.** It lives
on Greg's Mac under `~/.config/holdover-calculator/table-signing.key`, and the
app carries only the public half (key ID `93e6e396`, in
`Models/TableManifest.swift`).

Signed as of 2026-10-25. See the plan's "Threat model" section.

**5. The app always keeps a copy of the tables in its bundle.**

If these files are missing, malformed, unreachable or refused, the app falls back
to the tables it shipped with and behaves exactly as it did before. Deleting
everything here degrades updates; it does not break the app.
