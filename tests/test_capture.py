import unittest
from test_ui import ui_runtime, ROOT


def capture_runtime():
    lua = ui_runtime()
    lua.execute('''
        function UIParent:GetEffectiveScale() return .8 end
        function GetPhysicalScreenSize() return 1920,1080 end
        now=1800000000
        function time() return now end
        function date(_,stamp) return '112526_130000' end
        function Screenshot() screenshots=(screenshots or 0)+1 end
        function ReloadUI() reloaded=true end
        function GetCursorPosition() return 400,400 end
    ''')
    for name in ('Presentation.lua', 'Capture.lua', 'CaptureUI.lua'):
        lua.execute((ROOT/'ForeverShowcase'/name).read_text())
    lua.execute('''
        local a=ForeverShowcase
        a:Register(1,definition()); assert(a:Start('test','one'))
        c=a.Capture
        assert(c:SetRect(100,200,600,400))
    ''')
    return lua


class Capture(unittest.TestCase):
    def test_compact_gallery_filters_and_removes(self):
        capture_runtime().execute("""
            c:DB().captures={{id='one',name='Overview capture 1',addon='test',scene='one',width=400,height=600},
                {id='other',addon='other',scene='one',width=400,height=600}}
            c:ShowGallery()
            assert(c.gallery:GetWidth()==470 and not c.gallery.diagram)
            assert(c.gallery.rows[1].label.text=='Overview capture 1')
            assert(not c.gallery.rows[2]:IsShown())
            c.gallery.rows[1].remove:Click()
            assert(#c:DB().captures==1 and c:DB().captures[1].id=='other')
        """)

    def test_scene_picker_select_then_start(self):
        capture_runtime().execute("""
            local a=ForeverShowcase
            a:ShowScenePicker(); local w=a.ScenePicker
            assert(w:IsShown() and (not a.Window or not a.Window:IsShown()))
            w.rows[2]:Click(); assert(select(2,a:Status())=='one')
            w.start:Click(); assert(select(2,a:Status())=='two' and not w:IsShown())
        """)

    def test_confirmed_capture_and_export(self):
        capture_runtime().execute('''
            local a=ForeverShowcase
            c:Take(); assert(c:IsBusy() and not a.Presentation.toolbar:IsShown())
            c.controller:Fire('OnUpdate',.3); assert(not screenshots)
            c.controller:Fire('OnUpdate',.1); assert(screenshots==1)
            assert(#c:DB().captures==0 and not c.flash)
            c.controller:Fire('OnEvent','SCREENSHOT_SUCCEEDED')
            assert(#c:DB().captures==1 and c.flash:IsShown())
            local r=c:DB().captures[1]
            assert(r.x==100 and r.y==200 and r.width==600 and not r.exported)
            assert(r.addonTitle=='Test')
            assert(a.Presentation.toolbar:IsShown())
            c:Export(); assert(reloaded and r.exported and not a:Status())
        ''')

    def test_failure_timeout_and_late_event(self):
        capture_runtime().execute('''
            c:Take(); c.controller:Fire('OnUpdate',.3); c.controller:Fire('OnUpdate',.1)
            c.controller:Fire('OnEvent','SCREENSHOT_FAILED'); assert(#c:DB().captures==0)
            c:Take(); c.controller:Fire('OnUpdate',.3); c.controller:Fire('OnUpdate',.1)
            c.controller:Fire('OnUpdate',11); assert(not c:IsBusy())
            c:Take(); assert(not c:IsBusy())
            c.controller:Fire('OnEvent','SCREENSHOT_SUCCEEDED'); assert(#c:DB().captures==0)
        ''')

    def test_combat_cancellation_and_interruption(self):
        capture_runtime().execute('''
            c:Take(); inCombat=true; emit('PLAYER_REGEN_DISABLED')
            c.controller:Fire('OnUpdate',1); assert(not screenshots and not c:IsBusy())
            inCombat=false; emit('PLAYER_REGEN_ENABLED')
            ForeverShowcase:Start('test','one'); c:Take()
            c.controller:Fire('OnUpdate',.3); c.controller:Fire('OnUpdate',.1)
            ForeverShowcase:Stop(); c.controller:Fire('OnEvent','SCREENSHOT_SUCCEEDED')
            assert(c:DB().captures[1].review)
        ''')

    def test_bounds_resolution_reuse_and_gallery(self):
        capture_runtime().execute('''
            assert(not c:SetRect(0,0,4,4))
            assert(c:SetRect(1900,1060,500,500)); assert(c:Rect().width==20)
            ForeverShowcase:Next(); assert(c:Rect().x==1900)
            c:ShowArea(false); assert(c.overlay:IsShown())
            c.overlay:Hide()
            c:ShowGallery(); assert(c.gallery:IsShown())
            function GetPhysicalScreenSize() return 2560,1440 end
            assert(not c:Rect()); c:Take(); assert(not c:IsBusy())
        ''')

    def test_fit_normalizes_physical_resolution_and_frame_scale(self):
        capture_runtime().execute("""
            UIParent:SetSize(1600,900)
            function GetPhysicalScreenSize() return 3840,2160 end
            local f=CreateFrame('Frame',nil,UIParent)
            f:SetScale(.4); f.left=800; f.top=1200; f:SetSize(400,200)
            ForeverShowcase.Presentation:GetContext():SetPresentation({frames={f}})
            c:Fit(); local r=c:Rect()
            assert(r.x==944 and r.y==704 and r.width==512 and r.height==272)
            assert(c.overlay:IsShown())
            c.overlay:Hide(); assert(c:SetFitPadding(0)); c:Fit(); r=c:Rect()
            assert(r.x==960 and r.y==720 and r.width==480 and r.height==240)
            c.overlay:Hide()
            local t=ForeverShowcase.Presentation.toolbar
            t.paddingMore:Click(); assert(c:FitPadding()==4 and c:DB().fitPadding==4)
            c:Fit(); r=c:Rect(); assert(r.x==956 and r.width==488)
            c.overlay:Hide(); c:SetFitPadding(999); assert(c:FitPadding()==256)
            inCombat=true; assert(not c:SetFitPadding(12)); assert(c:FitPadding()==256)
        """)

    def test_fit_unions_roots_and_clips_padding_at_screen_edges(self):
        capture_runtime().execute("""
            UIParent:SetSize(2400,1350)
            local f=CreateFrame('Frame',nil,UIParent)
            f:SetScale(.8); f.left=0; f.top=1350; f:SetSize(100,100)
            local other=CreateFrame('Frame',nil,UIParent)
            other:SetScale(.8); other.left=200; other.top=1200; other:SetSize(100,100)
            ForeverShowcase.Presentation:GetContext():SetPresentation({frames={f,other}})
            c:Fit(); local r=c:Rect()
            assert(r.x==0 and r.y==0 and r.width==256 and r.height==216)
        """)

    def test_gallery_addon_dropdown_filters_and_removal(self):
        capture_runtime().execute("""
            c:DB().captures={
                {id='a1',name='Alpha old',addon='a',addonTitle='Alpha',scene='one',width=400,height=600},
                {id='z',name='Zulu',addon='z',addonTitle='Zulu',scene='one',width=400,height=600},
                {id='a2',name='Alpha new',addon='a',addonTitle='Alpha',scene='one',width=400,height=600}}
            c:ShowGallery(); c.gallery.filter:Click()
            c.gallery.addons:Click(); assert(c.gallery.addonMenu:IsShown())
            c.gallery.addonMenu.rows[2]:Click()
            assert(not c.gallery.addonMenu:IsShown())
            assert(c.gallery.rows[1].remove.id=='a2' and c.gallery.rows[2].remove.id=='a1')
            assert(not c.gallery.rows[3]:IsShown())
            c.gallery.rows[2].remove:Click(); assert(not c.gallery.rows[2]:IsShown())
            c.gallery.addons:Click(); c.gallery.addonMenu.rows[3]:Click()
            assert(c.gallery.rows[1].remove.id=='z' and not c.gallery.rows[2]:IsShown())
            c.gallery.addons:Click(); c.gallery.addonMenu.rows[1]:Click()
            assert(c.gallery.rows[1].remove.id=='a2' and c.gallery.rows[2].remove.id=='z')
            c.gallery.addons:Click(); c.gallery:Hide(); assert(not c.gallery.addonMenu:IsShown())
        """)

    def test_gallery_dropdown_scrolls_to_additional_addons(self):
        capture_runtime().execute("""
            for i=1,10 do c:DB().captures[i]={id='r'..i,addon=string.format('addon%02d',i),scene='one',width=100,height=100} end
            c:ShowGallery(); c.gallery.filter:Click(); c.gallery.addons:Click()
            c.gallery.addonMenu:Fire('OnMouseWheel',-20)
            c.gallery.addonMenu.rows[6]:Click()
            assert(c.gallery.rows[1].remove.id=='r10' and not c.gallery.rows[2]:IsShown())
            c.gallery.rows[1].remove:Click()
            assert(c.gallery.addons.text=='All addons  v')
        """)


if __name__ == '__main__':
    unittest.main()
