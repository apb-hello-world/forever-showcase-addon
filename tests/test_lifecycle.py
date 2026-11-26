"""Run against Lua 5.1, the relevant syntax/runtime baseline, with WoW event stubs."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


def runtime(load=True):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
        frames = {}; messages = {}; SlashCmdList = {}; inCombat = false
        function InCombatLockdown() return inCombat end
        DEFAULT_CHAT_FRAME = { AddMessage = function(_, s) table.insert(messages, s) end }
        function CreateFrame()
            local f = { events = {} }
            function f:RegisterEvent(e) self.events[e] = true end
            function f:SetScript(_, fn) self.handler = fn end
            table.insert(frames, f); return f
        end
        function emit(e, ...)
            for _, f in ipairs(frames) do if f.events[e] then f.handler(f, e, ...) end end
        end
        function definition(id)
            return {id=id or 'test', title='Test', scenes={
                {id='one', title='One', enter=function(c)
                    ctx=c; enters=(enters or 0)+1
                    c:AddCleanup(function() cleaned=(cleaned or 0)+1 end, false)
                    c:AddCleanup(function() assert(not inCombat); restored=(restored or 0)+1 end)
                    stale=c:Guard(function() writes=(writes or 0)+1 end)
                end, leave=function(c, reason)
                    assert(not inCombat); assert(not c:IsActive())
                    leaves=(leaves or 0)+1; lastReason=reason
                end},
                {id='two', title='Two', enter=function() end, leave=function() end}
            }}
        end
    ''')
    if load:
        load_core(lua)
    return lua


def load_core(lua):
    for file in ('Core.lua', 'Commands.lua'):
        lua.execute((ROOT / 'ForeverShowcase' / file).read_text())


class Lifecycle(unittest.TestCase):
    def run_lua(self, source):
        runtime().execute(source)

    def test_repeat_switch_and_stale(self):
        self.run_lua('''
            local a=ForeverShowcase
            assert(a:Register(1, definition()))
            assert(a:Register(1, definition('other')))
            assert(a:Start('test','one')); local old=stale
            assert(a:Start('test','one')); old(); assert(writes==nil)
            assert(cleaned==1 and restored==1 and leaves==1)
            assert(a:Start('other','one')); assert(cleaned==2)
            assert(a:Next()); assert(cleaned==3)
            assert(a:Stop()); assert(a:Stop()); assert(cleaned==3)
        ''')

    def test_failed_entry(self):
        for body in ('error("entry")', 'return false', 'c:Guard(function() error("guard") end)()'):
            self.run_lua('''
                local a=ForeverShowcase; local d=definition()
                local original=d.scenes[1].enter
                d.scenes[1].enter=function(c) original(c); BODY end
                assert(a:Register(1,d)); assert(not a:Start('test','one'))
                assert(cleaned==1 and restored==1 and leaves==1)
                assert(not ctx:IsActive()); assert(not a:Status())
                assert(a:Start('test','two'))
            '''.replace('BODY', body))

    def test_cleanup_failure_continues_and_blocks(self):
        self.run_lua('''
            local a=ForeverShowcase; local d=definition(); local original=d.scenes[1].enter
            d.scenes[1].enter=function(c)
                original(c); c:AddCleanup(function() error('cleanup') end)
            end
            d.scenes[1].leave=function() error('leave') end
            assert(a:Register(1,d)); assert(a:Start('test','one'))
            assert(not a:Stop()); assert(cleaned==1 and restored==1)
            assert(not a:Start('test','two')); a:Stop(); assert(cleaned==1)
            local _,_,_,fault=a:Status(); assert(fault)
        ''')

    def test_combat(self):
        self.run_lua('''
            local a=ForeverShowcase; assert(a:Register(1,definition()))
            inCombat=true; assert(not a:Start('test','one')); inCombat=false
            assert(a:Start('test','one')); inCombat=true; stale(); assert(not writes)
            emit('PLAYER_REGEN_DISABLED'); assert(cleaned==1 and not restored and not leaves)
            local _,_,pending=a:Status(); assert(pending)
            assert(not a:Start('test','two')); a:Stop(); assert(cleaned==1)
            inCombat=false; emit('PLAYER_REGEN_ENABLED')
            assert(restored==1 and leaves==1 and lastReason=='combat')
            emit('PLAYER_REGEN_ENABLED'); assert(restored==1)
            assert(a:Start('test','two'))
        ''')

    def test_registration_availability_and_missing(self):
        self.run_lua('''
            local a=ForeverShowcase; assert(#a:List()==0)
            assert(not a:Start('missing','one')); local d=definition()
            assert(not a:Register(2,d)); assert(a:Register(1,d)); assert(not a:Register(1,d))
            assert(not a:Start('test','missing')); assert(a:Start('test','one'))
            local b=definition('blocked'); b.scenes[1].available=function() return false,'missing dependency' end
            b.scenes[2].available=function() error('probe') end
            assert(a:Register(1,b)); assert(not a:Start('blocked','one'))
            assert(not a:Start('blocked','two')); assert(ctx:IsActive())
            assert(a:List()[1].reason=='missing dependency')
            d.scenes[1].enter=function() error('mutated caller table') end
            assert(a:Start('test','one'))
        ''')

    def test_guard_errors_and_reentrancy(self):
        self.run_lua('''
            local a=ForeverShowcase; local d=definition(); local orig=d.scenes[1].enter
            d.scenes[1].enter=function(c)
                orig(c); assert(not a:Start('test','two')); assert(not a:Stop())
            end
            assert(a:Register(1,d)); assert(a:Start('test','one'))
            ctx:Guard(function() error('timer') end)()
            assert(not ctx:IsActive()); assert(cleaned==1)
            assert(not pcall(function() ctx:AddCleanup(function() end) end))
        ''')

    def test_logout_and_fresh_runtime(self):
        self.run_lua('''
            local a=ForeverShowcase; a:Register(1,definition()); a:Start('test','one')
            emit('PLAYER_LOGOUT'); assert(cleaned==1 and restored==1)
        ''')
        self.run_lua("assert(not ForeverShowcase:Status()); assert(#ForeverShowcase:List()==0)")
        toc = (ROOT / 'ForeverShowcase/ForeverShowcase.toc').read_text()
        self.assertIn('## SavedVariables: ForeverShowcaseDB', toc)

    def test_example_load_orders_and_commands(self):
        example = (ROOT / 'examples/ForeverShowcaseExample/Example.lua').read_text()
        for companion_first in (False, True):
            lua = runtime(load=companion_first)
            lua.execute(example)
            if not companion_first:
                load_core(lua)
                lua.execute("emit('ADDON_LOADED','ForeverShowcase')")
            lua.execute('''
                emit('ADDON_LOADED','ForeverShowcase')
                assert(#ForeverShowcase:List()==3)
                local slash=SlashCmdList.FOREVERSHOWCASE
                slash(''); slash('list'); slash('EXAMPLE FIRST'); slash('info'); slash('next')
                local _,id=ForeverShowcase:Status(); assert(id=='second')
                slash('next'); _,id=ForeverShowcase:Status(); assert(id=='first')
                slash('off'); slash('status'); slash('bogus'); assert(not ForeverShowcase:Status())
            ''')


if __name__ == '__main__':
    unittest.main()
