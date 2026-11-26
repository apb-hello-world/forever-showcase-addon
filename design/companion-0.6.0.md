# Companion 0.6.0

Independent resizable preview opens in Fit mode with 100%, zoom, scroll and drag-to-pan. Ctrl-click multi-selection previews the newly added image; Shift-click selects ranges and Ctrl+A selects all. Finish edits persist per-record and apply to all selected captures. Batch export snapshots selected records, renders sequentially, uses unique names, preserves originals and reports partial failures.

Per-user Inno Setup installer uses a stable AppId and preserves capture settings. Settings includes opt-in GitHub update checks without authentication, exact release asset URL validation, checksum verification and confirmation before launching the installer. Component-specific GitHub release tags keep addon and companion updates separate. CurseForge upload remains unconfigured pending owner details.

Evidence: 35 automated tests passed. Native Tk smoke verified Ctrl-click focus/selection, selected-only style application, batch export, deselection, and separate preview fit/100% rendering. Public GitHub check succeeded without credentials and returned no newer release. Installer and reinstall both exited successfully, installed EXE hash matches the portable build, and existing capture settings hash remained unchanged. Live cross-version GitHub upgrade awaits published companion releases. No WoW runtime change in this revision.
