-- API v1. No SavedVariables, hooks, gameplay actions, or global API replacement.
local API = { API_VERSION = 1, VERSION = "0.5.2", CAPABILITIES = { presentation = true } }
ForeverShowcase = API
local registry, active, pending, busy, faulted = {}, nil, nil, false, false
local function combat() return InCombatLockdown() end
local function report(message)
    if DEFAULT_CHAT_FRAME then DEFAULT_CHAT_FRAME:AddMessage("Forever Showcase: " .. tostring(message)) end
end
API.Report = report
local function call(fn, ...)
    local ok, result = pcall(fn, ...)
    if not ok then report(result) end
    return ok, result
end
local function validID(id) return type(id) == "string" and id:match("^[a-z][a-z0-9_-]*$") end
local function availability(scene)
    if not scene.available then return true end
    local ok, ready, reason = pcall(scene.available)
    if not ok then return false, "Availability check failed: " .. tostring(ready) end
    return ready == true, reason or "Scene is unavailable."
end
function API:Register(version, definition)
    if version ~= self.API_VERSION then return false, "Unsupported API version." end
    if type(definition) ~= "table" or not validID(definition.id) or type(definition.title) ~= "string"
        or type(definition.scenes) ~= "table" or #definition.scenes == 0 then
        return false, "Invalid integration definition."
    end
    if registry[definition.id] then return false, "Integration already registered." end
    local entry = { id = definition.id, title = definition.title, scenes = {}, order = {} }
    for _, scene in ipairs(definition.scenes) do
        if type(scene) ~= "table" or not validID(scene.id) or type(scene.title) ~= "string"
            or type(scene.enter) ~= "function" or type(scene.leave) ~= "function"
            or (scene.available ~= nil and type(scene.available) ~= "function") or entry.scenes[scene.id] then
            return false, "Invalid or duplicate scene definition."
        end
        local copy = {}
        for _, key in ipairs({ "id", "title", "description", "caption", "instructions", "enter", "leave", "available" }) do
            if scene[key] ~= nil and key ~= "enter" and key ~= "leave" and key ~= "available" and type(scene[key]) ~= "string" then
                return false, "Metadata must be strings."
            end
            copy[key] = scene[key]
        end
        entry.scenes[copy.id] = copy
        entry.order[#entry.order + 1] = copy.id
    end
    registry[entry.id] = entry
    self._registryRevision = (self._registryRevision or 0) + 1
    return true
end
function API:List()
    local result, ids = {}, {}
    for id in pairs(registry) do ids[#ids + 1] = id end
    table.sort(ids)
    for _, id in ipairs(ids) do
        local entry = registry[id]
        for _, sceneID in ipairs(entry.order) do
            local scene = entry.scenes[sceneID]
            local ready, reason = availability(scene)
            result[#result + 1] = { addon = id, addonTitle = entry.title, id = sceneID, title = scene.title,
                description = scene.description, caption = scene.caption, instructions = scene.instructions,
                available = ready, reason = not ready and reason or nil }
        end
    end
    return result
end
function API:Status()
    return active and active.addon, active and active.scene.id, pending ~= nil, faulted
end
local function finish(session)
    -- leave always runs out of combat, including after a partially failed enter.
    if not call(session.scene.leave, session.context, session.reason) then faulted = true end
    for i = #session.cleanups, 1, -1 do
        local item = session.cleanups[i]
        if not item.done then
            item.done = true
            if not call(item.fn, session.reason) then faulted = true end
        end
    end
end
local function stop(reason)
    if not active then return end
    local session = active
    active = nil -- invalidate guarded callbacks before any adapter code runs
    session.live, session.reason = false, reason
    if API._OnSessionStopped then call(API._OnSessionStopped, session.context, reason) end
    if combat() then
        pending = session
        -- Only explicitly combat-safe cleanup executes now.
        for i = #session.cleanups, 1, -1 do
            local item = session.cleanups[i]
            if not item.protected then
                item.done = true
                if not call(item.fn, reason) then faulted = true end
            end
        end
    else finish(session) end
end
function API:Stop(reason)
    if busy then return false, "Lifecycle operation already in progress." end
    busy = true
    stop(reason or "off")
    busy = false
    if faulted then return false, "Cleanup failed; reload before starting another scene." end
    return true, pending and "Restoration deferred until combat ends." or nil
end
function API:Start(addon, sceneID)
    if busy then return false, "Lifecycle operation already in progress." end
    if combat() then return false, "Scenes cannot start in combat." end
    if pending or faulted then return false, "Restoration pending or failed; finish combat or reload." end
    local entry = registry[addon]
    if not entry then return false, "Integration not registered: " .. tostring(addon) .. ". Install an adapter-enabled add-on." end
    local scene = entry.scenes[sceneID]
    if not scene then return false, "Unknown scene: " .. tostring(sceneID) end
    busy = true
    local ready, reason = availability(scene)
    if not ready then busy = false; return false, reason end
    stop("switch")
    if faulted or pending or combat() then busy = false; return false, "Previous scene could not safely restore." end
    local session = { addon = addon, scene = scene, cleanups = {}, live = true }
    local context = { addonID = addon, sceneID = sceneID }
    session.context = context
    function context:IsActive() return session.live and active == session and not combat() end
    function context:AddCleanup(fn, protected)
        assert(session.live and active == session, "Cannot add cleanup to an inactive session")
        assert(type(fn) == "function", "Cleanup must be a function")
        -- Safe default: deferred in combat. false must be deliberately supplied.
        session.cleanups[#session.cleanups + 1] = { fn = fn, protected = protected ~= false }
    end
    function context:Guard(fn)
        assert(type(fn) == "function", "Guard requires a function")
        return function(...)
            if not self:IsActive() then return end
            local ok, result = call(fn, ...)
            if not ok then
                session.callbackFailed = true
                API:Stop("callback-error")
            end
            return ok, result
        end
    end
    function context:SetPresentation(options)
        assert(self:IsActive(), "Presentation requires an active session")
        assert(API.Presentation, "Presentation module is not loaded")
        return API.Presentation:Configure(self, options)
    end
    active = session
    local ok, result = call(scene.enter, context)
    if session.callbackFailed then ok = false end
    if not ok or result == false then stop("entry-failed") end
    busy = false
    if not ok or result == false then return false, "Scene entry failed; cleanup attempted." end
    if self._OnSessionStarted then
        local shown = call(self._OnSessionStarted, context)
        if not shown then self:Stop("presentation-error"); return false, "Scene controls failed; cleanup attempted." end
        if not context:IsActive() then return false, "Scene presentation failed; cleanup attempted." end
    end
    return true, scene.instructions or "Scene ready. Capture manually; /showcase off restores the workspace."
end
local function step(self, direction)
    if not active then return false, "No active scene. Use /showcase list." end
    local entry, current = registry[active.addon], active.scene.id
    local index = 1
    for i, id in ipairs(entry.order) do if id == current then index = i end end
    for offset = 1, #entry.order do
        local id = entry.order[(index + direction * offset - 1) % #entry.order + 1]
        if availability(entry.scenes[id]) then return self:Start(entry.id, id) end
    end
    return false, "No available scenes."
end
function API:Next() return step(self, 1) end
function API:Previous() return step(self, -1) end
local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_REGEN_DISABLED")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:RegisterEvent("PLAYER_LOGOUT")
events:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_REGEN_ENABLED" and pending then
        busy = true
        local session = pending
        pending = nil
        finish(session)
        busy = false
    elseif event == "PLAYER_REGEN_DISABLED" then
        local wasActive = active ~= nil
        API:Stop("combat")
        if wasActive then report("Scene stopped for combat; protected restoration waits until combat ends.") end
    elseif event == "PLAYER_LOGOUT" then API:Stop("logout") end
end)
