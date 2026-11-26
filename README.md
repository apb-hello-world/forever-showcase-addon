# Forever Showcase

A standalone developer companion for repeatable, real in-game add-on scenes on
World of Warcraft: Forever (Interface 16001). Adapters own the actual rendering
and sample content. Showcase owns discovery and the single active session.

The Stagekeeper window opens with `/showcase`. Select an add-on and scene, read
its notes, then click Start scene. The selector closes and a compact scene toolbar
appears with Previous, Next, Restart, Stop, Scene list, Backdrop and Hide for 10s.
No slash commands are needed after opening Showcase. Stop restores the workspace.
Capture adds a real user-requested WoW screenshot and remembers a crop area.
The optional Windows companion crops and styles separate exports after Send & reload.
See [CAPTURE-WORKFLOW.md](CAPTURE-WORKFLOW.md) for the local test workflow.
No game input, arbitrary addon hooks, or replacement WoW APIs are used.

## Commands

| Command | Result |
| --- | --- |
| `/showcase` or `/showcase show` | Open Stagekeeper controls |
| `/showcase hide` | Hide controls, preserving the active scene |
| `/showcase help` | Command help |
| `/showcase list` | Registered scenes, including unavailability reasons |
| `/showcase <addon> <scene>` | Enter or restart a scene |
| `/showcase next` | Next available scene in the current integration, wrapping |
| `/showcase off` | Stop and restore |
| `/showcase status` | Active scene, deferred restoration, or failure state |
| `/showcase info` | Current description, suggested caption and capture instructions |

No integrations are bundled in the production ZIP. Missing adapters and unknown
scenes are reported without stopping the current scene. The separate example is
a **nonvisual lifecycle fixture**, not a screenshot scene. Try `example first`,
`next`, and `off` after installing it. Spellwright supplies its own real integration; the first scene was owner-confirmed.

The window uses original Stagekeeper artwork selected by the owner. Lists paginate
when needed; long scene notes scroll with the mouse wheel. Unavailable scenes can
be selected to read the reason. Drag the title plaque to move the window. It fits
the viewport and keeps position only until reload. Opening the window never starts
a scene. Availability refreshes once per second while the window is visible.

Combat stops the session immediately, invalidates its guarded callbacks, runs
explicitly combat-safe cleanup, and defers leave/protected cleanup until combat
ends. The scene does not resume automatically. A cleanup error blocks activation
until reload; all other cleanup callbacks are still attempted. No session is persisted. Capture records and per-addon crop areas are saved in
ForeverShowcaseDB; adapter fixtures never enter that storage. Reload during combat discards remaining in-memory
restoration: adapters must never depend on logout cleanup to protect storage.

## Installation and packaging

Copy `ForeverShowcase/` into `E:/World of Warcraft/_forever_/Interface/AddOns/`.
The Example addon is a development fixture only; do not reinstall it without request.
Back up an existing installation first. Do not touch WTF/SavedVariables or sibling
add-ons. Reload manually; never send game input automatically.

From this project directory, run:

```powershell
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
..\.venv\Scripts\python.exe tools\package.py
```

The Python test dependency is `lupa==2.8`; tests explicitly use `lupa.lua51`.
Packaging uses only the Python standard library and writes deterministic,
allowlisted ZIPs to `dist/`. Production and example are separate archives.
Source and companion releases: https://github.com/apb-hello-world/forever-showcase-addon.
CurseForge publishing is pending the project ID and repository secret.

## Evidence and next steps

Implemented: runtime, commands, Stagekeeper native UI, API v1, isolated executable
example, packaging, and integration documentation. Automated: Lua 5.1 lifecycle
and UI interaction tests with mocked WoW frames, registration order, archive and
texture-format checks. Version 0.4.0 installation status is recorded in
INSTALLATION.md. The owner approved the overall 0.2.0 window appearance; the 0.3.0
toolbar and backdrop await native checks. Protected-frame behavior and real adapters require
each real adapter's in-game verification; this fixture makes no visual claims.

See [API.md](API.md), [INTEGRATION.md](INTEGRATION.md),
[MANUAL-TESTS.md](MANUAL-TESTS.md), and [SPELLWRIGHT-HANDOFF.md](SPELLWRIGHT-HANDOFF.md).

## Clean screenshot controls in 0.3.0

Drag the toolbar by its title. Hide for 10s removes the controls for a manual
capture, then restores them automatically. Background options are Off, Scene,
Charcoal, Ivory and Green. Scene uses the adapter-selected RGB color.

Existing adapters get the toolbar immediately. Backdrops require the small
opt-in documented in [PRESENTATION-HANDOFF.md](PRESENTATION-HANDOFF.md). Until then
the control is disabled with a visible explanation. This mode covers ordinary
UI rather than hiding UIParent; unrelated high-strata dialogs may still appear.

## Optional desktop capture companion in 0.4.0

Launch `dist/ForeverShowcaseCompanion/ForeverShowcaseCompanion.exe`.
Use Draw area ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ Capture ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ Captures ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ Send & reload in game, then select the
imported capture on the desktop. See CAPTURE-WORKFLOW.md for folders, presets,
export controls and the test checklist. 30 automated tests pass; real capture
event timing and pixel mapping await the owner. No GitHub work or publishing.

## Desktop companion 0.7.1

Download the Windows installer from this repository's companion releases. It installs for the current user, adds a Start menu shortcut and an uninstaller, and preserves settings and capture records in `%LOCALAPPDATA%/ForeverShowcase` across upgrades. The addon remains usable without it.

- Click a capture to edit it. Ctrl-click adds/removes captures and previews the newly added capture. Shift-click selects a range; Ctrl+A in the list selects all.
- The Finish controls apply edits to every selected capture. Each capture retains its own saved style. Selecting more captures alone does not overwrite their styles.
- Settings > Default save location sets the base export path. Exports go into a subfolder for the captured addon (display name, or addon ID for older records).
- Export opens a separate window for PNG, JPEG or WebP, quality, destination and dimensions. Maintain aspect ratio calculates the other dimension for each image; the 850 px wide preset is ready for smaller description images. Unlock the ratio to fit with padding, crop to fill, or stretch. The window stays open for repeat exports; Reset to defaults restores full-size PNG. Existing exports and originals are preserved.
- Copy Image appears only when one capture is selected, and copies the current preview mode at full resolution.
- Full-size preview opens a separate resizable window with Fit window, 100%, mouse-wheel zoom and drag-to-pan controls. Scrollbars appear only when the image overflows.
- Settings ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ Check for updates checks public GitHub companion releases. Download and installation require confirmation; no account or token is needed. Addon releases are ignored by the companion updater.

See [RELEASING.md](RELEASING.md) for build, installer and release instructions.
