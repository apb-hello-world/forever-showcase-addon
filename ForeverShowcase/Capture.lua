-- Metadata only. WoW owns screenshot files; the optional desktop app owns crops.
local API = ForeverShowcase
local C = { limit=200 }
API.Capture=C
API.CAPABILITIES.capture=true
local pending, blocked, ticks = nil, false, 0
function C:DB()
    if type(ForeverShowcaseDB)~='table' then ForeverShowcaseDB={} end
    local db=ForeverShowcaseDB
    db.schema=1
    if type(db.captures)~='table' then db.captures={} end
    if type(db.crops)~='table' then db.crops={} end
    if type(db.captureCounts)~='table' then db.captureCounts={} end
    db.sequence=tonumber(db.sequence) or 0
    return db
end
function C:Screen()
    local w,h
    if GetPhysicalScreenSize then w,h=GetPhysicalScreenSize() end
    if not w or not h or w<=0 or h<=0 then
        local s=UIParent:GetEffectiveScale()
        w,h=UIParent:GetWidth()*s,UIParent:GetHeight()*s
    end
    return math.floor(w+.5),math.floor(h+.5)
end
function C:Rect()
    local addon=API:Status()
    local r=addon and self:DB().crops[addon]
    local w,h=self:Screen()
    if r and r.screenWidth==w and r.screenHeight==h then return r end
end
function C:SetRect(x,y,w,h)
    local addon=API:Status()
    if not addon or InCombatLockdown() or pending then return false end
    local sw,sh=self:Screen()
    x=math.max(0,math.min(sw-1,math.floor(x+.5)))
    y=math.max(0,math.min(sh-1,math.floor(y+.5)))
    w=math.min(sw-x,math.floor(w+.5)); h=math.min(sh-y,math.floor(h+.5))
    if w<16 or h<16 then API.Report('Draw a rectangle at least 16 pixels wide and tall.'); return false end
    self:DB().crops[addon]={x=x,y=y,width=w,height=h,screenWidth=sw,screenHeight=sh}
    return true
end
function C:Fit()
    local context=API.Presentation:GetContext()
    local config=context and context._presentation
    if not config then API.Report('This adapter has not registered its scene windows. Use Draw area.'); return end
    local sw,sh=self:Screen()
    local x,y,right,bottom=sw,sh,0,0
    for _,f in ipairs(config.frames) do
        if f:IsShown() and f:GetLeft() and f:GetTop() then
            local s=f:GetEffectiveScale()
            local l,t=f:GetLeft()*s,sh-f:GetTop()*s
            x=math.min(x,l); y=math.min(y,t)
            right=math.max(right,l+f:GetWidth()*s); bottom=math.max(bottom,t+f:GetHeight()*s)
        end
    end
    if right<=x or bottom<=y then API.Report('No visible scene bounds. Use Draw area.'); return end
    x=math.max(0,x-16); y=math.max(0,y-16)
    if self:SetRect(x,y,math.min(sw,right+16)-x,math.min(sh,bottom+16)-y) then self:ShowArea(false) end
end
function C:IsBusy() return pending~=nil end
function C:Name(record)
    if record.name then return record.name end
    local title=record.scene
    for _,row in ipairs(API:List()) do
        if row.addon==record.addon and row.id==record.scene then title=row.title; break end
    end
    local number=0
    for _,r in ipairs(self:DB().captures) do
        if r.addon==record.addon and r.scene==record.scene then number=number+1 end
        if r==record then break end
    end
    return title..' capture '..math.max(1,number)
end
local function restore()
    if C.overlay then C.overlay:Hide() end
    API.Presentation:ShowControls()
    if C.RefreshGallery then C:RefreshGallery() end
end
function C:Take()
    if pending then return end
    if blocked then API.Report('Screenshot completion timed out. Reload before trying again.'); return end
    local context=API.Presentation:GetContext()
    if not context or not context:IsActive() then API.Report('Start a scene outside combat first.'); return end
    local r=self:Rect()
    if not r then API.Report('Choose Draw area or Auto-fit area before capturing.'); return end
    if #self:DB().captures>=self.limit then API.Report('Capture list full. Send your batch, then remove old records.'); return end
    local copy={}; for k,v in pairs(r) do copy[k]=v end
    pending={context=context,rect=copy,delay=.25,age=0,frames=0}
    if self.overlay then self.overlay:Hide() end
    if self.gallery then self.gallery:Hide() end
    if API.ScenePicker then API.ScenePicker:Hide() end
    API:HideWindow(); API.Presentation:SuspendControls()
    if GameTooltip then GameTooltip:Hide() end
