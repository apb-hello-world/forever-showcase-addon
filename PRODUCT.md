# Forever Showcase

## Platform and stack
World of Warcraft: Forever native addon, Lua 5.1-compatible code and WoW frames.
Interface 16001. This is not a web, iOS or Android surface.

## Confirmed user and purpose
The owner uses this developer companion to select repeatable real addon scenes
for manual screenshots for CurseForge descriptions, galleries and UI updates.
The original handoff specifies the workflow and boundaries. The owner selected
the Stagekeeper mockup on November 25, 2026 and requested a UI implementation.

## Workflow and constraints
Select a registered addon, inspect and activate a scene, hide companion controls,
capture manually, then stop and restore. One active scene globally. Actual addons
own rendering and isolated sample data. Never modify Spellwright in this project.
No gameplay actions, real-data replacement, automatic game input, or publication.
Combat invalidates sessions and defers protected restoration. No persisted session.

## Evidence
Approved concept: design/mockups/stagekeeper-v1.png. API v1 and executable
nonvisual example already exist. Real adapters and native visual approval remain
pending. UI must show only registered integrations, not imagined Spellwright data.

## Approved extension — 0.4.0
The same Stagekeeper artwork now supports an optional Windows desktop companion
(Tkinter/Pillow, packaged as a portable executable folder). The player can draw or
fit a reusable crop area, request a WoW screenshot, inspect recent capture
metadata and a crop diagram, and Send & reload. The desktop app reads the sent
instructions and screenshot files, offers Original/Crop/Styled previews, and
saves or copies separate images. It does not control WoW or publish images.
Manual screenshot capture remains available without the desktop app.

Only crop settings and capture records persist in the addon; sessions do not.
This extends the original manual-only workflow above. The original evidence
paragraph describes the initial handoff: the owner has since confirmed the
existing Spellwright scene. New in-game capture controls, framing and timing
still await owner validation. Desktop evidence and remaining limits are tracked
in design/capture-companion-0.4.0.md.
