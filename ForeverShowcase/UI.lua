local API, ui = ForeverShowcase, ForeverShowcase.Theme
local window, selectedAddon, selectedScene
local addonPage, scenePage, pageSize = 1, 1, 6
local lastStatus, elapsed, availabilityElapsed = nil, 0, 0
local function enabled(button, value) if value then button:Enable() else button:Disable() end end
local function focusActive()
    local addon, scene = API:Status()
    if not addon then return end
    selectedAddon, selectedScene = addon, scene
    local addonIndex, sceneIndex, seen = 0, 0, {}
    for _, row in ipairs(API:List()) do
        if not seen[row.addon] then
            seen[row.addon] = true; addonIndex = addonIndex+1
            if row.addon==addon then addonPage=math.ceil(addonIndex/pageSize) end
        end
        if row.addon==addon then
            sceneIndex=sceneIndex+1
            if row.id==scene then scenePage=math.ceil(sceneIndex/pageSize) end
        end
    end
end
local function run(method, ...)
    local ok, message = API[method](API, ...)
    if message then API.Report(message) end
    if window then window.notice = not ok and message or nil end
    if method == 'Next' and ok then focusActive() end
    API:RefreshWindow()
end
local function statusKey()
    local addon, scene, pending, faulted = API:Status()
    return table.concat({addon or '', scene or '', tostring(pending), tostring(faulted), tostring(InCombatLockdown()), tostring(API._registryRevision or 0)}, ':')
end
local function fit()
    local scale = math.min(1, (UIParent:GetWidth()-40)/1000, (UIParent:GetHeight()-40)/760)
    window:SetScale(math.max(.1, scale))
end
local function pager(parent, x, y, width, change)
    local p = CreateFrame('Frame', nil, parent); p:SetSize(width, 28); p:SetPoint('TOPLEFT', x, -y)
    p.previous = ui.Button(p, 'Prev', 52, 28); p.previous:SetPoint('LEFT')
    p.next = ui.Button(p, 'Next', 52, 28); p.next:SetPoint('RIGHT')
    p.label = ui.Label(p, '', 12, 53, 7, width-106, 16, true); p.label:SetJustifyH('CENTER')
    p.previous:SetScript('OnClick', function() change(-1) end)
    p.next:SetScript('OnClick', function() change(1) end)
    function p:Update(page, count)
        local pages = math.max(1, math.ceil(count/pageSize))
        self.label:SetText(page .. '/' .. pages)
        enabled(self.previous, page>1); enabled(self.next, page<pages)
        if pages>1 then self:Show() else self:Hide() end
    end
    return p
