---
name: Forever Showcase — Stagekeeper
description: A native theater cue board for manual addon screenshots.
colors:
  ivory-text: "rgb(98% 93% 79%)"
  dark-ink: "rgb(20% 12% 7%)"
  backdrop-default: "rgb(9% 7% 6%)"
  backdrop-charcoal: "rgb(5.5% 5.5% 6.5%)"
  backdrop-ivory: "rgb(94% 88% 76%)"
  backdrop-green: "rgb(0% 100% 0%)"
typography:
  title:
    fontFamily: "Fonts/FRIZQT__.TTF"
    fontSize: "24"
  heading:
    fontFamily: "Fonts/FRIZQT__.TTF"
    fontSize: "18"
  body:
    fontFamily: "Fonts/FRIZQT__.TTF"
    fontSize: "14"
  label:
    fontFamily: "Fonts/FRIZQT__.TTF"
    fontSize: "12"
spacing:
  row-gap: "8"
  action-gap: "8"
components:
  action-button:
    textColor: "{colors.ivory-text}"
    height: "36"
  toolbar-button:
    textColor: "{colors.ivory-text}"
    height: "32"
  list-row:
    height: "48"
  pager-button:
    width: "52"
    height: "28"
---

# Design System: Forever Showcase — Stagekeeper

## Overview

**Creative North Star: "Stagekeeper"**

The owner selected concept A on November 25, 2026: a theater cue board with dark walnut, oxblood velvet, brass, and quiet ivory working surfaces. The approved reference is `design/mockups/stagekeeper-v1.png`. Original generated artwork supplies material character; live WoW text and frames supply the working interface.

This records `ForeverShowcase/Theme.lua`, `ForeverShowcase/UI.lua` and `ForeverShowcase/Presentation.lua` through runtime 0.3.0, merging the provisional design seed. It is a native WoW Lua surface. All geometry and type sizes use native UI units before root scaling; frontmatter color strings represent normalized Lua RGB values. The reference is approved; the owner approved the overall 0.2.0 window appearance. The replacement 0.2.1 wordmark remains unchanged and still needs native review. The owner confirmed the existing Spellwright scene works; the 0.3.0 toolbar and backdrop need separate native validation. Automated frame tests do not substitute for an in-game screenshot.

**Key Characteristics:**

- Material artwork surrounding readable working surfaces.
- Live typography and controls with immediate state changes.
- A stable three-column composition that scales as one window.

## Colors

Walnut, velvet and brass are texture materials, not flat color tokens. Original artwork lives in `design/assets`; runtime textures are `ForeverShowcase/Media/StagekeeperShell` and `StagekeeperButton`.

### Primary

Oxblood and brass button artwork supplies actions and selected-row treatment. No flat swatch is asserted for this multicolor texture.

### Neutral

- **Ivory text:** titles, dark-surface labels, button labels, selected and hovered rows.
- **Dark ink:** detail text, scene pager counter and unselected scene rows.
- **Backdrop colors:** opaque capture surfaces use the frontmatter default, charcoal, ivory and green tokens. Scene mode accepts adapter RGB; the default applies when its RGB is omitted. These are temporary presentation surfaces, not a change to Stagekeeper materials.

**The Live Content Rule.** Keep labels, headings and controls out of the shell artwork; render them as native frames and font strings.

## Typography

All roles use the shipped FRIZQT font path in frontmatter, empty font flags, no configured fallback and transparent shadows with zero offset. No CSS font-weight or line-height is implemented. A separate original gold wordmark texture serves the title plaque; title serves scene headings; heading serves column labels; body serves details, status, list rows and actions; label serves pagers, hints, notices and footer guidance.

Detail text adds five units of line spacing. Labels align left/top by default; button labels center/middle. Buttons of height 28 or less use label size; taller buttons use body size. Scene titles longer than 55 Lua string bytes also appear in the scrolling body.

## Layout

The root is a 1000 × 760 native frame at DIALOG strata, initially centered, mouse-enabled, top-level and clamped to screen. Scale is `max(0.1, min(1, (viewportWidth-40)/1000, (viewportHeight-40)/760))`. There are no breakpoints or column reflows. Opening and visible display/scale changes recalculate scale. Position is session-only.

Coordinates below are top-left offsets in unscaled native units:

| Element | x, y | Width × height |
| --- | --- | --- |
| Wordmark canvas | 300, 42 | 400 × 100 |
| Header drag target | 270, 45 | 470 × 85 |
| Addon rows | 51, 201 | 178 × 48 |
| Scene rows | 260, 201 | 194 × 48 |
| Addon pager | 54, 566 | 174 × 28 |
| Scene pager | 266, 566 | 182 × 28 |
| Scene heading | 506, 180 | 414 × 64 |
| Detail viewport | 506, 252 | 412 × 290 |
| Scroll hint | 506, 550 | 410 × 24 |
| Error notice | 506, 576 | 410 × 26 |
| Status | 52, 641 | 270 × 57 |
| Start / Next / Hide / Stop | 340 / 492 / 630 / 788, 652 | 144 / 130 / 150 / 150 × 36 |

Each list shows six rows at a 56-unit pitch. Pagers appear only with more than one page. Detail text is 410 units wide; measured height determines the scroll range. Mouse-wheel scrolling moves 40 units per step and is clamped. Changing selection resets scrolling. Footer guidance is centered at 80, 721 in an 840 × 18 region.

## Elevation & Depth

Depth comes from shell and brass button artwork. No procedural shadows or animated elevation are implemented. Native top-level raising keeps the window in front; header dragging raises it before moving. Selector components descend from the selector root. During a scene, the selector deliberately moves to TOOLTIP strata at level 200, restoring its original layering afterward. The separate capture toolbar is a top-level TOOLTIP root at level 100 so scene click-to-raise cannot cover recovery controls. This is a deliberate capture overlay, not independent raising of unrelated addon children. The optional opaque backdrop uses FULLSCREEN strata at level 0. Explicit adapter roots and their snapshotted descendants temporarily use FULLSCREEN_DIALOG, with levels normalized to 100 plus their original offset from the tree minimum. Relative level differences are preserved; original strata and levels restore when the backdrop is turned off or the scene ends.

## Shapes

Artwork defines decorative silhouettes and brass corners; no numeric radius token exists. Buttons use three horizontal source slices: x ranges 0–48, 48–464 and 464–512, normalized over 512. Caps occupy `min(16, width/2)` units each; the center stretches. Text insets are ten units horizontally and five vertically.

## Components

### Buttons and rows

Brass-and-velvet controls use immediate multiplicative brightness: default 0.80, hover or selected 1.00, pressed 0.65, disabled 0.45. Disabled light text uses alpha 0.65. Hiding clears pressed and hover state. No animated transition or custom keyboard focus treatment is implemented.

Unselected, unhovered rows hide their button texture. Addon rows retain ivory text over the dark column; scene rows use dark ink over ivory. Selected or hovered rows show texture and ivory text. Unavailable scenes remain selectable to expose their explanation but cannot activate. Native tooltips reveal full titles and unavailable reasons.

### Detail and status surfaces

Details show description, suggested caption and capture notes, preceded by an availability explanation when needed. A hint appears only for scroll overflow. Empty registries show integration guidance rather than invented scenes. Status distinguishes active, idle, combat, deferred restoration and cleanup failure. Errors also have a separate notice region.

### Window controls

Selection previews metadata; Start scene activates it. The label becomes Restart scene for the active selection. Next scene follows the active session and updates selection after success. Hide controls, X and Escape preserve the scene. Stop scene restores the workspace. `/showcase` reopens and focuses the active scene. Capture remains manual.

Activation and Next are disabled during combat, pending restoration or cleanup failure; Stop requires an active scene. Visible status changes are checked every quarter-second, with availability refreshed at least once per second. No persisted preferences or sessions are introduced.

### Scene toolbar — 0.3.0

Starting a scene hides the selector and shows an 880 × 100 toolbar centered 20 units below the top of UIParent. Its scale is `max(0.1, min(1, (viewportWidth-24)/880))`; it is movable and clamped. The approved shell's wood action strip supplies its background through texture coordinates `(0.025, 0.975, 0.822, 0.932)`. No new skin or wordmark is introduced.

The live title is at 16, 8 with size 848 × 22 and body typography. The header drag region is at 8, 2 with size 864 × 27. Buttons sit at y32 with toolbar-button height, separated by six units. The note is at 16, 72 with size 848 × 20 and label typography.

