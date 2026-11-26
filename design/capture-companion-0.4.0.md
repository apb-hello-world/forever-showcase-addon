# Capture companion — 0.4.0 surface and evidence note

Date: 2026-11-25. Ordinary extension of the owner-approved Stagekeeper world.
No redesign, shared token changes, replacement artwork or publication.

## Authority and scope

DESIGN.md frontmatter and the incumbent .impeccable/design.json retain the native
system baseline. StagekeeperShell, StagekeeperButton and StagekeeperWordmark are
reused unchanged. Desktop PNG sources are in design/assets; native TGA assets
remain in ForeverShowcase/Media. Desktop controls and export-image styling below
are surface-specific implementation facts, not newly approved global tokens.

Sources inspected: ForeverShowcase/Capture.lua, CaptureUI.lua, Presentation.lua,
companion/app.py, companion/model.py, CAPTURE-WORKFLOW.md, PRODUCT.md, DESIGN.md,
.impeccable/design.json and design/installation-0.4.0.json.

## Native capture surfaces

The toolbar preserves its existing first row, shell crop and top anchor. Its
height increases from 100 to 140 units. Draw area, Fit windows, Capture and
Captures occupy a second row at y 72, x 16/172/328/484; each is 150 × 30 units.
The status note moves to x 16, y 110, width 848, height 20. Scaling remains based
on the 880-unit toolbar width.

Draw area covers UIParent at TOOLTIP level 400. Four translucent black mask
regions surround a one-unit gold outline; the live dimension label is at 40,40.
Dragging stores a physical-pixel crop per addon. Right-click or Escape cancels.
Live framing is explicitly labeled as a live guide, not a saved image. Fit
windows derives bounds from registered visible presentation roots with 16 pixels
of space. No desktop app is required for either route.

Recent captures reuse the 1000 × 760 shell and 400 × 100 wordmark at 300,42.
The window is TOOLTIP level 300, draggable and clamped, scaled to fit with 24 units
of viewport margin. Six rows at x 54, y 210 use a 52-unit pitch. Metadata is at
270,210 in a 175 × 350 region. The crop diagram starts at 506,300 and fits both
axes within 400 × 220, preserving the screen aspect ratio. It shows screen/crop
rectangles only; actual pixel previews belong to the desktop app. Empty state
explains Start scene → Draw area → Capture. The footer exposes Live framing,
Remove record and Send & reload. Removing deletes metadata only. Send stops and
restores the scene before marking records sent and reloading.

Capture hides controls and guide, waits at least two frames and 0.25 seconds,
and requests WoW's full-screen Screenshot. Success triggers a short 0.22-second
flash; failure restores controls and reports an error. A 10-second timeout blocks
further capture until reload. Combat or scene changes before the request cancel
it; changes after the request flag the resulting record for review. A changed
resolution requires reframing. The record limit is 200. These are implemented
behaviors; real-client timing and pixel alignment are not yet proven.

## Desktop composition and interaction

The window starts at 1200 × 912 client pixels and has a 1000 × 760 client minimum.
The 1000 × 760 design canvas scales uniformly by min(width/1000,height/760), with
centered letterboxing and no column reflow. The wordmark retains 300,42 and
400 × 100 geometry. All coordinates below are unscaled canvas units.

| Region | Geometry |
| --- | --- |
| Capture list | 55,206; 172 × 285 |
| Preset selector | 272,236; 166 × 28 |
| Numeric style controls | x 380, y 285/328/371/414; 58 × 28 |
| Preview heading | 507,190; width 405 |
| Original/Crop/Styled selector | 507,280; 130 × 27 |
| Image preview | centered 709,435; bounded 405 × 235 |
| Dimensions | 507,565; width 405 |
| Choose original | 507,583; 188 × 28 |
| Status | 55,657; width 390 |
| Save / Save as / Copy image | x 505/635/783, y 658; widths 122/140/145, height 36 |

