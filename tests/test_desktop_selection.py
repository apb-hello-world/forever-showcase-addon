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
        for timer in self.root.tk.call("after", "info"):
            self.root.after_cancel(timer)
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


    def test_export_dialog_repeat_export_and_reset(self):
        import time
        from PIL import Image
        source=Path(self.temp.name)/'source.png'
        image=Image.new('RGBA',(200,100),'red');image.save(source)
        row=dict(id='export',addon='Test',scene='Overview',source=str(source),screenWidth=200,screenHeight=100,width=200,height=100,x=0,y=0)
        self.app.records=[row];self.app.selected='export';self.app.selected_ids={'export'}
        self.app.images=(image,image,image);self.app.view.set('Original');self.app.output=str(Path(self.temp.name)/'exports')
        self.app.refresh_list();self.app.set_enabled(True);self.app.open_export();self.root.update()
        dialog=self.app.export_window
        self.assertIn(str((Path(self.app.output)/"Test").resolve()),dialog.status.get())
        def finish():
            deadline=time.monotonic()+10
            while dialog.busy and time.monotonic()<deadline:self.root.update();time.sleep(.01)
            self.assertFalse(dialog.busy)
        dialog.export();finish();self.assertTrue(dialog.winfo_exists())
        dialog.subfolder.set('thumbnails')
        self.assertIn(str((Path(self.app.output)/'Test'/'thumbnails').resolve()),dialog.status.get())
        dialog.width_850();self.assertEqual(dialog.height.get(),'425')
        dialog.export();finish()
        files=list((Path(self.app.output)/'Test').rglob('*.png'));self.assertEqual(len(files),2)
        with Image.open(next(p for p in files if '850x425' in p.name)) as resized:self.assertEqual(resized.size,(850,425))
        dialog.reset();self.assertTrue(dialog.original);self.assertEqual(dialog.width.get(),'200')
        self.assertEqual(dialog.subfolder.get(),'')
        self.assertLessEqual(dialog.export_button.winfo_rooty()+dialog.export_button.winfo_height(),dialog.winfo_rooty()+dialog.winfo_height())
        dialog.close_window()
