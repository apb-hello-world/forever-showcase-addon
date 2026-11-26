import unittest
from test_ui import ui_runtime
from test_lifecycle import ROOT


def presentation_runtime():
    lua=ui_runtime()
    for name in ('Presentation.lua','Capture.lua','CaptureUI.lua'):
        lua.execute((ROOT/'ForeverShowcase'/name).read_text())
    lua.execute('''
        function presentationDefinition(id)
            local d=definition(id)
            root=CreateFrame('Frame',nil,UIParent); root:SetFrameStrata('DIALOG'); root:SetFrameLevel(12)
            child=CreateFrame('Frame',nil,root); child:SetFrameStrata('HIGH'); child:SetFrameLevel(512)
            local original=d.scenes[1].enter
            d.scenes[1].enter=function(c)
                original(c)
                c:SetPresentation({frames={root},background={.2,.3,.4}})
            end
            return d
        end
    ''')
    return lua


class Presentation(unittest.TestCase):
    def test_toolbar_without_adapter_update_and_timer(self):
        presentation_runtime().execute('''
            local a=ForeverShowcase; a:Register(1,definition()); a:ShowWindow()
            assert(a:Start('test','one')); local p=a.Presentation; local t=p.toolbar
            assert(t:IsShown() and not a.Window:IsShown())
            assert(not t.background:IsEnabled())
            t.next:Click(); local _,scene=a:Status(); assert(scene=='two')
            t.previous:Click(); _,scene=a:Status(); assert(scene=='one')
            t.restart:Click(); assert(enters==3)
            t.hide:Click(); assert(not t:IsShown() and a:Status())
            p.controller:Fire('OnUpdate',9); assert(not t:IsShown())
            p.controller:Fire('OnUpdate',1); assert(t:IsShown())
            t.selector:Click(); assert(a.ScenePicker:IsShown() and not a.Window:IsShown())
            t.stop:Click(); assert(not a:Status()); assert(t:IsShown())
            assert(t.hide:IsEnabled() and t.hide.text=='Close toolbar')
            t.hide:Click(); assert(not t:IsShown())
        ''')

    def test_background_colors_layering_and_restore(self):
        presentation_runtime().execute('''
            local a=ForeverShowcase; a:Register(1,presentationDefinition())
            a:Start('test','one'); local p=a.Presentation
            assert(p:SetMode(2)); assert(p.backdrop:IsShown())
            assert(p.backdrop.fill.color[1]==.2)
            assert(root:GetFrameStrata()=='FULLSCREEN_DIALOG' and root:GetFrameLevel()==100)
            assert(child:GetFrameStrata()=='FULLSCREEN_DIALOG' and child:GetFrameLevel()==600)
            assert(p:SetMode(4)); assert(p.backdrop.fill.color[1]==.94)
            assert(p:SetMode(1)); assert(not p.backdrop:IsShown())
            assert(root:GetFrameStrata()=='DIALOG' and root:GetFrameLevel()==12)
            assert(child:GetFrameStrata()=='HIGH' and child:GetFrameLevel()==512)
            assert(p:SetMode(3)); assert(a:Stop()); assert(not p.backdrop:IsShown())
            assert(root:GetFrameStrata()=='DIALOG' and child:GetFrameLevel()==512)
        ''')

    def test_combat_clears_stage_and_defers_layers(self):
        presentation_runtime().execute('''
            local a=ForeverShowcase; a:Register(1,presentationDefinition()); a:Start('test','one')
            local p=a.Presentation; p:SetMode(2); p:HideForCapture()
            root.protected=true; child.protected=true
            inCombat=true; emit('PLAYER_REGEN_DISABLED'); p.controller:Fire('OnUpdate',.3)
            assert(not p.backdrop:IsShown() and p.toolbar:IsShown())
            assert(root:GetFrameStrata()=='FULLSCREEN_DIALOG')
            assert(not p.toolbar.background:IsEnabled()); assert(not p:SetMode(3))
            inCombat=false; emit('PLAYER_REGEN_ENABLED')
            assert(root:GetFrameStrata()=='DIALOG' and child:GetFrameStrata()=='HIGH')
            p.controller:Fire('OnUpdate',20); assert(not a:Status())
        ''')

    def test_scene_switch_and_entry_failure_remove_background(self):
        presentation_runtime().execute('''
            local a=ForeverShowcase; local d=presentationDefinition()
            d.scenes[2].enter=function() error('entry') end
            a:Register(1,d); a:Start('test','one'); local p=a.Presentation
            p:SetMode(2); p:HideForCapture(); assert(not a:Next())
            assert(not p.backdrop:IsShown() and root:GetFrameStrata()=='DIALOG')
            p.controller:Fire('OnUpdate',20); assert(not a:Status())
        ''')

    def test_invalid_presentation_fails_before_mutation(self):
        for opts in ('{frames={UIParent}}','{frames={root},background={2,0,0}}','{frames={}}'):
            presentation_runtime().execute('''
                local a=ForeverShowcase; local d=presentationDefinition()
                d.scenes[1].enter=function(c) c:SetPresentation(OPTIONS) end
                a:Register(1,d); assert(not a:Start('test','one'))
                assert(root:GetFrameStrata()=='DIALOG')
            '''.replace('OPTIONS',opts))

    def test_restore_failure_faults_and_attempts_other_frames(self):
        presentation_runtime().execute('''
            local a=ForeverShowcase; a:Register(1,presentationDefinition()); a:Start('test','one')
            local p=a.Presentation; p:SetMode(2); root.failLayer=true
            assert(not a:Stop()); assert(child:GetFrameLevel()==512)
            local _,_,_,fault=a:Status(); assert(fault)
            assert(not p.backdrop:IsShown()); assert(not a:Start('test','two'))
        ''')


    def test_navigation_stops_at_available_scene_boundaries(self):
        presentation_runtime().execute("""
            local a=ForeverShowcase
            local d=definition()
            d.scenes[2].enter=function() enters=(enters or 0)+1 end
            d.scenes[3]={id='unavailable',title='Unavailable',enter=function() error('must skip') end,leave=function() end,available=function() return false,'Not ready' end}
            a:Register(1,d); assert(a:Start('test','one'))
            local t=a.Presentation.toolbar
            assert(not t.previous:IsEnabled() and t.next:IsEnabled())
            assert(not a:Previous()); assert(select(2,a:Status())=='one')
            t.next:Click(); assert(select(2,a:Status())=='two')
            assert(not t.next:IsEnabled() and t.previous:IsEnabled())
            local before=enters; assert(not a:Next()); t.next:Click(); assert(enters==before)
            a:ShowWindow(); assert(not a.Window.next:IsEnabled())
            t.restart:Click(); assert(enters==before+1)
            t.previous:Click(); assert(select(2,a:Status())=='one')
            d=definition('single'); d.scenes={d.scenes[1]}; a:Register(1,d)
            assert(a:Start('single','one'))
            assert(not t.next:IsEnabled() and not t.previous:IsEnabled() and t.restart:IsEnabled())
        """)
