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


if __name__ == '__main__':
    unittest.main()
