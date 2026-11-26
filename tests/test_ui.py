"""Behavior tests, not native rendering proof. Mock methods fail if unsupported."""
from pathlib import Path
import unittest
from test_lifecycle import runtime, ROOT


def ui_runtime():
    lua = runtime()
    lua.execute('''
        local methods={}
        function methods:SetSize(w,h) self.width=w;self.height=h end
        function methods:SetWidth(w) self.width=w end
        function methods:SetHeight(h) self.height=h end
        function methods:GetWidth() return self.width or 0 end
        function methods:GetHeight() return self.height or 0 end
        function methods:SetPoint(...) self.point={...} end
        function methods:ClearAllPoints() self.point=nil end
        function methods:GetEffectiveScale() return self.scale or 1 end
        function methods:GetLeft() return self.left or 100 end
        function methods:GetTop() return self.top or 800 end
        function methods:SetAllPoints() self.allPoints=true end
        function methods:SetFont(...) self.font={...} end
        function methods:SetTextColor(...) self.color={...} end
        function methods:SetShadowColor() end
        function methods:SetShadowOffset() end
        function methods:SetJustifyH() end
        function methods:SetJustifyV() end
        function methods:SetSpacing() end
        function methods:SetText(t) self.text=t; if self.label then self.label.text=t end end
        function methods:GetStringHeight()
            local lines=0
            for line in ((self.text or '')..'\n'):gmatch('(.-)\n') do
                lines=lines+math.max(1,math.ceil(#line/math.max(1,(self.width or 100)/8)))
            end
            return lines*19
        end
        function methods:SetTexture(path) self.texture=path end
        function methods:SetTexCoord(...) self.uv={...} end
        function methods:SetVertexColor(...) self.vertex={...} end
        function methods:SetAlpha(a) self.alpha=a end
        function methods:SetFontString(label) self.label=label end
        function methods:IsEnabled() return self.enabled~=false end
        function methods:Enable() self.enabled=true; self:Fire('OnEnable') end
        function methods:Disable() self.enabled=false; self:Fire('OnDisable') end
        function methods:Fire(event, ...) if self.scripts[event] then self.scripts[event](self, ...) end end
        function methods:Click() if self:IsEnabled() and self:IsShown() then self:Fire('OnClick') end end
        function methods:Show() local was=self.shown; self.shown=true; if not was then self:Fire('OnShow') end end
        function methods:Hide() local was=self.shown; self.shown=false; if was then self:Fire('OnHide') end end
        function methods:IsShown() return self.shown~=false end
        function methods:SetScript(event,fn) self.scripts[event]=fn end
        function methods:RegisterEvent(event) self.events[event]=true end
        function methods:SetFrameStrata(strata) self.strata=strata end
        function methods:GetFrameStrata() return self.strata or (self.parent and self.parent:GetFrameStrata()) or 'MEDIUM' end
        function methods:GetFrameLevel() return self.level or 0 end
        function methods:SetFrameLevel(value)
            if self.failLayer then error('Layer mutation failed') end
            if inCombat and self.protected then error('Protected mutation in combat') end
            self.level=value
        end
        function methods:GetChildren() return unpack(self.children or {}) end
        function methods:IsForbidden() return self.forbidden end
        function methods:SetColorTexture(...) self.color={...} end
        function methods:SetToplevel(value) self.toplevel=value end
        function methods:EnableMouse() end
        function methods:EnableMouseWheel() end
        function methods:SetClampedToScreen(value) self.clamped=value end
        function methods:SetMovable() end
        function methods:RegisterForDrag() end
        function methods:Raise() self.raised=(self.raised or 0)+1 end
        function methods:StartMoving() self.moving=true end
        function methods:StopMovingOrSizing() self.moving=false end
        function methods:SetScale(scale) self.scale=scale end
        function methods:SetScrollChild(child) self.child=child end
        function methods:SetVerticalScroll(value) self.scroll=value end
        function methods:GetVerticalScroll() return self.scroll or 0 end
        local function object(parent)
            local o=setmetatable({parent=parent, scripts={}, events={}, shown=true}, {__index=methods})
            return o
        end
        function methods:CreateFontString() return object(self) end
        function methods:CreateTexture() return object(self) end
        function CreateFrame(kind,name,parent)
            local f=object(parent); f.name=name; f.kind=kind
            if parent then parent.children=parent.children or {}; table.insert(parent.children,f) end
            if name then _G[name]=f end
            table.insert(frames,f); return f
        end
        UIParent=object(); UIParent:SetSize(1920,1080); UISpecialFrames={}
    '''.replace("'\n'", "'\\n'").replace("(.-)\n", "(.-)\\n"))
    for name in ('Theme.lua', 'UI.lua'):
        lua.execute((ROOT / 'ForeverShowcase' / name).read_text())
    return lua


