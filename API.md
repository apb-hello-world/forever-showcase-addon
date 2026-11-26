# Forever Showcase API v1

Global: `ForeverShowcase`. Runtime version: `VERSION = "0.6.4"`.
Contract version: `API_VERSION = 1`. Lifecycle methods use Lua colon syntax;
`ForeverShowcase.Report(message)` is a dot-call logging helper. API v1 is the
integration target after the automated lifecycle tests; native validation remains
pending. Incompatible contract changes require a new API version.

## Registration

```lua
local ok, reason = ForeverShowcase:Register(1, {
    id = "myaddon", title = "My Add-on",
    scenes = {
        {
            id = "editor", title = "Editor",
            description = "What this demonstrates",
            caption = "Suggested gallery caption",
            instructions = "Close chat, then capture manually.",
            available = function() return true end,
            enter = function(context) end,
            leave = function(context, reason) end,
        },
    },
})
```

Identifiers match `^[a-z][a-z0-9_-]*$`. Title, enter and leave are required;
other metadata and available are optional. Metadata is string-valued. Scenes
are a dense ordered array, with at least one item and unique scene IDs. Add-on
IDs cannot be registered twice; replacement/unregistration is not supported.
Registration validates the whole definition before storing it and copies the
accepted fields. Callback closures remain the adapter's responsibility.

`available()` must be pure, synchronous and return `true` or `false, reason`.
It may run for listing, activation, or cycling. Errors mean unavailable. Recheck
dependencies here; do not enter a scene to discover whether it is safe.

`enter(context)` is synchronous. Throwing or returning exactly `false` fails
entry and invokes leave plus cleanup. Nil is a successful return. Register
restoration before the first mutation. Entry cannot recursively start/stop scenes.
This also applies to leave and cleanup. Never yield from lifecycle callbacks.

`leave(context, reason)` always runs out of combat, even after partial entry.
Reasons are `off`, `switch`, `entry-failed`, `callback-error`, `combat`, `logout`,
or a caller-supplied Stop reason. Leave must be idempotent and tolerate entry that
failed before creating any UI. Leave runs before remaining cleanup callbacks.

## Session context

- `context.addonID`, `context.sceneID`: identifying metadata; treat as read-only.
- `context:IsActive()`: true only for the current live session and outside combat.
- `context:AddCleanup(fn, protected)`: registers `fn(reason)`, executed once in
  reverse registration order. Protected defaults to true; explicitly pass false
  only for work safe during combat (e.g. pure Lua state or cancelling a timer).
  Registration on a stopped session errors. Cleanup itself must be idempotent.
- `context:Guard(fn)`: returns a callback that does nothing for an old/stopped
  session or during combat. Active execution returns `ok, firstResult`; errors
  are reported and stop the session. During entry, such an error fails entry.
  Guard is not a timer and does not cancel events. Cancel/unregister separately.

All guards become inactive **before** leave/cleanup. In combat, combat-safe
callbacks run first (reverse order within that subset); after combat, leave then
remaining protected callbacks run. Do not rely on ordering across these subsets.
Adapters should disconnect their demo data source with combat-safe cleanup and
defer protected frame restoration. Never use Guard for deferred restoration:
restoration must execute after the session is inactive.

Any leave/cleanup error latches a failure, continues other cleanup, and prevents
new activations until reload. Failed callbacks are not automatically retried.
This prevents layering a new scene over a potentially unrestored workspace.

## Companion methods

- `Start(addonID, sceneID) -> ok, instructionsOrReason`: validates destination
  before leaving the current scene, then enters a fresh session. Repeating the
  current scene fully leaves and re-enters it. A failed new entry does not resume
  the previous scene.
- `Stop(reason?) -> ok, message?`: idempotently stops; pending combat restoration
  counts as accepted. Cleanup failure returns false.
- `Next() -> ok, message`: advances within the active integration in declared order,
  skipping unavailable scenes. Stops at the last available scene without wrapping
  or restarting. `Previous()` stops at the first available scene.
- `CanNext()`, `CanPrevious()` return whether an available scene exists in that
  direction outside combat. Restart the current scene explicitly with Start.
- `List() -> rows`: fresh metadata records, sorted by add-on ID then declared
  scene order. Fields: addon, addonTitle, id, title, description, caption,
  instructions, available, reason. No adapter callbacks are exposed.
- `Status() -> addonIDOrNil, sceneIDOrNil, restorationPending, cleanupFailed`.
- `Report(message)`: local chat-frame output only; never sends network chat.
- `ShowWindow()`, `HideWindow()`: companion controls only; hiding never stops a
  scene. Adapters should not need these methods. Scene registration API stays v1.

The optional native selector reads List/Status and uses Start/Stop/Next; it adds
no adapter requirements. While shown, it probes availability once per second, so
availability callbacks must stay cheap and side-effect free.

## Load order

Participating TOCs may add `## OptionalDeps: ForeverShowcase` (append to existing
dependencies). Never add a required dependency. Call your local `register()` at
adapter-file load, and again on `ADDON_LOADED` for `ForeverShowcase`. Keep a local
success flag so registration is idempotent. The example contains the complete
pattern. A late-loaded adapter registers immediately. When Showcase is absent,
the adapter does nothing and ordinary functionality stays unchanged. An optional
dependency alone is not a substitute for the late-registration handler.

Showcase cannot sandbox trusted Lua callbacks. Adapters must enforce storage,
gameplay, combat, timer, and renderer boundaries described in INTEGRATION.md.

## Optional presentation extension (runtime 0.3.0)

API_VERSION remains 1. `Previous()` mirrors Next in reverse. Successful entry
opens the scene toolbar. `context:SetPresentation({frames={root}, background={r,g,b}})`
opts the scene into a clean backdrop; use a method-existence guard for older
runtimes. See PRESENTATION-HANDOFF.md for frame ownership, restoration, combat
and capability rules. All ordinary adapters continue to work unchanged.

## Optional capture UI (0.4.0)

`CAPABILITIES.capture` advertises player-operated capture controls. No adapter update
is required. Auto-fit area uses the existing presentation roots; Draw area works
without them. Crops are saved per addon, shared across scenes. Screenshot records
contain identifiers, display titles/names, time and pixel bounds; no scene fixture or frame objects.
See CAPTURE-WORKFLOW.md. The desktop companion is always optional.