Desktop text is live Segoe UI, with nominal 19-pixel preview title,16-pixel column
headings,12-pixel body/control text and 11-pixel hints. Text scales with the canvas,
with a 10-pixel floor. Native comboboxes, spinboxes, file dialogs and keyboard focus
remain visible. Buttons reuse three-slice artwork with 16-unit caps, brightness
0.85 at rest and 1.0 on hover, plus a keyboard-focus outline. Native Lua button
brightness and FRIZQT roles remain unchanged.

The desktop's local ink/ivory/paper/wood values are #362313/#f9ebcc/#ebd8af/#28190f.
They are recorded as observed surface values, not substituted for native tokens.
No new artwork or shared palette was introduced. Style controls change image
padding, radius, border, shadow, colors and PNG transparency. Stagekeeper, Clean,
Gallery ivory and Transparent presets are available; named local presets persist.
The Stagekeeper export starts with 32px padding,16px radius,2px border and 12px
shadow. These export values do not define UI component geometry.

| State | Visible result and action availability |
| --- | --- |
| No selection / empty preview | Capture workflow guidance; export actions disabled |
| Preparing | Preparing preview message; export actions disabled |
| Missing or ambiguous original | Choose original instruction with matching status; export actions disabled |
| Render failure | Preview unavailable plus specific error; export actions disabled |
| Ready | Selected preview mode, full-resolution dimensions; export actions enabled |
| Save success | Saved path appears in status |
| Copy success | Status confirms copy and white transparency flattening |

Original/Crop/Styled select the actual full-resolution export, not just a visual
preview. Save creates a unique PNG; Save as offers PNG/JPEG. PNG preserves alpha;
JPEG and Windows DIB clipboard output flatten transparency onto white. Known
original files and the screenshot directory are protected from export overwrite.
Folder setup and manual import remain local. Conservative timestamp/dimension
matching can require Choose original; no newest-file fallback is used.

## Evidence and disposition

- Inspected .impeccable/review/companion-desktop.png: populated 1202 × 944 outer
  window, synthetic fixture visibly labeled, styled preview and Copy success.
- Inspected .impeccable/review/companion-empty.png: minimum 1002 × 792 outer window,
  unselected preview guidance and disabled export actions. A record exists in the
  list: this is an unselected-state capture, not evidence of a zero-record list.
- Excluded companion-minimum.png: HDRSnip overlay invalidates it as app evidence.
- Review disposition supplied by the implementation/review handoff: ship limited
  to two fixes, both resolved. Source inspection confirms the 400 × 220 diagram
  bound and distinct loading/error/missing-preview text.
- Implementation handoff reports 30 automated tests passing, native desktop Save
  and Copy verified, and the portable executable folder packaged. This document
  pass did not rerun tests or independently repeat those native actions.
- Save As dialog opening was verified; completion remains unverified because
  tool interference/global HDRSnip shortcut interrupted the check.
- Installation receipt records 0.4.0 and 11 hash-verified installed runtime files.
  The receipt was inspected; this document pass did not rehash the game directory.
- Native game capture/framing timing, pixel alignment, combat restoration and new
  control appearance await the owner's game test. Desktop synthetic fixtures and
  mocked-frame tests cannot establish those outcomes. No publishing or GitHub work.

## Existing baseline differences retained

The root design document and sidecar describe native 0.3.0 toolbar geometry,
manual capture and no saved preferences; the versioned extension above records
0.4.0's added height and metadata persistence. PRODUCT.md's initial evidence was
also historical. Desktop Segoe UI, local colors and native widgets are a platform
adaptation, not grounds to rewrite the approved native token system. The
preexisting 0.2.1 wordmark native-review caveat and 0.3.0 backdrop-review caveat
remain. No unrelated visual drift was repaired in this documentation pass.


Final receipt: design/validation-0.4.0.json records 30 tests, 11 installed files,
no installed Example, packaged launch/import/preview/minimum-size/Save/Copy checks,
and a ship disposition with both listed fixes resolved. Paste into the owner's
editor remains pending alongside Save As completion and real WoW alignment.

