# Native verification (pending)

No automated game input. Perform these checks manually on a test character.

## Stagekeeper UI in 0.2.0

1. `/reload`, then `/showcase`. Confirm walnut/velvet/brass shell, live title,
   readable columns, no overlapping text, no opaque texture outside the rim.
2. With Example enabled, select First memory fixture, click Start scene, then
   Hide controls. `/showcase status` should still report `example first`.
   Reopen; test close and Escape also preserve the scene. Stop scene restores it.
3. Select Unsupported feature: see its reason and disabled Start. Next scene
   should skip it. No real Spellwright entries should appear without its adapter.
4. Drag by the title, close/reopen, and compare ordinary UI scale and a small
   viewport. Body/controls must remain within artwork. Window position resets on
   reload. Check pagination and mouse-wheel notes with a real long-content adapter.
5. Enter combat with an example active. The UI must show pending restoration and
   block activation; leaving combat completes restoration without resuming.
6. Overlap Showcase and two suite windows. Click exposed shells and controls,
   drag, close/reopen; foreground surfaces must cover all rear text and controls.

## Core and adapters

1. Install only ForeverShowcase. Reload: `/showcase list` reports no integrations;
   `/showcase spellwright editor` explains missing integration. No Lua error.
2. Install the separate example and reload. List shows three scenes, one unavailable
   with a reason. Start `example first`, use `info`, `next`, repeated activation,
   then `off` twice. The example deliberately renders no screenshot interface.
3. Start the fixture, enter combat normally: status becomes stopped/pending;
   activation is blocked. Leave combat: restoration completes; no auto-resume.
4. Start a fixture and reload, including during combat if the client permits it:
   status must be inactive. No demo SavedVariables should exist.
5. Disable Showcase: the example loads without errors. Re-enable and reload:
   registration succeeds once. Repeat with a real adapter when available.
6. For each future real scene: capture the original workspace/settings, activate,
   inspect all interactive write paths, capture manually with chat closed, then
   exit and compare workspace/geometry/settings. Repeat after combat, switching,
   reload, timer activity and simulated partial failures. Confirm no real data or
   gameplay changes. Confirm real native artwork, readability and screenshot framing.

Record client build, adapter version, scene, result and user evidence. Unit tests
cannot establish actual protected-frame behavior or visual correctness.

## Toolbar and backdrop in 0.3.0 (native checks pending)

1. Start a scene from the selector: it closes and the toolbar appears. Test
   Previous, Next, Restart, Stop and Scene list without slash commands.
2. Move the toolbar by its title; confirm it stays inside a small viewport.
3. Hide for 10s: selector and toolbar disappear, scene remains, toolbar returns.
4. Legacy adapter: background is disabled with a clear reason.
5. Updated adapter: cycle Off, Scene, Charcoal, Ivory and Green. Verify actual
   scene frames and input shields remain visible above the backdrop.
6. Enter combat normally: backdrop disappears immediately; restoration completes
   after combat. Stop, switch, reload and failed entry must leave no opaque cover.
7. Alternate clicking scene windows and toolbar; recovery controls remain on top.

## 0.4.0 capture and optional companion

Follow CAPTURE-WORKFLOW.md end to end. Native capture controls, real screenshot
events and pixel mapping remain pending owner confirmation. Preserve originals;
check two scenes have identical crop sizes, repeat after reload, and verify the
addon works when the companion is closed.


## 0.5.0 controls
- Reload WoW. Capture twice; verify scene title + capture numbers and X removal. Original files stay on disk.
- Open Scene list; select a different scene, then Start scene. Verify selection alone does not start it.
- Auto-fit area surrounds windows registered by the scene integration.
- Launch the companion: verify transparent exterior, artwork controls, header dragging, minimize/taskbar restore, maximize/restore and close.
- Open the gear, change/save paths and return. Check buttons stay inside artwork at normal and maximized sizes.
- Import an image, toggle Transparent PNG, save and copy. Confirm no opaque rectangles around buttons.


## Companion 0.6.0
- Open Full-size preview: verify a separate window, whole image in Fit mode, maximize, 100%, zoom, panning and Escape.
- Click one capture, Ctrl-click another: both remain selected and the overview shows the second. Ctrl-click a selected capture to remove it. Shift-click and Ctrl+A select ranges/all.
- Change padding/border/transparent settings with two selected. Select each separately and confirm its style is retained; unselected captures stay unchanged.
- Save a multi-selection, then save again: all selected exports appear with unique filenames. Save to folder chooses a destination. A missing original is reported without discarding other successful exports.
- Run the per-user installer, launch from Start, and run the installer again. Verify settings/captures persist and only one app entry appears in Installed apps.
- Settings → Check for updates: before companion releases exist, expect no newer version. After a newer companion release is published, verify confirmation, download, checksum verification, installer launch and retained settings.
