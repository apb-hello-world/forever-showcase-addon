# Controls revision 0.5.0

Implemented named, per-scene captures with row deletion and an all-captures filter. Replaced the diagram gallery with a compact working window. Added a separate current-addon scene picker; selection is inert until Start scene. Renamed Fit windows to Auto-fit area. Adapter contract remains API v1; companion manifest accepts optional capture names and remains compatible with older records.

The Tkinter companion keeps Stagekeeper artwork, uses Windows color-key transparency outside it, and draws buttons directly on the canvas. Custom settings/minimize/maximize/close controls replace the title bar. The gear opens folder settings in the right panel. Button positions move clear of artwork borders; Transparent PNG is a canvas toggle. Exports use capture names.

Validation: 31 automated tests passed; Tk smoke exercised layout, custom chrome, settings save/return, transparency toggle, maximize/restore and close. Read-only finish review findings were corrected (drag bounds, stale deleted title, export naming, picker selection). Built portable desktop executable and packaged addon. Installed 11 addon files with backup and SHA256 verification; see installation-0.5.0.json. No desktop capture session was used. Visual appearance, taskbar restore and native WoW behavior await user testing. No publication or sibling addon changes.
