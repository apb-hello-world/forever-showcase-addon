local API,ui=ForeverShowcase,ForeverShowcase.Theme
local C=API.Capture
local function box(parent,x,y,w,h,r,g,b,a)
    local t=parent:CreateTexture(nil,'ARTWORK')
    t:SetPoint('TOPLEFT',x,-y); t:SetSize(math.max(.01,w),math.max(.01,h)); t:SetColorTexture(r,g,b,a)
    return t
end
function C:Flash()
    if not self.flash then
        self.flash=CreateFrame('Frame',nil,UIParent); self.flash:SetAllPoints(UIParent)
        self.flash:SetFrameStrata('TOOLTIP'); self.flash:SetFrameLevel(600)
        local t=self.flash:CreateTexture(nil,'OVERLAY'); t:SetAllPoints(); t:SetColorTexture(1,.94,.8,.3)
    end
    self.flashAge=0; self.flash:SetAlpha(1); self.flash:Show()
end
local function cursor()
    local x,y=GetCursorPosition(); local s=UIParent:GetEffectiveScale()
    local sw,sh=C:Screen()
    return math.max(0,math.min(sw,x/s/UIParent:GetWidth()*sw)),math.max(0,math.min(sh,(1-y/s/UIParent:GetHeight())*sh))
end
local function paint(f,r,width,height)
    local w,h=width or UIParent:GetWidth(),height or UIParent:GetHeight()
    local x,y,rw,rh=r.x/r.screenWidth*w,r.y/r.screenHeight*h,r.width/r.screenWidth*w,r.height/r.screenHeight*h
    local areas={{0,0,w,y},{0,y,x,rh},{x+rw,y,w-x-rw,rh},{0,y+rh,w,h-y-rh},
        {x,y,rw,1},{x,y+rh-1,rw,1},{x,y,1,rh},{x+rw-1,y,1,rh}}
    for i,a in ipairs(areas) do
        local t=f.parts[i]; t:ClearAllPoints(); t:SetPoint('TOPLEFT',a[1],-a[2]); t:SetSize(math.max(.01,a[3]),math.max(.01,a[4]))
    end
end
function C:CreateFramingSubject()
    local f=CreateFrame('Frame',nil,UIParent)
    f:SetSize(760,560); f:SetPoint('CENTER'); f:SetFrameStrata('DIALOG')
    f.parts={}
    for i=1,8 do f.parts[i]=box(f,0,0,1,1,i>4 and .9 or 0,i>4 and .7 or 0,i>4 and .3 or 0,i>4 and 1 or .65) end
    paint(f,{x=54,y=50,width=652,height=460,screenWidth=760,screenHeight=560},760,560)
    ui.Label(f,'Repeatable framing  |  16 px padding',14,54,20,652,24,true)
    return f
end
function C:ShowArea(draw)
    if self:IsBusy() or InCombatLockdown() or not API:Status() then return end
    if not draw and not self:Rect() then API.Report('Draw an area first.'); return end
    if not self.overlay then
        local f=CreateFrame('Frame','ForeverShowcaseFraming',UIParent); self.overlay=f
        f:SetAllPoints(UIParent); f:SetFrameStrata('TOOLTIP'); f:SetFrameLevel(400); f:EnableMouse(true)
        f.parts={}
        for i=1,8 do f.parts[i]=box(f,0,0,1,1,i>4 and .9 or 0,i>4 and .7 or 0,i>4 and .3 or 0,i>4 and 1 or .65) end
        f.label=ui.Label(f,'',16,40,40,800,50,true)
        f:SetScript('OnMouseDown',function(self,button)
            if button=='RightButton' then self:Hide(); API.Presentation:ShowControls(); return end
            if self.draw then self.x,self.y=cursor() else self:Hide(); API.Presentation:ShowControls() end
        end)
        f:SetScript('OnUpdate',function(self)
            if not self.x then return end
            local x,y=cursor(); local sw,sh=C:Screen()
            self.rect={x=math.min(x,self.x),y=math.min(y,self.y),width=math.abs(x-self.x),height=math.abs(y-self.y),screenWidth=sw,screenHeight=sh}
            paint(self,self.rect)
            self.label:SetText(string.format('%.0f x %.0f pixels  |  Release to keep  |  Right-click / Escape to cancel',self.rect.width,self.rect.height))
        end)
        f:SetScript('OnMouseUp',function(self,button)
            if button=='LeftButton' and self.x then
                local x,y=cursor()
                C:SetRect(math.min(x,self.x),math.min(y,self.y),math.abs(x-self.x),math.abs(y-self.y))
                self:Hide(); API.Presentation:ShowControls()
            end
        end)
        f:SetScript('OnHide',function(self) self.x=nil; self.rect=nil; API.Presentation:ShowControls() end)
        table.insert(UISpecialFrames,'ForeverShowcaseFraming')
    end
    API:HideWindow(true); if self.gallery and not API:IsScreenshotSubject(self.gallery) then self.gallery:Hide() end
    API.Presentation:SuspendControls()
    local f=self.overlay; f.draw=draw; f.x=nil; f.rect=nil
    local sw,sh=self:Screen()
    paint(f,self:Rect() or {x=sw*.2,y=sh*.2,width=sw*.6,height=sh*.6,screenWidth=sw,screenHeight=sh})
    f.label:SetText(draw and 'Drag an area to crop. Right-click or Escape cancels.' or 'LIVE framing guide, not a saved image. Click or Escape to close.')
    f:Show()
