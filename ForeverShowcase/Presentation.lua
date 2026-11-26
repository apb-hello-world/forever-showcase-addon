-- Opt-in scene composition. Never hides UIParent, reparents frames or scans globals.
local API, ui = ForeverShowcase, ForeverShowcase.Theme
local P = { mode = 1, modes = {'Off', 'Scene', 'Charcoal', 'Ivory', 'Green'} }
API.Presentation = P
local toolbar, backdrop, current, hiddenUntil, clock = nil, nil, nil, nil, 0
local selectorLayer
local function enable(button, yes) if yes then button:Enable() else button:Disable() end end
local function color(value)
    if type(value)~='table' then return nil end
    local result={}
    for i=1,3 do
        local n=value[i]
        if type(n)~='number' or n~=n or n<0 or n>1 then return nil end
        result[i]=n
    end
    return result
end
local function inspect(frames)
    if type(frames)~='table' or #frames==0 then return nil, 'The adapter must provide its scene windows.' end
    local result, seen = {}, {}
    local function visit(frame)
        if seen[frame] then return end
        assert(frame~=UIParent and frame~=WorldFrame, 'Global UI/world frames cannot be scene windows')
        assert(frame and type(frame.GetFrameStrata)=='function' and type(frame.SetFrameStrata)=='function'
            and type(frame.GetFrameLevel)=='function' and type(frame.SetFrameLevel)=='function'
            and type(frame.GetChildren)=='function', 'Expected an adapter-owned native frame')
        assert(not frame.IsForbidden or not frame:IsForbidden(), 'Forbidden scene frame')
        assert(#result<4096, 'Scene frame tree is too large')
        seen[frame]=true
        result[#result+1]={frame=frame,strata=frame:GetFrameStrata(),level=frame:GetFrameLevel()}
        for _,child in ipairs({frame:GetChildren()}) do visit(child) end
    end
    local ok, reason=pcall(function() for _,frame in ipairs(frames) do visit(frame) end end)
    if not ok then return nil,tostring(reason) end
    return result
end
local function hideBackdrop()
    if backdrop then backdrop:Hide() end
end
local function restore(config)
    if not config.saved then return end
    assert(not InCombatLockdown(), 'Scene layering restoration must wait for combat to end')
    local failed
    -- Parent-first then children preserves explicit child strata/levels exactly.
    for _,saved in ipairs(config.saved) do
        local ok,reason=pcall(function()
            saved.frame:SetFrameStrata(saved.strata)
            saved.frame:SetFrameLevel(saved.level)
        end)
        if not ok then failed=reason end
    end
    if failed then error(failed) end
    config.saved=nil
end
function P:Configure(context, options)
    assert(not context._presentation, 'SetPresentation may be called once per scene entry')
    assert(type(options)=='table', 'Presentation options must be a table')
    local background={.09,.07,.06}
    if options.background~=nil then background=color(options.background) end
    assert(background, 'Background must contain three RGB numbers between 0 and 1')
    local checked, reason=inspect(options.frames)
    assert(checked, reason)
    local config={frames={},background=background}
    for _,frame in ipairs(options.frames) do config.frames[#config.frames+1]=frame end
    context._presentation=config
    -- Register before any later layering change. A failed restore faults the session.
    context:AddCleanup(function() restore(config) end)
    context:AddCleanup(function()
        hideBackdrop()
        config.ended=true
    end, false)
    return true
end
function P:SetMode(mode)
    if not current or not current:IsActive() then return false, 'Start a scene outside combat first.' end
    local config=current._presentation
    if not config then return false, 'This adapter has not registered scene windows for a backdrop yet.' end
    if type(mode)~='number' or mode%1~=0 or not self.modes[mode] then return false,'Unknown backdrop option.' end
    hideBackdrop()
    if mode==1 then
        local ok,reason=pcall(restore,config)
        if not ok then API:Stop('presentation-error'); return false,tostring(reason) end
        self.mode=mode; self:Refresh(); return true
    end
    if not config.saved then
        local saved,reason=inspect(config.frames)
        if not saved then return false,reason end
        config.saved=saved -- rollback exists before first mutation
        local ok,err=pcall(function()
            local minimum=math.huge
            for _,item in ipairs(saved) do minimum=math.min(minimum,item.level) end
            for _,item in ipairs(saved) do assert(item.level-minimum<15000, 'Scene layering exceeds the toolbar safety margin') end
            for _,item in ipairs(saved) do
                item.frame:SetFrameStrata('FULLSCREEN_DIALOG')
                item.frame:SetFrameLevel(100+item.level-minimum)
            end
        end)
        if not ok then API:Stop('presentation-error'); return false,tostring(err) end
    end
    local rgb=mode==2 and config.background or mode==3 and {.055,.055,.065}
        or mode==4 and {.94,.88,.76} or {0,1,0}
    backdrop.fill:SetColorTexture(rgb[1],rgb[2],rgb[3],1)
    backdrop:Show()
    self.mode=mode; self:Refresh()
    return true
end
local function invoke(method)
    hiddenUntil=nil
    local ok,message
    if method=='Restart' then
        local addon,scene=API:Status(); ok,message=API:Start(addon,scene)
    else ok,message=API[method](API) end
    if message then API.Report(message) end
    P:Refresh()
    return ok
end
local function fit()
    toolbar:SetScale(math.max(.1,math.min(1,(UIParent:GetWidth()-24)/880)))
end
local function build()
    if toolbar then return end
    backdrop=CreateFrame('Frame',nil,UIParent)
    backdrop:SetAllPoints(UIParent); backdrop:SetFrameStrata('FULLSCREEN'); backdrop:SetFrameLevel(0)
    backdrop:EnableMouse(true) -- prevent clicks through the opaque stage into the world
    backdrop.fill=backdrop:CreateTexture(nil,'BACKGROUND'); backdrop.fill:SetAllPoints(); backdrop:Hide()
    toolbar=CreateFrame('Frame','ForeverShowcaseToolbar',UIParent)
    P.toolbar=toolbar; P.backdrop=backdrop
    toolbar:SetSize(880,140); toolbar:SetPoint('TOP',UIParent,'TOP',0,-20)
    -- This is a capture overlay root, deliberately above opt-in scene windows.
    -- A scene's native click-to-raise must not cover the recovery controls.
    toolbar:SetFrameStrata('TOOLTIP'); toolbar:SetFrameLevel(100)
    toolbar:SetToplevel(true); toolbar:EnableMouse(true); toolbar:SetMovable(true); toolbar:SetClampedToScreen(true)
    -- Use the approved shell's finished wood action strip, not a new skin.
    local bg=toolbar:CreateTexture(nil,'BACKGROUND'); bg:SetAllPoints()
    bg:SetTexture(ui.media..'StagekeeperShell'); bg:SetTexCoord(.025,.975,.822,.932)
    toolbar.title=ui.Label(toolbar,'',14,16,8,848,22,true)
    local drag=CreateFrame('Frame',nil,toolbar); drag:SetPoint('TOPLEFT',8,-2); drag:SetSize(864,27)
    drag:EnableMouse(true); drag:RegisterForDrag('LeftButton')
    drag:SetScript('OnDragStart',function() toolbar:Raise(); toolbar:StartMoving() end)
    drag:SetScript('OnDragStop',function() toolbar:StopMovingOrSizing() end)
    local function button(key,label,x,width,fn)
        local b=ui.Button(toolbar,label,width,32); b:SetPoint('TOPLEFT',x,-32)
        b:SetScript('OnClick',fn); toolbar[key]=b; return b
    end
    button('previous','Previous',16,92,function() invoke('Previous') end)
    button('next','Next',114,76,function() invoke('Next') end)
    button('restart','Restart',196,86,function() invoke('Restart') end)
    button('stop','Stop scene',288,100,function() invoke('Stop') end)
    button('selector','Scene list',394,100,function() P:ShowControls(); API:ShowScenePicker() end)
    button('background','Backdrop: Off',500,166,function()
        local ok,message=P:SetMode(P.mode%#P.modes+1)
        if not ok then API.Report(message) end
    end)
    toolbar.background.tip='Cycle Off, adapter color, charcoal, ivory, and green. Requires adapter-registered scene windows.'
    button('hide','Hide for 10s',672,192,function()
        if current and current:IsActive() then P:HideForCapture()
        else hiddenUntil=nil; toolbar:Hide() end
    end)
    if API.Capture then
        local entries={{'Draw area',16,150,function() API.Capture:ShowArea(true) end},
            {'Auto-fit area',172,150,function() API.Capture:Fit() end},
            {'Capture',328,150,function() API.Capture:Take() end},
            {'Captures',484,150,function() API.Capture:ShowGallery() end}}
        for _,e in ipairs(entries) do
            local b=ui.Button(toolbar,e[1],e[3],30); b:SetPoint('TOPLEFT',e[2],-72); b:SetScript('OnClick',e[4])
        end
    end
    toolbar.note=ui.Label(toolbar,'',12,16,110,848,20,true)
    toolbar:SetScript('OnHide',function(self) self:StopMovingOrSizing(); if GameTooltip then GameTooltip:Hide() end end)
    toolbar:Hide(); fit()
end
function P:Refresh()
    if not toolbar then return end
    local addon,scene,pending,faulted=API:Status()
    local ready=addon and not InCombatLockdown() and not pending and not faulted
    toolbar.title:SetText(addon and ('Forever Showcase  -  '..addon..' / '..scene) or
        faulted and 'Cleanup failed - reload required' or pending and 'Restoration pending until combat ends' or 'Scene stopped')
    for _,key in ipairs({'previous','next','restart','stop'}) do enable(toolbar[key],ready) end
    enable(toolbar.hide,true)
    toolbar.hide:SetText(ready and 'Hide for 10s' or 'Close toolbar')
    enable(toolbar.background,ready and current and current._presentation)
    toolbar.background:SetText('Backdrop: '..self.modes[backdrop:IsShown() and self.mode or 1])
    toolbar.note:SetText(current and not current._presentation and 'Backdrop unavailable: this adapter must register its scene windows.'
        or 'Drag the title to move. Hide for 10s removes controls, then brings them back automatically.')
    if API.Capture and ready then
        local r=API.Capture:Rect()
        toolbar.note:SetText(r and ('Capture area: '..r.width..' x '..r.height..' pixels. Capture hides controls; Captures sends the batch.')
            or 'Draw area or Auto-fit area to set a repeatable crop. Captures opens your recent capture records.')
    end
    if API.Window then
        if addon then
            if not selectorLayer then selectorLayer={API.Window:GetFrameStrata(),API.Window:GetFrameLevel()} end
            if API.Window:GetFrameStrata()~='TOOLTIP' then API.Window:SetFrameStrata('TOOLTIP'); API.Window:SetFrameLevel(200) end
        elseif selectorLayer then
            API.Window:SetFrameStrata(selectorLayer[1]); API.Window:SetFrameLevel(selectorLayer[2]); selectorLayer=nil
        end
    end
end
function P:ShowControls()
    hiddenUntil=nil
    if toolbar and (current or select(3,API:Status()) or select(4,API:Status())) then
        fit(); toolbar:Show(); toolbar:Raise(); self:Refresh()
    end
end
function P:GetContext() return current end
function P:SuspendControls()
    hiddenUntil=nil
    if toolbar then toolbar:Hide() end
end
function P:HideForCapture()
    if not current or not current:IsActive() then return end
    hiddenUntil=clock+10
    API:HideWindow(); toolbar:Hide()
    if GameTooltip then GameTooltip:Hide() end
end
API._OnSessionStarted=function(context)
    build(); current=context; P.lastAddon=context.addonID; hiddenUntil=nil
    API:HideWindow()
    toolbar:Show(); toolbar:Raise()
    if context._presentation and P.mode~=1 then
        local ok,reason=P:SetMode(P.mode)
        if not ok then API.Report(reason) end
    end
    P:Refresh()
end
API._OnSessionStopped=function(context, reason)
    if API.Capture then API.Capture:Cancel() end
    hiddenUntil=nil; hideBackdrop()
    if current==context then current=nil end
    if toolbar then
        if reason=='switch' then toolbar:Hide() else toolbar:Show() end
    end
    -- Full lifecycle status is refreshed after deferred cleanup by the controller.
end
local controller=CreateFrame('Frame')
P.controller=controller
local elapsed=0
controller:SetScript('OnUpdate',function(_,delta)
    clock=clock+delta; elapsed=elapsed+delta
    if hiddenUntil and clock>=hiddenUntil then hiddenUntil=nil; P:ShowControls() end
    if elapsed>=.25 then
        elapsed=0
        if toolbar and toolbar:IsShown() then P:Refresh() end
    end
end)
controller:RegisterEvent('DISPLAY_SIZE_CHANGED'); controller:RegisterEvent('UI_SCALE_CHANGED')
controller:SetScript('OnEvent',function() if toolbar then fit() end end)