end
function C:Cancel()
    if self.overlay then self.overlay:Hide() end
    if pending then
        if pending.requestedAt then pending.interrupted=true
        else pending=nil; restore() end
    end
end
function C:Remove(id)
    if pending then return end
    local rows=self:DB().captures
    for i,r in ipairs(rows) do if r.id==id then table.remove(rows,i); break end end
    self:RefreshGallery()
end
function C:Export()
    if InCombatLockdown() or pending then API.Report('Wait until combat and capture finish before sending.'); return end
    API:Stop('capture-export')
    local _,_,deferred,fault=API:Status()
    if deferred or fault then API.Report('Scene restoration failed. Resolve it before sending the batch.'); return end
    local db=self:DB(); db.exportedAt=time()
    for _,r in ipairs(db.captures) do r.exported=true end
    ReloadUI()
end
local controller=CreateFrame('Frame')
C.controller=controller
controller:RegisterEvent('SCREENSHOT_SUCCEEDED'); controller:RegisterEvent('SCREENSHOT_FAILED')
controller:RegisterEvent('DISPLAY_SIZE_CHANGED'); controller:RegisterEvent('UI_SCALE_CHANGED')
controller:SetScript('OnEvent',function(_,event)
    if event=='DISPLAY_SIZE_CHANGED' or event=='UI_SCALE_CHANGED' then C:Cancel(); return end
    if not pending or not pending.requestedAt then return end
    local p=pending; pending=nil
    if event=='SCREENSHOT_SUCCEEDED' then
        local db=C:DB(); db.sequence=db.sequence+1
        local r=p.rect
        r.id=tostring(p.requestedAt)..'-'..tostring(db.sequence)
        r.addon=p.context.addonID; r.scene=p.context.sceneID
        local key=r.addon..'/'..r.scene
        local count=db.captureCounts[key] or 0
        for _,old in ipairs(db.captures) do
            if old.addon==r.addon and old.scene==r.scene then
                count=math.max(count,old.captureNumber or 0)
            end
        end
        if count==0 then
            for _,old in ipairs(db.captures) do if old.addon==r.addon and old.scene==r.scene then count=count+1 end end
        end
        r.captureNumber=count+1; db.captureCounts[key]=r.captureNumber
        local title=r.scene
        for _,row in ipairs(API:List()) do if row.addon==r.addon and row.id==r.scene then title=row.title; break end end
        r.name=title..' capture '..r.captureNumber
        r.requestedAt=p.requestedAt; r.completedAt=time()
        r.localTime=p.localTime; r.localCompleted=date('%m%d%y_%H%M%S',r.completedAt)
        r.review=p.interrupted or not p.context:IsActive() or nil
        db.captures[#db.captures+1]=r
        C:Flash(); API.Report(r.review and 'Screenshot captured after scene changed. Review it in the companion.' or 'Screenshot captured. Open Captures to send the batch.')
    else API.Report('WoW could not save the screenshot. Check free disk space and try again.') end
    restore()
end)
controller:SetScript('OnUpdate',function(_,delta)
    ticks=ticks+delta
    if C.flash and C.flash:IsShown() then
        C.flashAge=(C.flashAge or 0)+delta
        C.flash:SetAlpha(math.max(0,1-C.flashAge/.22))
        if C.flashAge>=.22 then C.flash:Hide() end
    end
    if not pending then return end
    local p=pending; p.age=p.age+delta; p.frames=p.frames+1
    if p.age>10 then pending=nil; blocked=true; restore(); API.Report('Screenshot timed out. Reload before another capture.'); return end
    if not p.requestedAt and p.age>=p.delay and p.frames>=2 then
        if not p.context:IsActive() then pending=nil; restore(); return end
        local sw,sh=C:Screen()
        if sw~=p.rect.screenWidth or sh~=p.rect.screenHeight then pending=nil; restore(); return end
        p.requestedAt=time(); p.localTime=date('%m%d%y_%H%M%S',p.requestedAt)
        local ok=pcall(Screenshot)
        if not ok then pending=nil; restore(); API.Report('Screenshot API failed. You can still capture manually.') end
    end
end)
