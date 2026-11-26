# Handoff to the Spellwright agent

The companion and API v1 are implemented at
`D:/Projects/wow-forever-addons/forever-showcase`.
Spellwright has not been modified. No real screenshot adapters exist yet.

Read `API.md` for the exact tested contract, `INTEGRATION.md` for safety obligations,
and `examples/ForeverShowcaseExample/Example.lua` for executable registration.
Runtime implementation: `ForeverShowcase/Core.lua` and `Commands.lua`.
Lifecycle tests: `tests/test_lifecycle.py`. Manual checks: `MANUAL-TESTS.md`.

Add an optional adapter module to Spellwright's canonical checkout, load after
the modules it uses, append `ForeverShowcase` to OptionalDeps, and use both immediate
registration and the ADDON_LOADED fallback shown in the example:

```lua
local ok, reason = ForeverShowcase:Register(1, {
    id = "spellwright", title = "Spellwright",
    scenes = { -- supply actual callbacks, not these illustrative placeholders
        { id = "editor", title = "Editor", enter = EnterEditor, leave = LeaveEditor,
          available = EditorAvailable, instructions = "Close chat and capture manually." },
    },
})
```

Inside enter: `context:AddCleanup(restoreProtectedWorkspace)` before changes;
`context:AddCleanup(disconnectDemoData, false)` for combat-safe pure Lua cleanup;
wrap delayed callbacks using `context:Guard(callback)` and cancel their timers.
Use `context:IsActive()` to gate other event paths. Leave receives `(context, reason)`
and must tolerate partial entry. Never rely on leave to disconnect sample storage
during combat: leave is deferred until combat ends.

Planned scene IDs: `editor` (folders/tabs/script/snippets/reference/output), `menus`
(enemy chooser), `smartcast` (backing-bar preview without slot writes), `quickfixes`
(suggestion and Apply dialog), `templates` (categories and preview), `appearance`
(existing theme/palette/font preview). Implement only scenes whose existing screens
can safely consume isolated fixtures. Mark others unavailable with reasons.

Activation: `/showcase spellwright editor`; discovery: `/showcase list`; cycle:
`/showcase next`; restore: `/showcase off`; captions/instructions: `/showcase info`.
`/showcase` opens the Stagekeeper selector in 0.2.0. Hide controls, Escape or close
leave the active scene running; Stop scene restores it. Close chat for capture.

Known limits: no sandbox for adapter code; no real renderer
in the synthetic example; no persisted sessions; cleanup errors require reload;
protected restoration waits for combat and is discarded by reload. Only mocked
Lua 5.1 lifecycle and mocked selector behavior are automatically verified. See
INSTALLATION.md for local installation status. The owner approved the overall 0.2.0 selector appearance. Adapter safety and
combat behavior still require native validation; the 0.2.1 wordmark also awaits review. API v1 has not changed.

For the optional 0.3.0 clean screenshot backdrop, also read
`D:/Projects/wow-forever-addons/forever-showcase/PRESENTATION-HANDOFF.md`.
The scene toolbar needs no adapter update. API v1 remains compatible.