end
local function build()
    window = CreateFrame('Frame', 'ForeverShowcaseWindow', UIParent)
    API.Window = window
    window:SetSize(1000,760); window:SetPoint('CENTER'); window:SetFrameStrata('DIALOG')
    window:SetToplevel(true); window:EnableMouse(true); window:SetClampedToScreen(true)
    window:SetMovable(true)
    local shell = window:CreateTexture(nil, 'BACKGROUND'); shell:SetAllPoints(); shell:SetTexture(ui.media .. 'StagekeeperShell')
    -- Transparent 1024x256 canvas; uniform scaling preserves the wordmark.
    local title = window:CreateTexture(nil, 'ARTWORK')
    title:SetTexture(ui.media .. 'StagekeeperWordmark')
    title:SetSize(400,100); title:SetPoint('TOPLEFT',300,-42)
    local drag = CreateFrame('Frame', nil, window); drag:SetPoint('TOPLEFT', 270, -45); drag:SetSize(470,85)
    drag:EnableMouse(true); drag:RegisterForDrag('LeftButton')
    drag:SetScript('OnDragStart', function() window:Raise(); window:StartMoving() end)
    drag:SetScript('OnDragStop', function() window:StopMovingOrSizing() end)
    window.close = ui.Button(window, 'X', 32, 30); window.close:SetPoint('TOPRIGHT', -46, -77)
    window.close:SetScript('OnClick', function() window:Hide() end)
    window.close.tip = 'Hide controls; the active scene keeps running.'
    ui.Label(window, 'Add-on', 18, 66, 151, 155, 25, true)
    ui.Label(window, 'Scene', 18, 272, 151, 170, 25, true)
    window.addonRows, window.sceneRows = {}, {}
    for i=1,pageSize do
        local row = ui.Button(window, '', 178, 48, 'row'); row.dark=true
        row:SetPoint('TOPLEFT', 51, -(201+(i-1)*56))
        row:SetScript('OnClick', function(self)
            selectedAddon, selectedScene, scenePage = self.id, nil, 1
            window.notice=nil; API:RefreshWindow()
        end)
        window.addonRows[i] = row
        row = ui.Button(window, '', 194, 48, 'row'); row:SetPoint('TOPLEFT', 260, -(201+(i-1)*56))
        row:SetScript('OnClick', function(self) selectedScene=self.id; window.notice=nil; API:RefreshWindow() end)
        window.sceneRows[i] = row
    end
    window.addonPager = pager(window, 54, 566, 174, function(delta) addonPage=addonPage+delta; API:RefreshWindow() end)
    window.scenePager = pager(window, 266, 566, 182, function(delta) scenePage=scenePage+delta; API:RefreshWindow() end)
    window.scenePager.label:SetTextColor(.20,.12,.07)
    window.heading = ui.Label(window, '', 24, 506, 180, 414, 64, false)
    window.scroll = CreateFrame('ScrollFrame', nil, window)
    window.scroll:SetPoint('TOPLEFT', 506, -252); window.scroll:SetSize(412, 290)
    window.content = CreateFrame('Frame', nil, window.scroll); window.content:SetSize(412, 290)
    window.scroll:SetScrollChild(window.content); window.scroll:EnableMouseWheel(true)
    window.scroll:SetScript('OnMouseWheel', function(self, delta)
        self:SetVerticalScroll(math.max(0, math.min(window.scrollMax or 0, self:GetVerticalScroll()-delta*40)))
    end)
    window.body = ui.Label(window.content, '', 14, 0, 0, 410, 1, false)
    window.body:SetSpacing(5)
    window.scrollHint = ui.Label(window, '', 12, 506, 550, 410, 24, false)
    window.noticeLabel = ui.Label(window, '', 12, 506, 576, 410, 26, false)
    window.status = ui.Label(window, '', 14, 52, 641, 270, 57, true)
    window.start = ui.Button(window, 'Start scene', 144, 36); window.start:SetPoint('TOPLEFT',340,-652)
    window.start:SetScript('OnClick', function() run('Start', selectedAddon, selectedScene) end)
    window.next = ui.Button(window, 'Next scene', 130, 36); window.next:SetPoint('TOPLEFT',492,-652)
    window.next:SetScript('OnClick', function() run('Next') end)
    window.hide = ui.Button(window, 'Hide controls', 150, 36); window.hide:SetPoint('TOPLEFT',630,-652)
    window.hide:SetScript('OnClick', function() window:Hide() end)
    window.stop = ui.Button(window, 'Stop scene', 150, 36); window.stop:SetPoint('TOPLEFT',788,-652)
    window.stop:SetScript('OnClick', function() run('Stop') end)
    local footer = ui.Label(window, 'Starting a scene opens its toolbar. Close hides this list; Stop scene restores your workspace.', 12, 80, 721, 840, 18, true)
    footer:SetJustifyH('CENTER')
    if API.Capture then
        local captures=ui.Button(window,'Captures',150,28); captures:SetPoint('TOPLEFT',780,-120)
        captures:SetScript('OnClick',function() API.Capture:ShowGallery() end)
    end
    table.insert(UISpecialFrames, 'ForeverShowcaseWindow')
    window:SetScript('OnShow', function(self) fit(); self:Raise(); API:RefreshWindow() end)
    window:SetScript('OnHide', function(self) self:StopMovingOrSizing(); if GameTooltip then GameTooltip:Hide() end end)
    window:SetScript('OnUpdate', function(_, delta)
        elapsed=elapsed+delta; availabilityElapsed=availabilityElapsed+delta
        if elapsed<.25 then return end
        elapsed=0
        -- Availability can change without a lifecycle event. Probe only while visible.
        if lastStatus~=statusKey() or availabilityElapsed>=1 then
            availabilityElapsed=0; API:RefreshWindow()
        end
    end)
    window:RegisterEvent('ADDON_LOADED'); window:RegisterEvent('DISPLAY_SIZE_CHANGED')
    window:RegisterEvent('UI_SCALE_CHANGED')
    window:SetScript('OnEvent', function(self, event)
        if self:IsShown() then
            if event~='ADDON_LOADED' then fit() end
            API:RefreshWindow()
        end
    end)
    window:Hide()
