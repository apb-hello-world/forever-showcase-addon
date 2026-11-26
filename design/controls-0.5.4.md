# Companion 0.5.4 dragging

Position-only Configure events no longer schedule layout and image recreation. Windows dragging moves the existing native surface via SetWindowPos with NOSIZE, NOZORDER and NOACTIVATE, and services pending idle paint work without nested input dispatch. Real resize layout retains old image references until replacement images are assigned.

Validation: 40 native position changes retained image handles and dimensions with zero layout rebuilds; final native coordinates verified. Minimize/system restore and maximize/restore still work, and actual size changes trigger layout. All 31 automated tests passed. Companion rebuilt. No desktop screen capture used; user confirmation of visible dragging behavior remains pending.