| Control | x | Width |
| --- | --- | --- |
| Previous | 16 | 92 |
| Next | 114 | 76 |
| Restart | 196 | 86 |
| Stop scene | 288 | 100 |
| Scene list | 394 | 100 |
| Backdrop | 500 | 166 |
| Hide for 10s / Close toolbar | 672 | 192 |

Previous and Next wrap within the active addon, skipping unavailable scenes; a single available scene restarts. Scene list reopens the selector. Hide for 10s hides both control surfaces and tooltips, leaves the scene and backdrop active, and automatically restores the toolbar after ten seconds. It becomes Close toolbar when inactive or not ready; that action simply hides the toolbar. Navigation, restart and stop require a ready session. No automatic screenshot capture or gameplay input is added.

### Optional capture backdrop — 0.3.0

The Backdrop button cycles Off, Scene, Charcoal, Ivory and Green. It is disabled unless the active adapter opts in with `context:SetPresentation({frames=..., background=...})`; a visible note explains missing registration. API v1 remains compatible with existing adapters. Mode is remembered only in memory across scenes, with Scene resolving each adapter's color.

The backdrop fills UIParent and consumes mouse input to prevent clicks through to the world. It does not hide UIParent or promise to suppress unrelated high-strata windows or tooltips. Only explicitly registered adapter-owned frame trees are layered above it. Trees are snapshotted before backdrop activation and must remain stable while enabled. On combat the backdrop disappears immediately; protected scene-layer restoration waits until combat ends. Stop, switch, failed entry and reload must not leave a capture backdrop covering ordinary gameplay. Restoration failure blocks new sessions through the existing fault mechanism. Native toolbar layout, backdrop composition and restoration still require in-game validation; see `PRESENTATION-HANDOFF.md`.
## Do's and Don'ts

### Do:

- **Do** preserve Stagekeeper's approved material identity and live native text.
- **Do** preserve three-slice caps and implemented interaction feedback.
- **Do** inspect the native window in-game before claiming visual approval.

### Don't:

- **Don't** invent flat texture tokens, CSS, breakpoints or motion absent from the Lua.
- **Don't** equate hiding controls with stopping and restoring a scene.

Forever UI native guidance was reviewed during implementation at Hub revision `7ce4ea5b898618c3979a5ff33a620ce205c6e8033588c07eea6b6b76aad29770`. Buttons adapt its three-slice geometry and states with original Stagekeeper artwork. The owner confirmed the existing Spellwright scene works. Native validation of the 0.3.0 toolbar and opt-in backdrop remains pending.

## Wordmark update — 0.2.1

The owner requested a stylized title after approving the Stagekeeper window.
StagekeeperWordmark is a 1024x256 transparent texture displayed at 400x100, with
identical aspect ratio. Its visible lettering is centered within the existing
plaque; the shell and interaction geometry are unchanged. No live font title is
drawn beneath it. Source and exact prompt: design/assets/PROVENANCE.md.


## Capture companion extension — 0.4.0

The owner requested capture framing and an optional Windows finishing workspace
in the approved Stagekeeper world. The original shell, button and wordmark assets
remain authoritative. This is an additive surface record, not a token refresh:
frontmatter and `.impeccable/design.json` remain the incumbent native 0.3.0
baseline. Historical component descriptions above retain their version scope.
Exact 0.4.0 geometry, desktop typography, states and evidence are recorded in
[the capture companion surface note](design/capture-companion-0.4.0.md).

The toolbar now has a second capture row and is 880 × 140 native units. Recent
captures reuse the 1000 × 760 shell, with metadata and a bounded crop diagram;
they do not display saved screenshot pixels in WoW. The desktop workspace uses
the same shell composition and artwork, with live Segoe UI text and native Tk
controls. Its finishing presets change exported images, not the Stagekeeper UI.
No shared colors, native type roles, material assets or global tokens change.

Capture is explicitly player-requested: controls hide, WoW writes a full-screen
screenshot, and the optional desktop companion later creates separate exports.
Crop areas and capture metadata persist; active scene sessions still do not.
Native desktop screenshots support the populated and minimum-size unselected
states. Native game framing, screenshot timing and pixel alignment remain
unverified. The existing overall-window approval does not imply approval of
these new game controls.
