local API = ForeverShowcase
SLASH_FOREVERSHOWCASE1 = "/showcase"
SlashCmdList.FOREVERSHOWCASE = function(input)
    local words = {}
    for word in input:gmatch("%S+") do words[#words + 1] = word:lower() end
    local command = words[1]
    local ok, message
    if not command or command == "show" then
        API._showSelfInSelector=false
        if API.ShowWindow then API:ShowWindow() else API.Report("/showcase list | <addon> <scene> | next | off | status | info") end
    elseif command == "self" then
        if API.ShowSelfScenes then API:ShowSelfScenes() end
    elseif command == "hide" then
        if API.HideWindow then API:HideWindow() end
    elseif command == "help" then
        API.Report("/showcase opens controls | hide | list | <addon> <scene> | next | off | status | info. Hide controls leaves the scene active.")
    elseif command == "list" then
        local scenes = API:List()
        if #scenes == 0 then API.Report("No integrations registered. Install an adapter-enabled add-on; Showcase works on its own.") end
        for _, scene in ipairs(scenes) do
            API.Report(scene.addon .. " " .. scene.id .. " — " .. scene.title .. (scene.available and "" or " (unavailable: " .. tostring(scene.reason) .. ")"))
        end
    elseif command == "off" then ok, message = API:Stop()
    elseif command == "next" then ok, message = API:Next()
    elseif command == "previous" then ok, message = API:Previous()
    elseif command == "status" or command == "info" then
        local addon, id, pending, faulted = API:Status()
        API.Report(addon and (addon .. " " .. id) or (pending and "Waiting for combat restoration." or "No active scene."))
        if faulted then API.Report("Cleanup failed. Reload required before another scene.") end
        if command == "info" and addon then
            for _, scene in ipairs(API:List()) do
                if scene.addon == addon and scene.id == id then
                    for _, key in ipairs({ "description", "caption", "instructions" }) do
                        if scene[key] then API.Report(key .. ": " .. scene[key]) end
                    end
                end
            end
        end
    elseif #words == 2 then ok, message = API:Start(command, words[2])
    else ok, message = false, "Unknown command. Use /showcase help." end
    if message then API.Report(message) elseif ok == false then API.Report("Operation failed.") end
    if API.RefreshWindow then API:RefreshWindow() end
end
