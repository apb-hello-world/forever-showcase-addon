# Companion 0.6.3 selection stability

Reproduced selection loss through actual Tk events: ButtonPress selected a row, then a one-pixel B1-Motion cleared the selected IDs. The application overrides Listbox button press, so the native class drag handler did not receive its expected initialization and used a stale anchor.

Suppress native motion/leave/enter/release selection handlers on this list only. The custom click handler remains the pointer-selection owner, explicitly sets focus and anchor, and preserves plain, Ctrl and Shift click behavior. Keyboard and wheel class bindings remain available.

Validation: 37 tests passed, including two new Windows Tk integration regressions using generated pointer events. Repeated clicks with held-button jitter preserve selection; Ctrl-add/remove, Shift ranges and refresh preserve intended selections. No desktop capture or game input was used.
