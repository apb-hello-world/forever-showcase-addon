# Begin a Forever Showcase integration

Companion API v1 is ready for adapter development. Runtime 0.3.0 includes the
Stagekeeper selector. The owner approved the overall 0.2.0 window appearance;
that confirmation does not cover adapter data safety or all combat behaviors.

Give the following task to the agent for the participating add-on:

> Implement an optional Forever Showcase API v1 adapter in this add-on. Read
> `D:/Projects/wow-forever-addons/forever-showcase/API.md`, `INTEGRATION.md`, and
> `examples/ForeverShowcaseExample/Example.lua` first. Start with one representative
> scene using the add-on's actual UI and isolated, deterministic in-memory data.
> Preserve ordinary behavior when Showcase is absent. Use optional dependency
> ordering plus immediate/late registration. Register cleanup before mutation,
> guard and cancel delayed work, and disconnect demo data with combat-safe cleanup.
> Never write sample data to SavedVariables or perform real gameplay changes.
> Restore the prior workspace and geometry on exit; mark unsafe features unavailable.
> Test repeated activation, partial entry failure, switching, stale callbacks,
> cleanup failure, reload, and combat. Install for owner-controlled native checks.
> Do not publish or modify other add-ons. Do not change the companion's API contract
> to fit an adapter without first reporting the missing capability.

Only register scenes the add-on can actually implement safely. The companion
automatically discovers registrations and shows their metadata in its selector.
No companion-side catalog edit is required. Use `ForeverShowcase:Register(1, def)`;
the API version stays 1 despite the runtime's 0.3.0 optional presentation extension.

For Spellwright, also read `SPELLWRIGHT-HANDOFF.md` and begin with `editor` before
expanding to menus, smartcast, quickfixes, templates and appearance.

Ready to begin integration is not a claim that an adapter is screenshot-ready.
Confirm the first scene's real rendering, restoration and absence of data/gameplay
side effects in game before expanding the adapter. No other add-on was changed
by this companion project.

For the optional 0.3.0 clean screenshot backdrop, also read
`D:/Projects/wow-forever-addons/forever-showcase/PRESENTATION-HANDOFF.md`.
The scene toolbar needs no adapter update. API v1 remains compatible.