end
local page,showAll,addonFilter=1,false,nil
function C:GalleryRecords()
    return self.sampleRecords or self:DB().captures
end
function C:RefreshGallery()
    local w=self.gallery; if not w then return end
    local addon,scene=API:Status()
    local titles={}
    for _,r in ipairs(self:GalleryRecords()) do titles[r.addon]=r.addonTitle or titles[r.addon] or r.addon end
    if addonFilter and not titles[addonFilter] then addonFilter=nil end
    w.addonOptions={{title='All addons'}}
    local options={}
    for id,title in pairs(titles) do options[#options+1]={id=id,title=title} end
    table.sort(options,function(a,b) if a.title==b.title then return a.id<b.id end return a.title<b.title end)
    for _,option in ipairs(options) do w.addonOptions[#w.addonOptions+1]=option end
    local all=showAll or not addon
    local records={}
    for i=#self:GalleryRecords(),1,-1 do
        local r=self:GalleryRecords()[i]
        if (all and (not addonFilter or r.addon==addonFilter)) or (not all and r.addon==addon and r.scene==scene) then records[#records+1]=r end
    end
    w.addons:SetText((titles[addonFilter] or 'All addons')..'  v')
    w.addons.tip=titles[addonFilter] or 'Choose an addon to filter captures.'
    if all then w.addons:Show(); w.scope:Hide() else w.addons:Hide(); w.scope:Show(); w.addonMenu:Hide() end
    page=math.max(1,math.min(page,math.ceil(#records/6)))
    w.title:SetText((showAll or not addon) and 'All captures' or 'Scene captures')
    w.scope:SetText(addon and not showAll and (addon..' / '..scene) or 'All scenes and addons')
    w.filter:SetText(showAll and 'This scene' or 'All captures')
    for i,b in ipairs(w.rows) do
        local r=records[(page-1)*6+i]
        if r then
            b.label:SetText(self:Name(r)); b.info:SetText(((showAll or not addon) and ((r.addonTitle or r.addon)..'  -  ') or '')..r.width..' x '..r.height..'  -  '..(r.exported and 'Sent' or 'Pending send'))
            b.remove.id=r.id; b:Show()
            if self.sampleRecords or self:IsBusy() then b.remove:Disable() else b.remove:Enable() end
        else b:Hide() end
    end
    if w.addonMenu:IsShown() then self:RefreshAddonMenu() end
    w.empty:SetText(#records==0 and 'No captures in this view yet.' or '')
    w.count:SetText(string.format('%d captures  |  Page %d / %d',#records,page,math.max(1,math.ceil(#records/6))))
    if page>1 then w.previous:Enable() else w.previous:Disable() end
    if page*6<#records then w.next:Enable() else w.next:Disable() end
    if not self.sampleRecords and #self:GalleryRecords()>0 and not self:IsBusy() and not InCombatLockdown() then w.send:Enable() else w.send:Disable() end
end
function C:RefreshAddonMenu()
    local w=self.gallery; if not w then return end
    w.menuOffset=math.min(w.menuOffset or 0,math.max(0,#w.addonOptions-6))
    for i,b in ipairs(w.addonMenu.rows) do
        local option=w.addonOptions[(w.menuOffset or 0)+i]
        if option then b.addonID=option.id; b:SetText(option.title); b.tip=option.title; b:SetSelected(addonFilter==option.id); b:Show() else b:Hide() end
    end
    if #w.addonOptions>6 then w.addonMenu.hint:Show() else w.addonMenu.hint:Hide() end
    w.addonMenu:SetHeight(math.min(6,#w.addonOptions)*32+8+(#w.addonOptions>6 and 20 or 0))
end
function C:ShowGallery()
    if self:IsBusy() then return end
    if not self.gallery then
        local w=ui.CompactWindow('ForeverShowcaseCaptures','Scene captures',470,480); self.gallery=w
        w.scope=ui.Label(w,'',13,18,62,300,25,true)
        w.filter=w:Button('All captures',326,58,126,function() showAll=not showAll; page=1; C:RefreshGallery() end)
        w.addons=w:Button('All addons  v',18,58,300,function()
            if w.addonMenu:IsShown() then w.addonMenu:Hide()
            else w.menuOffset=0; C:RefreshAddonMenu(); w.addonMenu:Show() end
        end)
        local menu=CreateFrame('Frame','ForeverShowcaseCaptureAddonMenu',w); w.addonMenu=menu
        menu:SetPoint('TOPLEFT',18,-90); menu:SetSize(300,216); menu:SetFrameLevel(w:GetFrameLevel()+20); menu:EnableMouse(true)
        local fill=menu:CreateTexture(nil,'BACKGROUND'); fill:SetAllPoints(); fill:SetColorTexture(.12,.075,.045,1)
        menu.rows={}
        for i=1,6 do
            local item=ui.Button(menu,'',292,30); item:SetPoint('TOPLEFT',4,-(4+(i-1)*32))
            item:SetFrameLevel(menu:GetFrameLevel()+1)
            item:SetScript('OnClick',function(self) addonFilter=self.addonID; page=1; menu:Hide(); C:RefreshGallery() end)
            menu.rows[i]=item
        end
        menu.hint=ui.Label(menu,'Scroll for more addons',11,8,198,284,16,true)
        menu:EnableMouseWheel(true)
        menu:SetScript('OnMouseWheel',function(_,delta)
            w.menuOffset=math.max(0,math.min(math.max(0,#w.addonOptions-6),(w.menuOffset or 0)-delta)); C:RefreshAddonMenu()
        end)
        table.insert(UISpecialFrames,'ForeverShowcaseCaptureAddonMenu')
        w:SetScript('OnHide',function(self) self:StopMovingOrSizing(); menu:Hide() end)
        menu:Hide()
        w.rows={}
        for i=1,6 do
            local row=CreateFrame('Frame',nil,w); row:SetSize(434,44); row:SetPoint('TOPLEFT',18,-(100+(i-1)*46))
            row.label=ui.Label(row,'',14,0,0,388,22,true)
            row.info=ui.Label(row,'',12,0,23,388,18,true)
            row.remove=ui.Button(row,'X',30,28); row.remove:SetPoint('TOPRIGHT',0,-4)
            row.remove.tip='Remove this capture record. The original screenshot stays on disk.'
            row.remove:SetScript('OnClick',function(self) C:Remove(self.id) end)
            w.rows[i]=row
        end
        w.empty=ui.Label(w,'',14,18,115,410,40,true)
        w.count=ui.Label(w,'',12,18,384,236,25,true)
        w.previous=w:Button('Previous',274,378,84,function() page=page-1; C:RefreshGallery() end)
        w.next=w:Button('Next',366,378,84,function() page=page+1; C:RefreshGallery() end)
        ui.Label(w,'Send all captures to the companion and reload the UI.',12,18,420,268,40,true)
        w.send=w:Button('Send & reload',300,426,150,function() C:Export() end)
        local elapsed=0
        w:SetScript('OnUpdate',function(_,delta) elapsed=elapsed+delta; if elapsed>.3 then elapsed=0; C:RefreshGallery() end end)
    end
    API:HideWindow(true); if API.ScenePicker and not API:IsScreenshotSubject(API.ScenePicker) then API.ScenePicker:Hide() end
    self.gallery:Show(); self:RefreshGallery()
end

local scenePage,chosen,pickerAddon=1,nil,nil
function API:RefreshScenePicker()
    local w=self.ScenePicker; if not w then return end
    local addon=self:Status() or self.Presentation.lastAddon
    if addon~=pickerAddon then pickerAddon=addon; chosen=nil; scenePage=1 end
    local rows={}
    for _,r in ipairs(self:List()) do if r.addon==addon then rows[#rows+1]=r end end
    local current=select(2,self:Status())
    if not chosen then chosen=current or (rows[1] and rows[1].id) end
    local selected
    for _,r in ipairs(rows) do if r.id==chosen then selected=r end end
    w.title:SetText((rows[1] and rows[1].addonTitle or 'Addon')..' scenes')
    scenePage=math.max(1,math.min(scenePage,math.ceil(#rows/6)))
    for i,b in ipairs(w.rows) do
        local r=rows[(scenePage-1)*6+i]
        if r then b.id=r.id; b:SetText(r.title); b.tip=r.title; b:SetSelected(chosen==r.id); b:Show() else b:Hide() end
    end
    w.heading:SetText(selected and selected.title or 'No scenes available')
    local body=selected and (selected.description or 'No description provided.') or 'Start an addon from the main Showcase window first.'
    if selected and not selected.available then body='Unavailable: '..tostring(selected.reason)..'\n\n'..body end
    if chosen~=w.detailID then w.scroll:SetVerticalScroll(0); w.detailID=chosen end
    w.body:SetText(body); w.body:SetHeight(0)
    local h=math.max(232,w.body:GetStringHeight()+8); w.body:SetHeight(h); w.content:SetHeight(h); w.scrollMax=h-232
    w.pages:SetText(scenePage..' / '..math.max(1,math.ceil(#rows/6)))
    if scenePage>1 then w.previous:Enable() else w.previous:Disable() end
    if scenePage*6<#rows then w.next:Enable() else w.next:Disable() end
    local _,_,pending,fault=self:Status()
    if selected and selected.available and not InCombatLockdown() and not pending and not fault and not C:IsBusy() then w.start:Enable() else w.start:Disable() end
end
function API:ShowScenePicker()
    if C:IsBusy() then return end
    if not self.ScenePicker then
        local w=ui.CompactWindow('ForeverShowcaseScenePicker','Scenes',620,428); self.ScenePicker=w
        w.rows={}
        for i=1,6 do
            local b=ui.Button(w,'',210,38,'row'); b.dark=true; b:SetPoint('TOPLEFT',18,-(68+(i-1)*46))
            b:SetScript('OnClick',function(self) chosen=self.id; API:RefreshScenePicker() end); w.rows[i]=b
        end
        w.heading=ui.Label(w,'',18,250,68,350,48,true)
        w.scroll=CreateFrame('ScrollFrame',nil,w); w.scroll:SetPoint('TOPLEFT',250,-126); w.scroll:SetSize(350,232)
        w.content=CreateFrame('Frame',nil,w.scroll); w.content:SetSize(350,232); w.scroll:SetScrollChild(w.content)
        w.body=ui.Label(w.content,'',14,0,0,344,232,true)
        w.scroll:EnableMouseWheel(true); w.scroll:SetScript('OnMouseWheel',function(self,delta) self:SetVerticalScroll(math.max(0,math.min(w.scrollMax or 0,self:GetVerticalScroll()-delta*36))) end)
        w.previous=w:Button('Previous',18,350,80,function() scenePage=scenePage-1; API:RefreshScenePicker() end)
        w.pages=ui.Label(w,'',12,106,358,40,22,true)
        w.next=w:Button('Next',152,350,76,function() scenePage=scenePage+1; API:RefreshScenePicker() end)
        w.start=w:Button('Start scene',440,382,160,function()
            local ok,message=API:Start(pickerAddon,chosen)
            if ok then w:Hide() elseif message then API.Report(message) end
            API:RefreshScenePicker()
        end)
        local elapsed=0
        w:SetScript('OnUpdate',function(_,delta) elapsed=elapsed+delta; if elapsed>.5 then elapsed=0; API:RefreshScenePicker() end end)
    end
    self:HideWindow(); if C.gallery then C.gallery:Hide() end
    chosen=select(2,self:Status()); scenePage=1
    self.ScenePicker:Show(); self:RefreshScenePicker()
end
