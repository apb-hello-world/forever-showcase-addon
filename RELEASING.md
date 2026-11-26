# Builds and releases

Public repository: https://github.com/apb-hello-world/forever-showcase-addon

## Local Windows build

Use Python 3.12, install `requirements-dev.txt` and `requirements-companion.txt`, and install Inno Setup 6. `ISCC` can point to its compiler if not on PATH or in the normal installation locations.

```
python -m unittest discover -s tests -v
python tools/package.py
python tools/build_companion.py
python tools/build_installer.py
```

The addon ZIP contains only runtime files. The example fixture stays separate. The companion installer and `.exe.sha256` checksum are written to `dist`. Installer upgrades use a stable AppId and per-user install path. No saved capture data or exported images are included in the installer or removed by uninstalling it. Installer binaries are currently unsigned.

## GitHub Actions

Pushes to main and pull requests build and test, then retain installer/addon ZIP build artifacts. They do not create releases. Workflow dispatch also creates build artifacts only.

After testing and explicit publication approval:

- Companion: update `companion/version.py`, commit, then push tag `companion-vX.Y.Z` matching that version.
- Addon: update the TOC and API.VERSION together, tests/docs as needed, then push tag `addon-vX.Y.Z` matching the TOC.

The workflow verifies tag/version agreement and publishes only that component's assets. It uses the repository's automatic `GITHUB_TOKEN` with contents-write permission in the release job. No personal access token is required by the build workflow or by companion users.

## Update behavior

Settings → Check for updates requests public releases without authentication, ignores drafts/prereleases/addon tags, and finds a newer companion version with the expected installer and checksum. The user approves downloading; the app verifies SHA-256, persists settings, opens the interactive installer and closes. The installer detects the existing installation using its AppId. No release means no available update, not an error. GitHub rate limits/network failures are shown without affecting local image editing. A checksum checks integrity against the trusted release; it is not a code-signing certificate.

A live upgrade between published versions can be tested after the first releases exist. No release tags are created by local build scripts.

## CurseForge — pending

The owner will supply the addon project ID and set the API token in repository Actions secrets. There is no active CurseForge upload step yet; add one only after those details are available. Never include credentials in the addon, companion or repository files.
