# Companion 0.6.4 preview performance

Render only the visible image area plus a 96-pixel surrounding margin instead of resizing and uploading the full zoomed image. Crop before resampling to bound Pillow alpha-conversion and filtering work. Zoom input coalesces into a scheduled frame; panning and scrollbar movements schedule viewport redraws. Preserve the image position around the viewport center when zoom changes. Preview zoom up to 400% no longer allocates a full zoomed bitmap. Export images remain unchanged.

Evidence: 40 tests passed, including exact 100% crops, comparison with full-image resampling and viewport allocation bounds. Local 3840x2160 RGBA benchmark at 200%: full-image resize 530.8ms, 1280x800 viewport median 16.4ms (five samples). Native Tk smoke checked rapid zoom coalescing, bounded bitmap dimensions at 400%, panning through image edges, 100% and Fit restoration. Timing is machine-specific and excludes export rendering. No desktop screen capture or game input.
