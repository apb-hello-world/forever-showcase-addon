# Companion 0.6.1

Move the selection hint inside the Finish panel with dark text. Capture rows use alternating warm shading, inset text and larger row spacing. Native input controls are inset into rounded canvas borders with the shared brass border color, including settings paths, Finish fields and dropdowns.

Preview wheel input zooms; scrollbars are computed from image overflow and reserved scrollbar space, avoiding fit/scrollbar feedback loops. Rendering retains the existing image when its size has not changed.

Validation: 35 automated tests passed. Tk smoke checks cover all nine field borders, selection after row styling, settings navigation, no bars for Fit/small images, both bars for overflow, wheel zoom directions and resize stability. Owner requested publication to test the installed 0.6.0 updater. Do not install locally over their baseline before they perform that test.
