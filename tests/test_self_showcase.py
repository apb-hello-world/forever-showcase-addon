import unittest
from test_capture import capture_runtime
from test_ui import ROOT

class SelfShowcase(unittest.TestCase):
    def runtime(self, reveal=True):
        lua=capture_runtime()
        lua.execute((ROOT/'ForeverShowcase/SelfShowcase.lua').read_text(encoding='utf-8'))
        if reveal:lua.execute('ForeverShowcase:ShowSelfScenes()')
        return lua

    def test_real_subjects_survive_capture_controls_and_clean_up(self):
        self.runtime().execute("""
            local a=ForeverShowcase
            for _,id in ipairs({'selector','scenes','captures','toolbar','framing','charcoal','ivory'}) do
                assert(a:Start('forever-showcase',id))
                local context=a.Presentation:GetContext()
                local root=context._presentation.frames[1]
                assert(root:IsShown() and a:IsScreenshotSubject(root))
                assert(c:SetRect(100,100,400,300))
                c:Take(); assert(root:IsShown() and not a.Presentation.toolbar:IsShown())
                c.controller:Fire('OnUpdate',.3); c.controller:Fire('OnUpdate',.1)
                c.controller:Fire('OnEvent','SCREENSHOT_SUCCEEDED')
                assert(root:IsShown() and a.Presentation.toolbar:IsShown())
                assert(a:Stop()); assert(not root:IsShown() and not c.sampleRecords and not a._screenshotSubjects)
            end
            assert(#c:DB().captures==7)
            for _,r in ipairs(c:DB().captures) do assert(r.addon=='forever-showcase' and not r.id:find('self%-sample')) end
        """)

    def test_fixture_isolation_switch_and_combat(self):
        self.runtime().execute("""
            local a=ForeverShowcase
            assert(a:Start('forever-showcase','captures'))
            assert(#c.sampleRecords==5 and #c:DB().captures==0)
            assert(not c.gallery.send:IsEnabled() and not c.gallery.rows[1].remove:IsEnabled())
            assert(a:Start('forever-showcase','selector'))
            assert(not c.sampleRecords and not c.gallery:IsShown())
            assert(a:Start('forever-showcase','captures'))
            inCombat=true; emit('PLAYER_REGEN_DISABLED')
            assert(not c.sampleRecords and not c.gallery:IsShown() and not a._screenshotSubjects)
            inCombat=false; emit('PLAYER_REGEN_ENABLED')
            assert(not a:Status() and #c:DB().captures==0)
        """)

    def test_self_command_is_opt_in_idempotent_and_does_not_start_scene(self):
        lua=self.runtime(False)
        lua.execute((ROOT/'ForeverShowcase/Commands.lua').read_text(encoding='utf-8'))
        lua.execute("""
            local a=ForeverShowcase
            a:Stop()
            local function countSelf()
                local count=0
                for _,r in ipairs(a:List()) do if r.addon=='forever-showcase' then count=count+1 end end
                return count
            end
            SlashCmdList.FOREVERSHOWCASE('')
            assert(countSelf()==0 and not a:Status())
            assert(not a:Start('forever-showcase','selector'))
            SlashCmdList.FOREVERSHOWCASE('self')
            assert(countSelf()==7 and a.Window:IsShown() and not a:Status())
            assert(a.Window.heading.text=='Scene library')
            SlashCmdList.FOREVERSHOWCASE('self'); assert(countSelf()==7 and not a:Status())
            assert(a:Start('test','one'))
            SlashCmdList.FOREVERSHOWCASE('self')
            assert(a:Status()=='test' and a.Window.heading.text=='Scene library')
            SlashCmdList.FOREVERSHOWCASE('')
            for _,row in ipairs(a.Window.addonRows) do assert(not row:IsShown() or row.id~='forever-showcase') end
            SlashCmdList.FOREVERSHOWCASE('self')
            assert(a.Window.heading.text=='Scene library' and a:Status()=='test')
            SlashCmdList.FOREVERSHOWCASE('show')
            for _,row in ipairs(a.Window.addonRows) do assert(not row:IsShown() or row.id~='forever-showcase') end
        """)
        self.runtime(False).execute("""
            for _,r in ipairs(ForeverShowcase:List()) do assert(r.addon~='forever-showcase') end
        """)

    def test_toolbar_copy_framing_and_backdrop_restore(self):
        self.runtime().execute("""
            local a=ForeverShowcase; local p=a.Presentation
            assert(a:Start('forever-showcase','toolbar'))
            local subject=p:GetContext()._presentation.frames[1]
            assert(subject~=p.toolbar and subject:GetWidth()==p.toolbar:GetWidth())
            assert(subject.previous.label.text==p.toolbar.previous.label.text and subject.paddingMore.label.text=='+')
            assert(a:Start('forever-showcase','framing'))
            local roots=p:GetContext()._presentation.frames
            assert(#roots==2 and roots[2]:GetWidth()==760 and #roots[2].parts==8)
            c:SetRect(100,100,500,500); c:Take()
            assert(roots[1]:IsShown() and roots[2]:IsShown())
            c:Cancel(); a:Stop(); assert(not roots[2]:IsShown())
            p.mode=1
            assert(a:Start('forever-showcase','charcoal')); assert(p.mode==3 and p.backdrop:IsShown())
            a:Stop(); assert(p.mode==1 and not p.backdrop:IsShown())
            assert(a:Start('forever-showcase','ivory')); assert(p.mode==4)
            a:Stop(); assert(p.mode==1)
        """)
