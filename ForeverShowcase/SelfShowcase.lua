-- Stage the real Showcase UI. Sample capture rows never enter SavedVariables.
local API,C=ForeverShowcase,ForeverShowcase.Capture
local function enter(kind)
    return function(context)
        local selectorState=API:SelectorState()
        local subjects={}; local root,shield,extra
        local previousMode=API.Presentation.mode
        context:AddCleanup(function()
            C.sampleRecords=nil; API._screenshotSubjects=nil
            if shield then shield:Hide() end
            if root then root:Hide() end
            if extra then extra:Hide() end
            API.Presentation.mode=previousMode
        end,false) -- addon-owned unprotected UI and pure Lua fixtures
        context:AddCleanup(function() API:RestoreSelectorState(selectorState) end)
        API._screenshotSubjects=subjects
        if kind=='toolbar' then
            root=API.Presentation:CreateSubjectToolbar()
        elseif kind=='framing' then
            API:ShowScenePicker(); root=API.ScenePicker
            extra=C:CreateFramingSubject()
            extra:SetScale(root:GetEffectiveScale()/UIParent:GetEffectiveScale())
        elseif kind=='selector' or kind=='charcoal' or kind=='ivory' then
            API:ShowWindow(); root=API.Window
        elseif kind=='scenes' then
            API:ShowScenePicker(); root=API.ScenePicker
        else
            C.sampleRecords={}
            for i,title in ipairs({'Scene library','Choose a scene','Clean captures','Repeatable framing','Gallery-ready images'}) do
                C.sampleRecords[i]={id='self-sample-'..i,addon='forever-showcase',addonTitle='Forever Showcase',
                    scene='captures',name=title..' capture 1',width=1200,height=900,exported=i<4}
            end
            C:ShowGallery(); root=C.gallery
        end
        subjects[root]=true
        if extra then subjects[extra]=true end
        if kind=='charcoal' then API.Presentation.mode=3 elseif kind=='ivory' then API.Presentation.mode=4 end
        -- Capture-only composition: controls on the photographed window are inert.
        shield=CreateFrame('Frame',nil,root); shield:SetAllPoints(root)
        shield:SetFrameLevel(root:GetFrameLevel()+40); shield:EnableMouse(true); shield:EnableMouseWheel(true)
        shield:SetScript('OnMouseWheel',function() end)
        context:SetPresentation({frames=extra and {root,extra} or {root},background={.09,.07,.06}})
    end
end
local function leave() end
local scenes={}
for _,entry in ipairs({
    {'selector','Scene library','Discover supported addons and their screenshot scenes.','Stage real addon interfaces from one place.'},
    {'scenes','Scene picker','Choose the next scene using the compact picker.','Move between feature scenes without reopening the main window.'},
    {'toolbar','Scene controls','A staged copy of the real toolbar, separate from the operating controls.','Navigate, frame and capture without extra commands.'},
    {'framing','Repeatable framing','The real scene picker with a staged framing guide that remains in the screenshot.','Reuse a consistent capture rectangle across scenes.'},
    {'charcoal','Charcoal backdrop','The scene library presented against a clean charcoal backdrop.','Keep the focus on your addon UI.'},
    {'ivory','Ivory backdrop','The same scene library presented against a light ivory backdrop.','Choose a background that complements your artwork.'},
    {'captures','Capture records','A sample capture list demonstrates named captures and transfer status.','Review captures before sending them to the optional desktop companion.'},
}) do
    scenes[#scenes+1]={id=entry[1],title=entry[2],description=entry[3],caption=entry[4],
        instructions='Use Auto-fit area, choose a backdrop, then Capture. Stop the scene before opening Captures to Send & reload. This staged window is read-only.',
        available=function() return not InCombatLockdown(),'Leave combat before staging Showcase.' end,
        enter=enter(entry[1]),leave=leave}
end
local registered=false
function API:ShowSelfScenes()
    if not registered then
        local ok,reason=self:Register(1,{id='forever-showcase',title='Forever Showcase',scenes=scenes})
        if not ok then self.Report(reason); return end
        registered=true
    end
    self._showSelfInSelector=true
    self:ShowWindow('forever-showcase')
end
