# Capture and desktop companion — 0.4.0 local test build

The desktop companion is optional. Showcase still provides real addon scenes,
navigation, backdrops, framing, and normal full-screen WoW screenshots without it.
No GitHub repository, release, installer, or publication is part of this build.

## First in-game test

1. Reload WoW to load 0.4.0, then open `/showcase` and start a Spellwright scene.
2. Click **Draw area** and drag a rectangle, or **Auto-fit area** to surround the
   adapter's registered windows with 16 pixels of space. Right-click/Escape cancels
   drawing. The area is remembered per addon and reused across its scenes.
3. Click **Capture**. Showcase hides its controls and guide, waits at least two
   frames and 0.25 seconds, then requests a real full-screen screenshot. A flash
   appears only after WoW reports success. Close chat and unrelated windows first.
4. Move to another scene and capture it with the same area. Don't press the normal
   screenshot key while Showcase is already taking a screenshot.
5. Open **Captures**. Review named captures for the current scene. Each row has an X to remove its record; All captures shows other scenes.
   **Live framing** shows the current scene under a mask; it is not a saved image.
   **Remove record** removes metadata only, never a screenshot file.
6. Click **Send & reload**. This stops the scene, saves the crop instructions in
   SavedVariables, and reloads the UI. Screenshots were already written to disk.

The list holds 200 records. After importing a batch, remove old records if needed.
A changed screen resolution requires drawing/fitting again. UI scale changes
cancel an active drawing/capture; frame placement should be checked before reuse.
Only crop settings and records persist; scenes never resume after reload.
Combat cancels an unstarted capture. If capture had already started, its record
requires manual review. A screenshot timeout blocks another capture until reload.

## Desktop test

Launch `dist/ForeverShowcaseCompanion/ForeverShowcaseCompanion.exe`.
Keep the whole folder together, including `_internal`; Python is not required.

**Folders & setup** selects:

- The account's `WTF/Account/<account>/SavedVariables/ForeverShowcase.lua`.
- The game client's `Screenshots` folder.
- The default export folder (initially `Pictures/Forever Showcase`).

For this local checkout, the app looks under `E:/World of Warcraft/_forever_` and
automatically selects the manifest path when there is exactly one account. Other
installs/accounts use Browse. The manifest may not exist until the first send.

The companion polls every two seconds and waits for stable manifest metadata.
It parses a bounded literal-data subset of Lua; it never executes SavedVariables.
Only explicitly sent records import. Screenshot matches require a filename time
within the capture interval (one-second tolerance) and exact full-screen pixel
dimensions. Multiple possible files, overlapping records, and interrupted scenes
require **Choose original**. It never selects the newest file as a fallback.
These are conservative matching heuristics, not an exact filename supplied by WoW.
Verify the first real capture and any uncertain match before exporting.

Choose **Original**, **Crop**, or **Styled** above the preview. Save, Save as, and
Copy use that selected mode at full resolution. **Save** creates a uniquely named
PNG in the default directory. **Save as** supports PNG and JPEG. Exports cannot
replace known originals or be saved in the WoW screenshot directory. Rounded
corners and transparency are preserved in PNG; JPEG and clipboard images flatten
transparent pixels onto white. The clipboard uses the Windows DIB image format.

Built-in presets: Stagekeeper, Clean, Gallery ivory, Transparent. Customize
padding, radius, border, shadow, background and border color; Save preset keeps a
named local style. Shadow space can exceed padding to avoid clipping the blur.
Manual image import uses the full image; it does not require WoW or a manifest.
Removing a companion record keeps original/exported files and ignores that record
on future imports. Desktop records, folders and custom presets live in
`%LOCALAPPDATA%/ForeverShowcase/settings.json`.

The companion does not communicate with WoW, inject input, upload images, alter
SavedVariables, or delete original files. No desktop process is needed to play
or use Showcase. Image reads are limited to 40 megapixels; styled exports to 50.

## Validation boundaries

Automated checks cover lifecycle cleanup, capture delay/success/failure/timeout,
combat cancellation, screen bounds/resolution, safe parsing, matching ambiguity,
pixel-exact cropping, styled output and preservation of originals. Synthetic QA
fixtures remain under `design/qa` and are excluded from both production packages.
The packaged desktop application is checked locally. New native controls and the
real WoW screenshot event/timing/coordinate mapping require the owner's game test.

Test rounded PNG in an image editor, copy/paste into your usual publishing tool,
Save and Save as, folder choices, a second batch, missing/duplicate screenshots,
changing UI scale, Stop, combat restoration, and addon operation with the app closed.

## Development

Run from the project root:

```powershell
../.venv/Scripts/python.exe -m unittest discover -s tests -v
../.venv/Scripts/python.exe -m companion.app
../.venv/Scripts/python.exe tools/build_companion.py
../.venv/Scripts/python.exe tools/package.py
```

The desktop runtime uses Python 3.12, Tkinter and Pillow; PyInstaller builds the
portable Windows folder. No adapter changes are needed for capture. API v1 and
`SetPresentation({frames=..., background=...})` remain unchanged.
