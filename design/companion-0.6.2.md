# Companion 0.6.2

Remove the native Listbox selection bevel and dotted active outline. Keep the flat burgundy selection and alternating warm row backgrounds. Capture labels are measured against the actual available width, with right padding and ellipsis, and recomputed when the list is resized. Full record names are retained for preview and export. No artwork or window sizing changes.

Validation: 35 automated tests passed. Native Tk checks verified zero selection-border width, every label fitting its row at 1000x760 and 1200x912, Ctrl-click multi-selection, and unchanged full capture names.
