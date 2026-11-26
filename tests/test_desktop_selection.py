"""Real Tk pointer-event regression, not direct click-handler calls."""
import sys
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from companion.app import App

@unittest.skipUnless(sys.platform=='win32','Windows desktop integration')
class DesktopSelection(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=tk.Tk()
        self.app=App(self.root,self.temp.name,manifest=str(Path(self.temp.name)/'missing.lua'),screenshots=self.temp.name)
        self.app.show_window();self.root.update();self.app.layout();self.root.update()
        self.app.records=[dict(id=str(i),addon='test',scene='Capture '+str(i)) for i in range(4)]
        self.app.refresh_list();self.root.update()

    def tearDown(self):
        self.app.close();self.temp.cleanup()

    def pointer_click(self,index,modifiers=0):
        box=self.app.listbox;y=box.bbox(index)[1]+5
        box.event_generate('<ButtonPress-1>',x=20,y=y,state=modifiers)
        self.root.update()
        after_press=set(self.app.selected_ids)
        for offset in (1,2,0):
            box.event_generate('<Motion>',x=20+offset,y=y,state=0x100|modifiers)
            self.root.update()
            self.assertEqual(self.app.selected_ids,after_press)
        box.event_generate('<ButtonRelease-1>',x=20,y=y,state=modifiers)
        self.root.update()
        self.assertEqual(self.app.selected_ids,after_press)
        return after_press

    def test_repeated_clicks_with_pointer_jitter(self):
        for index in (0,1,2,3,2,1,0,3):
            selected=self.pointer_click(index)
            self.assertEqual(selected,{self.app.visible_records[index]['id']})
            self.assertEqual(self.app.listbox.curselection(),(index,))

    def test_ctrl_add_remove_and_shift_range_with_jitter(self):
        first=self.pointer_click(0)
        second=self.pointer_click(1,4)
        self.assertEqual(len(second),2)
        self.assertTrue(first<second)
        self.assertEqual(self.pointer_click(1,4),first)
        self.assertEqual(len(self.pointer_click(3,1)),4)
        self.app.refresh_list();self.root.update()
        self.assertEqual(len(self.app.listbox.curselection()),4)