end
function API:RefreshWindow()
    if not window then return end
    local rows, addons, seen, scenes = self:List(), {}, {}, {}
    for _, row in ipairs(rows) do
        if not seen[row.addon] then addons[#addons+1]={id=row.addon,title=row.addonTitle}; seen[row.addon]=true end
    end
    if not selectedAddon or not seen[selectedAddon] then
        selectedAddon=addons[1] and addons[1].id; selectedScene=nil; scenePage=1
    end
    for _, row in ipairs(rows) do if row.addon==selectedAddon then scenes[#scenes+1]=row end end
    local selected
    for _, row in ipairs(scenes) do if row.id==selectedScene then selected=row end end
    if not selected then selected=scenes[1]; selectedScene=selected and selected.id end
    addonPage=math.max(1,math.min(addonPage,math.ceil(#addons/pageSize)))
    scenePage=math.max(1,math.min(scenePage,math.ceil(#scenes/pageSize)))
    for i=1,pageSize do
        local row, data = window.addonRows[i], addons[(addonPage-1)*pageSize+i]
        if data then row.id=data.id; row:SetText(data.title); row.tip=data.title; row:SetSelected(data.id==selectedAddon); row:Show() else row:Hide() end
        row, data = window.sceneRows[i], scenes[(scenePage-1)*pageSize+i]
        if data then
            row.id=data.id; row:SetText(data.title); row.tip=data.title .. (data.available and '' or ('\nUnavailable: '..tostring(data.reason)))
            row:SetSelected(data.id==selectedScene); row:Show()
        else row:Hide() end
    end
    window.addonPager:Update(addonPage,#addons); window.scenePager:Update(scenePage,#scenes)
    window.heading:SetText(selected and selected.title or 'No integrations yet')
    local body
    if selected then
        body=(selected.description or 'This scene is provided by '..selected.addonTitle..'.')
            ..'\n\nSuggested caption\n'..(selected.caption or 'No caption supplied.')
            ..'\n\nCapture notes\n'..(selected.instructions or 'Hide these controls, then take your screenshot manually.')
        if #selected.title>55 then body=selected.title..'\n\n'..body end
        if not selected.available then body='Unavailable\n'..tostring(selected.reason)..'\n\n'..body end
    else body='Install an add-on with a Showcase adapter to see its scenes here.\n\nThe separate Example add-on provides nonvisual lifecycle tests.\n\nSpellwright scenes will appear when its adapter is implemented.' end
    local key=(selectedAddon or '')..'/'..(selectedScene or '')
    if key~=window.detailKey then window.scroll:SetVerticalScroll(0); window.detailKey=key end
    window.body:SetText(body); window.body:SetHeight(0)
    local textHeight=window.body:GetStringHeight()+8
    window.body:SetHeight(textHeight)
    local height=math.max(290,textHeight)
    window.content:SetHeight(height); window.scrollMax=height-290
    window.scroll:SetVerticalScroll(math.min(window.scroll:GetVerticalScroll(),window.scrollMax))
    window.scrollHint:SetText(window.scrollMax>0 and 'Scroll for more details' or '')
    local addon, scene, pending, faulted=self:Status()
    local fighting=InCombatLockdown()
    window.status:SetText(faulted and 'Cleanup failed. Reload before starting another scene.'
        or pending and 'Restoration waits for combat to end.'
        or fighting and 'In combat. Scene activation is paused.'
        or addon and ('Active: '..addon..' / '..scene) or 'No active scene')
    window.noticeLabel:SetText(window.notice or '')
    window.start:SetText(addon==selectedAddon and scene==selectedScene and addon and 'Restart scene' or 'Start scene')
    enabled(window.start, selected and selected.available and not fighting and not pending and not faulted)
    enabled(window.next, addon and not fighting and not pending and not faulted)
    enabled(window.stop, addon~=nil)
    window.hide:SetText(addon and 'Scene toolbar' or 'Hide controls')
    lastStatus=statusKey()
end
function API:ShowWindow()
    if not window then build() end
    -- Follow a command-activated scene on reopening, while browsing remains free.
    focusActive()
    window:Show(); window:Raise(); self:RefreshWindow()
    if self.Presentation then self.Presentation:ShowControls(); self.Presentation:Refresh() end
end
function API:HideWindow() if window then window:Hide() end end
