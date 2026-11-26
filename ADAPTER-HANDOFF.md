# Forever Showcase integration handoff

Copy the task below to the agent working in the participating addon's canonical repository.

## Task

Implement and validate an optional Forever Showcase adapter for this addon so its actual UI can be staged for repeatable CurseForge description and media-gallery screenshots. Keep this work inside this addon's repository and preserve its approved artwork, normal behavior and saved settings.

### Read first

Use the Forever UI Hub MCP tools to resolve the current framework and read AGENTS.md and NATIVE.md, especially the required Showcase integration section. Record the revision adopted. This handoff was prepared against Hub revision `ae5033f3ced9d83000bb1f2ec375f0751eb80d660ab699390c41b9c7281651c9`.

Canonical Showcase source: `D:/Projects/wow-forever-addons/forever-showcase`.
Public repository: https://github.com/apb-hello-world/forever-showcase-addon.
Read API.md, INTEGRATION.md, PRESENTATION-HANDOFF.md, CAPTURE-WORKFLOW.md and the registration pattern in examples/ForeverShowcaseExample/Example.lua. The example is a nonvisual lifecycle fixture; do not install it or use it as a screenshot renderer.

Baseline: WoW addon 0.5.2, registration API v1, optional Windows companion 0.7.2. API and application versions are distinct. Verify current owning source if those versions have advanced.

### Implement

1. Audit the addon's real UI, data reads/writes, events, timers, custom widgets and gameplay actions. Start with a representative main scene, then cover meaningful screenshot-worthy features that can be isolated safely. Document unavailable features with actionable reasons rather than fabricating screens.
2. Keep the adapter in this addon, loaded after its renderer dependencies. Append ForeverShowcase to existing OptionalDeps. Register immediately when available and on ADDON_LOADED for ForeverShowcase; keep a local success flag. Use `ForeverShowcase:Register(1, definition)`. Ordinary operation must work unchanged without Showcase or the desktop companion.
3. Use a stable lowercase addon id and human-readable addon title. Each scene needs a stable id, readable title, description, suggested caption, concise capture instructions, pure synchronous available callback, and synchronous enter/leave callbacks. IDs match `^[a-z][a-z0-9_-]*$`. Do not register twice or modify the Showcase contract/catalog.
4. Render through the real addon UI with deterministic, isolated in-memory fixtures. Never put fixtures in SavedVariables, even temporarily. Gate all live events, background writes, keyboard handlers and save/apply actions. No macro, binding, action-slot, inventory, transaction, quest, guide-progress or chat changes. Use safe read-only interactions or tested input shields when necessary.
5. Register cleanup before mutation. Restore prior page/tab, selection, scroll, visibility, anchors, size and scale. Use the actual custom widgets' methods, not assumed ScrollFrame APIs. Leave must tolerate partial entry and repeated cleanup. Guard delayed callbacks and separately cancel timers/unregister events. Disconnect demo data with `context:AddCleanup(disconnect, false)` only when that operation is combat-safe; protected restoration remains deferred. Never depend on logout/reload cleanup to protect real data.
6. At the end of each entry, after all scene roots, popups and input shields exist and restoration is registered, opt into presentation where safe:

```lua
if context.SetPresentation then
    context:SetPresentation({
        frames = { actualAddonOwnedSceneRoot },
        background = { 0.09, 0.07, 0.06 }, -- choose a color fitting this addon
    })
end
```

Use actual frame objects. Include separate top-level scene windows not descended from a registered root; never include UIParent, WorldFrame, Blizzard/shared frames or another addon's UI. Keep the registered tree stable during presentation. This supports clean backdrops and Auto-fit area. Document any unsafe presentation limitation instead of changing unrelated UI.

### Capture and desktop responsibilities

Showcase owns `/showcase`, scene discovery, the compact scene picker, toolbar navigation, Stop, backdrops, Draw area, Auto-fit area, Capture and the captures list. Users should not need extra slash commands or addon-specific demo controls. Keep comparable scenes consistently positioned/sized so a remembered crop rectangle remains useful.

The user opens `/showcase`, starts a scene, chooses a backdrop and capture rectangle, then clicks Capture. Captures are named from the scene title. Captures > Send & reload stops the scene and flushes capture metadata for the optional desktop companion. Manual screenshots remain supported without the companion. Do not automate screenshots, reloads or game input.

The registered addon title automatically becomes addonTitle in new capture records. The companion uses it for `<base folder>/<addon name>/<optional subfolder>/`; older records fall back to addon id. The desktop handles cropping, styles, batch selection, full-size preview, PNG/JPEG/WebP, proportional resizing including an 850-pixel preset, repeated exports and unique filenames. Subfolders such as large or thumbnails belong to the desktop Export dialog. Do not add capture-record writes, export paths, format controls or desktop communication to the adapter.

### Verify and deliver

Run meaningful lifecycle/isolation tests using mocks that match the real widgets. Cover Showcase absent, load order/late registration, availability failures, repeated entry, scene switches, partial entry failure, stale callbacks, cleanup errors, Stop, reload and combat. No sample content may persist. On combat the scene stops, combat-safe data disconnection runs immediately, protected restoration waits, and the scene does not auto-resume.

Back up before local installation, install only this addon's intended runtime files, and preserve SavedVariables and sibling addons. Have the owner perform native checks; never send game input. Check scene roots/input shields, backdrop colors and Off, Auto-fit and manual crop, capture/Send & reload, scene switching, Stop restoration, combat and normal operation without Showcase. Passing mocks are not proof of native appearance.

Deliver a list of scene IDs with screenshot purposes/captions, changed files, test results, backup/install status, API/runtime compatibility and reviewed Hub revision. Separate implemented, automated, installed and owner-confirmed status. Give the owner a short in-game checklist. Do not publish this addon or modify Showcase/sibling addons unless separately authorized.