class WindowBehavior(unittest.TestCase):
    def test_availability_changes_while_open(self):
        ui_runtime().execute('''
            local a=ForeverShowcase; local d=definition(); local ready=false
            d.scenes[1].available=function() return ready,'Waiting for dependency' end
            a:Register(1,d); a:ShowWindow(); local w=a.Window
            assert(not w.start:IsEnabled())
            ready=true; w:Fire('OnUpdate',1); assert(w.start:IsEnabled())
            ready=false; w:Fire('OnUpdate',1); assert(not w.start:IsEnabled())
        ''')

    def test_empty_and_window_ownership(self):
        ui_runtime().execute('''
            SlashCmdList.FOREVERSHOWCASE('')
            local w=ForeverShowcase.Window
            assert(w:IsShown() and w.toplevel and w.clamped and w.strata=='DIALOG')
            assert(w.heading.text=='No integrations yet'); assert(not w.start:IsEnabled())
            assert(not w.next:IsEnabled() and not w.stop:IsEnabled())
            assert(UISpecialFrames[1]=='ForeverShowcaseWindow')
            for _,b in ipairs(w.sceneRows) do assert(b.parent==w and not b:IsShown()) end
            SlashCmdList.FOREVERSHOWCASE('hide'); assert(not w:IsShown())
        ''')

    def test_selection_activation_hide_stop_and_combat(self):
        ui_runtime().execute('''
            local a=ForeverShowcase
            a:Register(1,definition()); a:ShowWindow(); local w=a.Window
            assert(not a:Status()); assert(w.heading.text=='One')
            w.sceneRows[2]:Click(); assert(w.heading.text=='Two' and not a:Status())
            w.start:Click(); local addon,scene=a:Status(); assert(scene=='two')
            assert(w.start.text=='Restart scene')
            w.hide:Click(); assert(not w:IsShown() and a:Status())
            a:ShowWindow(); w.close:Click(); assert(a:Status())
            a:ShowWindow(); w.stop:Click(); assert(not a:Status())
            w.sceneRows[1]:Click(); w.start:Click()
            inCombat=true; emit('PLAYER_REGEN_DISABLED'); w:Fire('OnUpdate',.3)
            assert(not w.start:IsEnabled() and not w.next:IsEnabled())
            assert(w.status.text:find('Restoration'))
            inCombat=false; emit('PLAYER_REGEN_ENABLED'); w:Fire('OnUpdate',.3)
            assert(w.start:IsEnabled() and w.status.text=='No active scene')
        ''')

    def test_unavailable_and_failed_entry(self):
        ui_runtime().execute('''
            local a=ForeverShowcase; local d=definition()
            d.scenes[1].available=function() return false,'Needs safe isolation' end
            d.scenes[2].enter=function() error('Entry failed') end
            a:Register(1,d); a:ShowWindow(); local w=a.Window
            assert(w.body.text:find('Needs safe isolation')); assert(not w.start:IsEnabled())
            w.sceneRows[2]:Click(); w.start:Click(); assert(not a:Status())
            assert(w.noticeLabel.text:find('Scene entry failed'))
        ''')

    def test_pagination_late_registration_long_text_and_viewport(self):
        ui_runtime().execute('''
            local a=ForeverShowcase; a:ShowWindow(); local w=a.Window
            for i=1,8 do
                local d=definition('addon'..i)
                for j=3,9 do
                    d.scenes[j]={id='scene'..j,title='Scene '..j,description=string.rep('Long content ',200),enter=function() end,leave=function() end}
                end
                assert(a:Register(1,d))
            end
            w:Fire('OnUpdate',.3); assert(w.addonPager:IsShown() and w.scenePager:IsShown())
            w.addonPager.next:Click(); assert(w.addonRows[1].id=='addon7')
            w.addonRows[1]:Click(); w.scenePager.next:Click(); assert(w.sceneRows[1].id=='scene7')
            w.sceneRows[1]:Click(); assert(w.scrollMax>0)
            w.scroll:Fire('OnMouseWheel',-10000); assert(w.scroll:GetVerticalScroll()==w.scrollMax)
            w.scroll:Fire('OnMouseWheel',10000); assert(w.scroll:GetVerticalScroll()==0)
            w.start:Click(); a:HideWindow(); a:ShowWindow()
            assert(w.addonRows[1].id=='addon7' and w.sceneRows[1].id=='scene7')
            assert(w.sceneRows[1].selected and w.addonRows[1].selected)
            UIParent:SetSize(800,600); a:HideWindow(); a:ShowWindow()
            assert(w.scale<1 and w.scale*1000<=760 and w.scale*760<=560)
        ''')


if __name__ == '__main__':
    unittest.main()
