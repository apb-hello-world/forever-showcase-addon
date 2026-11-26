# Scene toolbar and clean backdrop — runtime 0.3.0, API v1

The toolbar works with existing adapters without any code change. Starting a
scene closes the selector and shows Previous, Next, Restart, Stop scene, Scene
list, Backdrop and Hide for 10s. Navigation stays within the current add-on,
skips unavailable scenes and stops at either end without wrapping. Next and
Previous disable at the last and first available scenes. Use Restart to repeat
the current scene, including in a one-scene integration.
Hide for 10s hides the selector and toolbar, leaves the scene/background active,
then automatically brings the toolbar back. The user captures manually. No
screenshot API, keybinding changes, chat sends or automatic game input is used.

## Optional adapter update

At the **end of enter**, after all real scene windows, popups and input shields
have been built and their usual restoration registered:

```lua
if context.SetPresentation then
    context:SetPresentation({
        frames = { mySceneWindow },
        background = { 0.09, 0.07, 0.06 }, -- RGB 0..1, always opaque
    })
end
```

Use the actual frame object, not a global name string. For Spellwright the agent
should evaluate `ns.UI.mainFrame` and include any separate top-level scene windows
that are not descendants. Do not edit Showcase to hard-code Spellwright names.
The owner confirmed the first Spellwright scene works before this extension;
the clean-background option needs its own native validation.

`SetPresentation` is an additive API-v1 capability. Older runtimes lack the
method, so use the guard above. `ForeverShowcase.CAPABILITIES.presentation` also
advertises support. Call it once per entry. Re-register on each new session.
Background defaults to dark warm charcoal when omitted. Invalid options raise
an entry error before any scene-layer mutation. Return value on success is true.

## Ownership and restoration

Providing a root explicitly authorizes Showcase to adjust that root and its
descendant frame tree's strata/levels while a backdrop is active. Register only
frames this adapter owns and has prepared for demo mode. Never register UIParent,
WorldFrame, Blizzard windows, shared ancestors or other addons' windows.
Do not reparent unrelated UI or depend on captured frames being hidden by Showcase.

Showcase snapshots the tree before enabling a backdrop, preserves relative frame
levels, and temporarily raises it above an opaque fullscreen background. Parent
and child strata/levels are restored when backdrop is turned off or the scene
ends. Restoration errors block new sessions through the existing fault mechanism.
Scene roots and children must support normal native frame layering methods.
Keep the registered tree stable while backdrop mode is enabled: late-created
popups/frames are not part of the earlier snapshot. Create them before this call,
or exit/re-enter the scene to capture a changed composition.

On combat, the backdrop disappears immediately so it cannot cover gameplay. No
scene-frame mutation occurs in combat. Protected layering restoration is deferred
through the session cleanup until combat ends, just like adapter restoration.
Reload discards the whole temporary composition. No preferences/session persist.

The selector/toolbar use an overlay root above scene windows while active so a
scene's click-to-raise cannot cover recovery controls. No child of an unrelated
addon is independently raised.

## What this mode does and does not do

It covers the world and ordinary HUD with a flat opaque color and leaves the
registered real scene windows on top. It does **not** hide UIParent or promise to
suppress unrelated high-strata dialogs, system warnings or third-party tooltips.
Those may still appear; dismiss unrelated windows before capturing. The renderer
and scene artwork remain the participating add-on's own.

Toolbar background choices: Off, Scene (adapter RGB), Charcoal, Ivory, Green.
The chosen mode is remembered in memory across scenes; Scene resolves the current
adapter's color. Adapters without opt-in cannot enable a background and receive
a visible explanation. Other integrations remain fully usable without this feature.

## Required adapter test

Start with the stage off; activate Scene background. Verify all scene windows and
read-only input shields remain correctly layered. Try the other background colors,
Hide for 10s and the automatic toolbar return. Toggle background off and compare
original strata/levels and native appearance. Test scene switch, failed entry,
Stop, reload and combat; the background must never remain over normal gameplay.
