-- Deliberately nonvisual: this fixture validates isolation, not screenshot rendering.
local workspace = { page = "home", source = { "ordinary workspace" } }
local registered = false
local function enter(context)
    local previousPage, previousSource = workspace.page, workspace.source
    context:AddCleanup(function()
        workspace.page, workspace.source = previousPage, previousSource
    end, false) -- pure Lua state, safe during combat
    workspace.page = context.sceneID
    workspace.source = { "Sample one", "Sample two" } -- never SavedVariables
    -- Real adapters must guard timers/events AND cancel/unregister them on cleanup.
    local refresh = context:Guard(function() workspace.refreshed = true end)
    refresh()
    context:AddCleanup(function() workspace.refreshed = nil end, false)
end
local function leave(context, reason)
    -- Idempotent restoration registered before mutation; no additional work here.
end
local function register()
    if registered or not ForeverShowcase then return end
    local ok, reason = ForeverShowcase:Register(1, {
        id = "example", title = "Synthetic lifecycle fixture",
        scenes = {
            { id = "first", title = "First memory fixture", enter = enter, leave = leave,
              description = "A nonvisual, isolated memory scene.", caption = "Development fixture only",
              instructions = "No screenshot UI is rendered. Try /showcase next, then /showcase off." },
            { id = "second", title = "Second memory fixture", enter = enter, leave = leave },
            { id = "unavailable", title = "Unsupported feature", enter = enter, leave = leave,
              available = function() return false, "This fixture cannot safely demonstrate gameplay." end },
        },
    })
    registered = ok
    if not ok then ForeverShowcase.Report(reason) end
end
local listener = CreateFrame("Frame")
listener:RegisterEvent("ADDON_LOADED")
listener:SetScript("OnEvent", function(_, _, name)
    if name == "ForeverShowcase" then register() end
end)
register() -- works when companion loaded first; ADDON_LOADED handles the reverse
