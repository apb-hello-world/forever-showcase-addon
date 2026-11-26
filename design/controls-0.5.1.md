# Companion 0.5.1 polish

Windows color-key transparency now uses a binary alpha silhouette after resizing the shell. This removes partially transparent exterior pixels that previously composited into black fringes. Artwork source files remain unchanged.

Button captions are rendered with their visible glyph bounds centered inside the button artwork. Gear, minimize, maximize and close use drawn icons with a common square box. The PNG toggle reads Transparent PNG: On/Off. Narrow button sizing now reserves at least one pixel for the center slice.

Verified: 31 automated tests; Tk layout/button/settings/toggle smoke at 1x, 1.2x and 1.6x; binary alpha assertions at three sizes; inspected rendered caption alignment sheet. Companion rebuilt. No desktop screen capture, game changes, or publication. Final Windows desktop appearance awaits user confirmation.
