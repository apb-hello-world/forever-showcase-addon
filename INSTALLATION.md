# Current local installation — 0.4.0

The addon was installed November 25, 2026 at
`E:/World of Warcraft/_forever_/Interface/AddOns/ForeverShowcase`.
All 11 runtime files were SHA-256 verified; receipt: `design/installation-0.4.0.json`.
Backup: `D:/Projects/wow-forever-addons/backups/showcase-before-0.4.0-20261125-170422/ForeverShowcase`.
SavedVariables and sibling addons were not modified. The Example addon remains absent.
Reload manually to load the new TOC and capture modules. No game input was sent.

The optional Windows companion is
`dist/ForeverShowcaseCompanion/ForeverShowcaseCompanion.exe`.
Keep its `_internal` folder alongside it. See CAPTURE-WORKFLOW.md for the first test.
No installation service, startup task, GitHub remote or publication was created.

Automated: 30 tests pass. Desktop: packaged preview, default PNG Save and Copy
checked with isolated synthetic data. Save As dialog opening checked; completion
and paste into the user's chosen editor still need testing. In-game: capture
controls, success event timing, framing coordinates and reload export need owner
confirmation. Earlier toolbar/backdrop appearance remains owner-confirmed.

To roll back, close/stop scenes and replace only the runtime ForeverShowcase folder
with the backup. Preserve SavedVariables, backups and sibling folders.

## Earlier installation record

# Local installation

Forever Showcase **0.3.0** installed November 25, 2026 at
`E:/World of Warcraft/_forever_/Interface/AddOns/ForeverShowcase`.
All nine runtime files were SHA-256 verified against the source after copying.
Receipt: `design/installation-0.3.0.json`.

Previous installed copy backed up at
`D:/Projects/wow-forever-addons/backups/showcase-before-0.3.0-20261125-142538/ForeverShowcase`.
The backup directory timestamp is the execution host's label.
To roll back, close the game and replace only the installed ForeverShowcase folder
with that backup. Preserve the backup and all sibling folders and SavedVariables.

ForeverShowcaseExample was removed from the game at the owner's request on
November 25, 2026. Its two files were backed up and hash-verified under
`D:/Projects/wow-forever-addons/backups/removed-showcase-example-20261125-142742/ForeverShowcaseExample`
before removal. Reload clears its existing registrations. Development example
source remains in this project for adapter documentation and automated tests;
do not reinstall it unless requested. No other addons or SavedVariables were modified.

Validation: 20 automated Lua lifecycle/UI/presentation/package tests pass.
Independent review's toolbar dismissal finding is resolved. The owner approved
the earlier Stagekeeper window and confirmed Spellwright's first scene works.
The new toolbar, backdrop layering, color choices, timed hide and combat behavior
still need native verification. Run `/reload`, then `/showcase`, start a scene and
use the toolbar. See MANUAL-TESTS.md and PRESENTATION-HANDOFF.md.

Existing adapters receive the toolbar immediately. Backdrops remain disabled
until an adapter opts in with explicit scene frames and optional RGB color.
Spellwright was not modified by this update.

No remote repository or CurseForge publication was created.
