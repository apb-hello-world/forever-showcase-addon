# Authoring a real adapter

Start with `examples/ForeverShowcaseExample/Example.lua`. Keep the adapter inside
the participating add-on. Register after its rendering/data modules are ready.
Keep commands out of ordinary help/settings; Showcase alone owns `/showcase`.

1. Audit the real screen's data reads, writes, timers, events, and actions before
   choosing fixtures. If any boundary cannot be isolated, make the scene unavailable.
2. Add a renderer-owned temporary data-provider path. Build fixtures in memory;
   never assign sample tables to real SavedVariables, even temporarily. Suppress
   real writes and gameplay actions in demo mode, including keyboard handlers.
3. Snapshot the ordinary selected page, tabs, selection, shown state, anchors,
   dimensions and scale without deep-copying protected objects. Register a pure
   Lua cleanup to disconnect the demo provider, then appropriate UI restoration.
4. Register cleanup before changing anything. Use the existing real renderer and
   approved artwork. Any geometry/theme overrides must be explicit and reversible.
5. Guard delayed work with `context:Guard` and/or `IsActive`; register cancellation
   for every timer/event. Live non-demo events also need a demo-mode gate so they
   cannot write fixture content into storage. Do not suppress unrelated gameplay.
6. On combat, deactivate demo data immediately through combat-safe cleanup. Leave
   and protected cleanup run after combat. Ensure the still-visible frame is safe
   if it cannot be hidden in combat; disabling a protected control may itself be
   forbidden. Mark unsafe scenes unavailable rather than hoping restoration works.
7. Supply an informative availability reason and concise capture instructions.
   Adapters must not automate screenshots or game input. The player can use
   Showcase Capture; the user closes chat manually.

## Scene-authoring checklist

- [ ] Fixtures never reach SavedVariables, including logout or reload in combat.
- [ ] No creation/deletion of macros, action-slot changes, bindings, inventory,
      quests, guide progress, chat sends, or gameplay actions.
- [ ] All interactive paths respect demo isolation; save/apply actions are safe.
- [ ] Original workspace, geometry and visibility restore where safe.
- [ ] Partial entry and repeated leave/cleanup are safe.
- [ ] Delayed callbacks cannot affect a later session; timers/events are cancelled.
- [ ] Combat-safe cleanup is explicitly identified; protected restoration defers.
- [ ] Unavailable features explain why; optional dependencies are truly optional.
- [ ] Fixtures are deterministic and readable, with no fabricated product controls.
- [ ] User confirms actual native rendering, layout and behavior in-game.

For new UI, consult the Forever UI guide at
`D:/Projects/forever-atlas/design/forever-ui/` and current Hub. README, DESIGN,
AGENTS and NATIVE were consulted for this companion; Hub reported
2.0.0-preview.3, revision
`7ce4ea5b898618c3979a5ff33a620ce205c6e8033588c07eea6b6b76aad29770`.
The owner selected the Stagekeeper mockup on November 25, 2026. Version 0.2.0
adds its native selector with original textures, live text and controls. See
DESIGN.md and design/assets/PROVENANCE.md. The UI shows registered adapters only;
it does not manufacture scenes for addons that have no adapter.

For the optional 0.3.0 clean screenshot backdrop, also read
`D:/Projects/wow-forever-addons/forever-showcase/PRESENTATION-HANDOFF.md`.
The scene toolbar needs no adapter update. API v1 remains compatible.
