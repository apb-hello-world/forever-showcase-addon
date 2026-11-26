# Forever Showcase development

Canonical local project: `D:/Projects/wow-forever-addons/forever-showcase`.
Runtime folder: `ForeverShowcase`. Public remote: `apb-hello-world/forever-showcase-addon`.
The owner authorized this shared addon/companion repository and release workflow.
Publish releases only when requested; component tags trigger release automation.
CurseForge publishing awaits the project ID and repository secret.
Do not modify Spellwright or sibling add-ons as part of companion development.

Read README.md, API.md and INTEGRATION.md before changes. Preserve the versioned
contract; changes to adapter obligations need explicit documentation and tests.
No global WoW API replacements, arbitrary addon hooks, SavedVariables fixtures,
gameplay side effects or automatic game input. No new native UI without reading
the shared Forever UI README/DESIGN/AGENTS/NATIVE and current Hub guidelines.

Validation (from project root):
`../.venv/Scripts/python.exe -m unittest discover -s tests -v`.
Use Python with `lupa==2.8` (Lua 5.1 runtime); mock tests are not native proof.
Packaging: `../.venv/Scripts/python.exe tools/package.py`.
Allowlist runtime files only; keep test fixture in its separate developer ZIP.
Update TOC and API.VERSION together when versioning. No upload automation.

Installation: back up the target addon directory; copy only the corresponding
runtime folder into `E:/World of Warcraft/_forever_/Interface/AddOns/`. Preserve
SavedVariables and all sibling addons. Do not claim installed without doing and
verifying the copy. Ask the user to perform MANUAL-TESTS.md; never send game input.
Report implemented, automated, installed, and user-confirmed states separately.
