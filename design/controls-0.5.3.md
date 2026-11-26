# Companion 0.5.3 minimize recovery

Removed override-redirect window mode. The companion now keeps a managed Tk top-level, strips only the native caption/resize frame, and retains APPWINDOW plus system/minimize/maximize styles. Minimize uses Tk iconify so Tk and Windows agree on the window state. Map events reapply the frameless styling after restoration; the code no longer hides and shows the window during style changes.

Validation: three real Tk/Win32 minimize and SC_RESTORE cycles, asserting iconic/normal states, APPWINDOW without TOOLWINDOW, no caption/resize frame, unchanged geometry, visible/enabled restoration and settings actions after each cycle. All 31 existing tests passed. Portable companion rebuilt. No desktop screen capture or game changes. Taskbar appearance and mouse restoration await user confirmation.
