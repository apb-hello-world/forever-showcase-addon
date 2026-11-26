"""Stagekeeper desktop workspace. Local images with opt-in public release updates."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from tkinter import font as tkfont
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont

from companion import updates
from companion.version import VERSION
from companion.preview import PreviewWindow
from companion.batch import export_batch

from companion.model import (Style, PRESETS, read_manifest, match_batch, open_image,
                             crop_image, render, save_image, copy_image)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'design' / 'assets'
INK, IVORY, PAPER, WOOD = '#362313', '#f9ebcc', '#ebd8af', '#28190f'
GAME = Path('E:/World of Warcraft/_forever_')


def fit_label(text, width, measure):
    """Fit visible text to the actual row width while preserving the source name."""
    if measure(text)<=width:return text
    if measure('…')>width:return ''
    low,high=0,len(text)
    while low<high:
        middle=(low+high+1)//2
        if measure(text[:middle]+'…')<=width:low=middle
        else:high=middle-1
    return text[:low].rstrip()+'…'


def shell_image(source, size):
    """Windows color-key windows need a binary alpha silhouette after scaling."""
    image = source.resize(size, Image.Resampling.LANCZOS)
    image.putalpha(image.getchannel('A').point(lambda value: 255 if value >= 128 else 0))
    return image


def caption_image(label, scale, color):
    oversample = 4
    size = max(10, round(12*scale))
    if label in ('⚙', '−', '□', '×'):
        side = max(10,round(12*scale))*oversample
        image = Image.new('RGBA',(side,side))
        d = ImageDraw.Draw(image); center = side/2
        stroke = max(4,round(scale*oversample))
        low,high = side*.18,side*.82
        if label == '−': d.line((low,center,high,center),fill=color,width=stroke)
        elif label == '□': d.rectangle((low,low,high,high),outline=color,width=stroke)
        elif label == '×':
            d.line((low,low,high,high),fill=color,width=stroke)
            d.line((low,high,high,low),fill=color,width=stroke)
        else:
            points=[]
            for i in range(64):
                angle=i*math.tau/64
                radius=side*(.46 if i%8 in (1,2,3,4) else .35)
                points.append((center+math.cos(angle)*radius,center+math.sin(angle)*radius))
            d.polygon(points,fill=color)
            d.ellipse((side*.32,side*.32,side*.68,side*.68),fill=(0,0,0,0))
        # Keep a common square icon box, including the thin minimize stroke.
        return image.resize((side//oversample,side//oversample),Image.Resampling.LANCZOS)
    font=ImageFont.truetype(str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/segoeui.ttf'),size*oversample)
    box=font.getbbox(label)
    image=Image.new('RGBA',(max(1,box[2]-box[0]),max(1,box[3]-box[1])))
    ImageDraw.Draw(image).text((-box[0],-box[1]),label,font=font,fill=color)
    return image.resize((max(1,round(image.width/oversample)),max(1,round(image.height/oversample))),Image.Resampling.LANCZOS)


class ArtButton:
    """Canvas controls share the shell beneath their transparent artwork."""
    def __init__(self, app, label, x, y, width, command, height, plain=False):
        self.app, self.command, self.state = app, command, 'normal'
        self.x, self.y, self.width, self.height = x, y, width, height
        self.plain = plain
        self.caption = label
        self.hover = self.focused = False
        c = app.canvas
        self.image = c.create_image(0, 0, anchor='nw')
        self.label = c.create_image(0, 0)
        self.items = [self.image, self.label]
        for item in self.items:
            c.tag_bind(item, '<Button-1>', lambda e: self.invoke())
            c.tag_bind(item, '<Enter>', lambda e: self.highlight('hover', True))
            c.tag_bind(item, '<Leave>', lambda e: self.highlight('hover', False))
        self.widget = tk.Button(c, text=label, command=self.invoke, takefocus=True)
        self.widget.bind('<FocusIn>', lambda e: self.highlight('focused', True))
        self.widget.bind('<FocusOut>', lambda e: self.highlight('focused', False))
        # Offscreen native button keeps normal Tab/Space keyboard behavior.
        self.widget.place(x=-1000, y=-1000, width=1, height=1)
        app.art_buttons.append(self)
    def invoke(self):
        if self.state != 'disabled': self.command()
    def highlight(self, key, value):
        setattr(self, key, value); self.draw_caption()
        if key == 'hover':
            self.app.canvas.configure(cursor='hand2' if value and self.state != 'disabled' else '')

    def configure(self, **kw):
        self.state = kw.get('state', self.state)
        self.widget.configure(state=self.state)
        if self.hover:
            self.app.canvas.configure(cursor='hand2' if self.state != 'disabled' else '')
        if 'text' in kw:
            self.caption = kw['text']; self.widget.configure(text=self.caption)
        self.draw_caption()

    def draw_caption(self):
        color = '#a68f71' if self.state == 'disabled' else '#ffdc72' if self.focused else '#ffffff' if self.hover else IVORY
        # Crop to visible ink, rather than centering the font's ascent/descent box.
        scale = self.app.scale
        image = caption_image(self.caption, scale, color)
        self.caption_photo = ImageTk.PhotoImage(image)
        self.app.canvas.itemconfigure(self.label, image=self.caption_photo)

    def layout(self):
        a, c = self.app, self.app.canvas
        x,y,w,h = a.ox+self.x*a.scale,a.oy+self.y*a.scale,self.width*a.scale,self.height*a.scale
        art = a.button_image(max(3,round(w)),max(1,round(h)))
        self.photo = ImageTk.PhotoImage(art)
        c.coords(self.image,x,y); c.itemconfigure(self.image,image=self.photo)
        bounds = art.getchannel('A').point(lambda v: 255 if v >= 128 else 0).getbbox()
        left,top,right,bottom = bounds or (0,0,w,h)
        c.coords(self.label,round(x+(left+right)/2),round(y+(top+bottom)/2))
        self.draw_caption()

    def show(self, visible):
        if not visible and self.hover:
            self.highlight('hover', False)
        for item in self.items: self.app.canvas.itemconfigure(item,state='normal' if visible else 'hidden')
        self.widget.configure(takefocus=visible)


class App:
    def __init__(self, root, state_dir, manifest=None, screenshots=None):
        self.root, self.state_dir = root, Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / 'settings.json'
        try:
            self.state = json.loads(self.state_file.read_text(encoding='utf-8'))
            if not isinstance(self.state, dict):
                self.state = {}
        except (OSError, ValueError):
            self.state = {}
        self.records = self.state.get('records', [])
        self.ignored = set(self.state.get('ignored', []))
        self.presets = {**PRESETS, **self.state.get('presets', {})}
        self.manifest = manifest or self.state.get('manifest', '')
        if not self.manifest:
            paths = [p / 'SavedVariables/ForeverShowcase.lua' for p in (GAME / 'WTF/Account').glob('*') if p.is_dir()]
            if len(paths) == 1:
                self.manifest = str(paths[0])
        self.screenshots = screenshots or self.state.get('screenshots', str(GAME / 'Screenshots'))
        self.output = self.state.get('output', str(Path.home() / 'Pictures/Forever Showcase'))
        self.pool = ThreadPoolExecutor(max_workers=2)
        self.future = self.render_future = None
        self.selected_ids = set()
        self.batch_running = False
        self.selected = None
        self.images = None
        self.rendering = False
        self.render_error = None
        self.render_generation = 0
        self.scan_signature = None
        self.stable_signature = None
        self.retry_ticks = 0
        self.status = 'Start a scene in WoW, capture an area, then choose Captures → Send & reload.'
        self.view = tk.StringVar(value='Styled')
        self.preset = tk.StringVar(value='Stagekeeper')
        self.fields = {k: tk.StringVar(value=str(v)) for k, v in asdict(Style()).items() if k != 'transparent'}
        self.transparent = tk.BooleanVar(value=False)
        self.nodes = []
        self.art_buttons = []
        self.settings_open = False
        self.photos = []
        self.scale, self.ox, self.oy = 1, 0, 0
        root.title('Forever Showcase — Companion '+VERSION)
        root.geometry('1200x912'); root.minsize(1000, 760)
        root.configure(bg='#010203')
        if sys.platform == 'win32':
            root.withdraw()
            root.attributes('-transparentcolor', '#010203')
            root.bind('<Map>', self.restore_chrome, add='+')
            root.after(100, self.show_window)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.report_callback_exception = lambda kind, value, trace: self.error(value)
        self.canvas = tk.Canvas(root, bg='#010203', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.shell = Image.open(ASSETS / 'StagekeeperShell.png').convert('RGBA')
        self.logo = Image.open(ASSETS / 'StagekeeperWordmark-runtime.png').convert('RGBA')
        self.button_art = Image.open(ASSETS / 'StagekeeperButton.png').convert('RGBA').resize((512,128), Image.Resampling.LANCZOS)
        self.build()
        root.bind('<Configure>', self.resize)
        root.bind('<Control-s>', lambda _: self.save())
        root.bind('<Control-Shift-S>', lambda _: self.save(True))
        root.bind('<Control-c>', lambda _: self.copy() if not isinstance(root.focus_get(), (tk.Entry, tk.Spinbox, ttk.Entry, ttk.Combobox)) else None)
        root.after(80, self.layout)
        root.after(100, self.scan)
        self.refresh_list()

    def persist(self):
        self.state.update(manifest=self.manifest, screenshots=self.screenshots, output=self.output,
                          records=self.records, ignored=sorted(self.ignored),
                          presets={k: v for k, v in self.presets.items() if k not in PRESETS})
        temporary = self.state_file.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.state, indent=2), encoding='utf-8')
        temporary.replace(self.state_file)

    def text(self, text, x, y, width, size=12, color=INK, bold=False):
        item = self.canvas.create_text(0, 0, text=text, anchor='nw', fill=color)
        self.nodes.append(('text', item, x, y, width, size, bold))
        return item

    def widget(self, widget, x, y, width, height, button=False):
        item = self.canvas.create_window(0, 0, window=widget, anchor='nw')
        self.nodes.append(('button' if button else 'widget', item, x, y, width, height, widget))
        return widget

    def field(self, widget, x, y, width, height):
        border=self.canvas.create_polygon(0,0,1,0,1,1,0,1,fill='#f7e8ca',outline='#a18456',smooth=True)
        self.nodes.append(('field',border,x,y,width,height,widget))
        options=widget.keys()
        if 'highlightthickness' in options:widget.configure(highlightthickness=0)
        if 'borderwidth' in options:widget.configure(borderwidth=0)
        widget.bind('<FocusIn>',lambda e:self.canvas.itemconfigure(border,outline='#704b27'),add='+')
        widget.bind('<FocusOut>',lambda e:self.canvas.itemconfigure(border,outline='#a18456'),add='+')
        self.widget(widget,x+5,y+3,width-10,height-6)
        return widget

    def button(self, label, x, y, width, command, height=32):
        return ArtButton(self, label, x, y, width, command, height)

    def build(self):
        self.bg = self.canvas.create_image(0, 0, anchor='nw')
        self.wordmark = self.canvas.create_image(0, 0, anchor='nw')
        self.text('Captures', 62, 151, 165, 16, IVORY, True)
        self.text('Finish', 273, 151, 170, 16, IVORY, True)
        self.selection_note = self.text('Select a capture to edit',272,197,170,10,INK)
        self.button('⚙', 782, 92, 32, self.setup, 28)
        self.button('−', 820, 92, 32, self.minimize, 28)
        self.button('□', 858, 92, 32, self.maximize, 28)
        self.button('×', 896, 92, 32, self.close, 28)
        self.canvas.bind('<ButtonPress-1>', self.drag_start)
        self.canvas.bind('<B1-Motion>', self.drag_move)
        style=ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('Showcase.TCombobox',fieldbackground='#f7e8ca',background='#e0cba4',foreground=INK,borderwidth=0,arrowsize=12)
        style.map('Showcase.TCombobox',fieldbackground=[('readonly','#f7e8ca')],foreground=[('readonly',INK)])
        self.listbox = tk.Listbox(self.canvas, bg=WOOD, fg=IVORY, selectbackground='#6b3930',
                                 selectforeground='white', borderwidth=0, highlightthickness=0,
                                 activestyle='none', exportselection=False, selectmode='extended',cursor='hand2',relief='flat',selectborderwidth=0)
        self.widget(self.listbox, 55, 206, 172, 260)
        self.listbox.bind('<Configure>', self.resize_capture_list)
        self.listbox.bind('<Button-1>', self.click_capture)
        self.listbox.bind('<Control-a>', self.select_all)
        self.listbox.bind('<<ListboxSelect>>', self.select)
        self.count_text = self.text('', 57, 486, 170, 11, IVORY)
        self.button('Import image', 66, 530, 150, self.import_image)
        self.button('Remove record', 66, 570, 150, self.remove, 28)
        self.text('Preset', 272, 218, 165, 12, INK, True)
        combo = ttk.Combobox(self.canvas, textvariable=self.preset, values=list(self.presets), state='readonly',style='Showcase.TCombobox')
        self.preset_combo = self.field(combo, 272, 241, 166, 30)
        combo.bind('<<ComboboxSelected>>', lambda _: self.apply_preset())
        for i, (key, maximum) in enumerate((('padding', 256), ('radius', 256), ('border', 32), ('shadow', 64))):
            y = 285 + i * 43
            self.text(key.capitalize() + ' (px)', 272, y + 4, 107, 11)
            spin = tk.Spinbox(self.canvas, from_=0, to=maximum, textvariable=self.fields[key],
                              bg='#f7e8ca', fg=INK, buttonbackground='#d8bd8d', relief='flat',
                              command=self.request_render, highlightthickness=1, highlightbackground='#a18456')
            spin.bind('<Return>', lambda _: self.request_render())
            spin.bind('<FocusOut>', lambda _: self.request_render())
            self.field(spin, 380, y, 58, 28)
        self.button('Background color', 283, 450, 144, lambda: self.choose_color('background'), 28)
        self.button('Border color', 283, 486, 144, lambda: self.choose_color('border_color'), 28)
        self.check = self.button('Transparent PNG: Off', 283, 522, 144, self.toggle_transparency, 28)
        self.button('Save preset', 283, 558, 144, self.save_preset, 28)
        self.preview_node_start = len(self.nodes)
        self.preview_button_start = len(self.art_buttons)
        self.title_text = self.text('Your screenshots, ready for the gallery', 507, 190, 405, 19, INK, True)
        self.subtitle = self.text('The same framing across every scene.', 507, 244, 400, 12)
        mode = ttk.Combobox(self.canvas, textvariable=self.view, values=['Original', 'Crop', 'Styled'], state='readonly',style='Showcase.TCombobox')
        self.field(mode, 507, 280, 130, 30)
        mode.bind('<<ComboboxSelected>>', lambda _: self.draw_preview())
        self.preview = self.canvas.create_image(0, 0)
        self.empty_text = self.text('Capture in WoW\n\nDraw an area and click Capture. Open Captures and choose Send & reload.\n\nYour full-size screenshot stays safe. The companion crops and styles a separate export.', 530, 345, 350, 14)
        self.dimensions = self.text('', 507, 532, 405, 11)
        self.locate = self.button('Choose original…', 507, 558, 160, self.locate_original, 28)
        self.full_preview_button = self.button('Full-size preview', 683, 558, 180, self.show_full_preview, 28)
        self.preview_nodes = self.nodes[self.preview_node_start:]
        self.preview_buttons = self.art_buttons[self.preview_button_start:]
        self.build_settings()
        self.status_text = self.text(self.status, 55, 657, 390, 12, IVORY)
        self.save_button = self.button('Save', 505, 658, 122, self.save, 36)
        self.save_as_button = self.button('Save as…', 635, 658, 140, lambda: self.save(True), 36)
        self.copy_button = self.button('Copy image', 783, 658, 145, self.copy, 36)
        self.set_enabled(False)

    def resize(self, event):
        if event.widget is self.root:
            size = (event.width, event.height)
            if size == getattr(self, 'configured_size', None):
                return
            self.configured_size = size
            if getattr(self, 'resize_job', None):
                self.root.after_cancel(self.resize_job)
            self.resize_job = self.root.after(80, self.layout)

    def button_image(self, width, height):
        source = self.button_art
        cap = min(16, (width - 1) // 2)
        out = Image.new('RGBA', (width, height))
        out.alpha_composite(source.crop((0, 0, 48, source.height)).resize((cap, height)), (0, 0))
        out.alpha_composite(source.crop((48, 0, source.width-48, source.height)).resize((width-2*cap, height)), (cap, 0))
        out.alpha_composite(source.crop((source.width-48, 0, source.width, source.height)).resize((cap, height)), (width-cap, 0))
        return out

    def layout(self):
        self.resize_job = None
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.scale = min(w/1000, h/760)
        s = self.scale; self.ox = (w-1000*s)/2; self.oy = (h-760*s)/2
        photos = []
        for item, source, x, y, iw, ih in ((self.bg, self.shell, 0, 0, 1000, 760), (self.wordmark, self.logo, 300, 42, 400, 100)):
            size = (max(1, int(iw*s)), max(1, int(ih*s)))
            photo = ImageTk.PhotoImage(shell_image(source,size) if item == self.bg else source.resize(size,Image.Resampling.LANCZOS))
            photos.append(photo); self.canvas.itemconfigure(item, image=photo)
            self.canvas.coords(item, self.ox+x*s, self.oy+y*s)
        self.photos = photos
        for kind, item, x, y, width, height, extra in self.nodes:
            if kind == 'field':
                left,top=self.ox+x*s,self.oy+y*s
                right,bottom=left+width*s,top+height*s
                radius=5*s
                self.canvas.coords(item,left+radius,top,right-radius,top,right,top,right,top+radius,right,bottom-radius,right,bottom,right-radius,bottom,left+radius,bottom,left,bottom,left,bottom-radius,left,top+radius,left,top)
                self.canvas.itemconfigure(item,width=max(1,round(s)))
                continue
            self.canvas.coords(item, self.ox+x*s, self.oy+y*s)
            if kind == 'text':
                self.canvas.itemconfigure(item, width=width*s, font=('Segoe UI', -max(10, round(height*s)), 'bold' if extra else 'normal'))
            else:
                self.canvas.itemconfigure(item, width=width*s, height=height*s)
                if 'font' in extra.keys():
                    extra.configure(font=('Segoe UI', -max(10, round(12*s))))
                if kind == 'button':
                    art = self.button_image(max(3, round(width*s)-2), max(1, round(height*s)-2))
                    extra.normal_image = ImageTk.PhotoImage(ImageEnhance.Brightness(art).enhance(.85))
                    extra.hover_image = ImageTk.PhotoImage(art)
                    extra.configure(image=extra.normal_image)
        for button in self.art_buttons: button.layout()
        self.draw_preview()

    def set_enabled(self, enabled):
        for b in (self.copy_button,self.full_preview_button):
            b.configure(state='normal' if enabled else 'disabled')
        can_save=(enabled or len(self.selected_ids)>1) and not self.batch_running
        for b in (self.save_button,self.save_as_button):b.configure(state='normal' if can_save else 'disabled')

    def say(self, text):
        self.status = text; self.canvas.itemconfigure(self.status_text, text=text)

    def error(self, error):
        self.say(str(error))
        messagebox.showerror('Forever Showcase', str(error), parent=self.root)

    def current(self):
        return next((r for r in self.records if r['id'] == self.selected), None)

    def selected_records(self):
        return [r for r in self.records if r['id'] in self.selected_ids]

    def refresh_list(self):
        self.listbox.delete(0, 'end')
        self.visible_records = list(reversed(self.records))
        self.selected_ids.intersection_update(r['id'] for r in self.records)
        if not self.selected_ids and self.selected:self.selected_ids.add(self.selected)
        font=tkfont.Font(font=self.listbox.cget('font'))
        width=self.listbox.winfo_width()
        if width<=1:width=round(172*self.scale)
        available=max(1,width-font.measure('  ')-round(12*self.scale))
        for i,r in enumerate(self.visible_records):
            name=r.get('name',r['scene']).replace('\n',' ')
            self.listbox.insert('end','  '+fit_label(name,available,font.measure))
            self.listbox.itemconfigure(i,background='#38271b' if i%2==0 else '#302116',foreground=IVORY)
            if r['id'] in self.selected_ids:self.listbox.selection_set(i)
            if r['id']==self.selected:self.listbox.activate(i)
        count=len(self.selected_ids)
        self.canvas.itemconfigure(self.selection_note,text=f'Applies to {count} selected' if count else 'Select a capture to edit')
        self.canvas.itemconfigure(self.count_text,text=f'{len(self.records)} captures · {count} selected\nCtrl-click to select more')
        self.save_button.configure(text=f'Save {count} images' if count>1 else 'Save')
        self.save_as_button.configure(text='Save to folder…' if count>1 else 'Save as…')

    def resize_capture_list(self,event):
        key=(event.width,self.listbox.cget('font'))
        if key==getattr(self,'capture_list_size',None):return
        self.capture_list_size=key
        if hasattr(self,'visible_records'):
            position=self.listbox.yview()[0]
            self.refresh_list()
            self.listbox.yview_moveto(position)

    def select_all(self,event=None):
        self.selected_ids={r['id'] for r in self.records}
        if not self.selected and self.visible_records:self.selected=self.visible_records[0]['id']
        self.refresh_list();self.load_selected_style();self.request_render(False)
        return 'break'

    def click_capture(self,event):
        if not self.visible_records:return 'break'
        index=self.listbox.nearest(event.y)
        bounds=self.listbox.bbox(index)
        if not bounds or not bounds[1]<=event.y<bounds[1]+bounds[3]:return 'break'
        identity=self.visible_records[index]['id']
        if event.state & 0x4:
            if identity in self.selected_ids:self.selected_ids.remove(identity)
            else:self.selected_ids.add(identity)
        elif event.state & 0x1 and self.selected:
            anchor=next((i for i,r in enumerate(self.visible_records) if r['id']==self.selected),index)
            self.selected_ids={r['id'] for r in self.visible_records[min(anchor,index):max(anchor,index)+1]}
        else:self.selected_ids={identity}
        self.selected=identity if identity in self.selected_ids else next((r['id'] for r in self.visible_records if r['id'] in self.selected_ids),None)
        self.refresh_list();self.load_selected_style();self.request_render(False)
        return 'break'

    def select(self,_=None):
        indices=self.listbox.curselection()
        ids={self.visible_records[i]['id'] for i in indices}
        if ids==self.selected_ids:return
        self.selected_ids=ids
        active=self.listbox.index('active')
        self.selected=self.visible_records[active]['id'] if active in indices else (self.visible_records[indices[-1]]['id'] if indices else None)
        self.refresh_list();self.load_selected_style();self.request_render(False)

    def load_selected_style(self):
        row=self.current()
        if row and row.get('style'):
            try:style=Style(**row['style']).validated()
            except (ValueError,TypeError):return
            for key,var in self.fields.items():var.set(str(getattr(style,key)))
            self.transparent.set(style.transparent);self.update_check()
            match=next((name for name,value in self.presets.items() if value==asdict(style)), 'Custom')
            self.preset.set(match)

    def style(self):
        return Style(**{k: int(v.get()) if k in ('padding', 'radius', 'border', 'shadow') else v.get()
                        for k, v in self.fields.items()}, transparent=self.transparent.get()).validated()

    def request_render(self, apply_style=True):
        self.render_generation += 1
        generation = self.render_generation
        self.images = None; self.set_enabled(False)
        self.rendering = False; self.render_error = None
        r = self.current()
        if not r:
            self.draw_preview(); return
        self.canvas.itemconfigure(self.title_text, text=r.get('name', r['scene'])[:60])
        self.canvas.itemconfigure(self.subtitle, text=r['addon'] + '  ·  ' + r.get('status', 'Ready'))
        try:
            style = self.style()
            if apply_style:
                for row in self.selected_records():row['style']=asdict(style)
                self.persist()
            elif r.get('style'):
                style=Style(**r['style']).validated()
            else:
                r['style']=asdict(style)
        except (ValueError, TypeError) as error:
            self.render_error = str(error)
            self.say(str(error)); self.draw_preview(); return
        if not r.get('source'):
            self.draw_preview(); return
        self.say('Preparing full-resolution preview…')
        self.rendering = True
        self.draw_preview()
        row = dict(r)
        def work():
            original = open_image(row['source']); crop = crop_image(original, row)
            return original, crop, render(crop, style)
        future = self.pool.submit(work)
        def done():
            if generation != self.render_generation:
                return
            if not future.done():
                self.root.after(80, done); return
            try:
                self.rendering = False
                self.images = future.result(); self.set_enabled(True)
                self.say('Ready to export. Save and Copy use the selected preview mode.')
            except Exception as error:
                self.render_error = str(error)
                self.say(str(error)); self.images = None
            self.draw_preview()
        self.root.after(80, done)

    def draw_preview(self):
        if getattr(self,'settings_open',False) or getattr(self,'viewer_open',False): return
        self.canvas.itemconfigure(self.preview, image='')
        r = self.current()
        if not self.images:
            text = ('Preparing preview…' if self.rendering else
                    'Preview unavailable.\n\n' + self.render_error if self.render_error else
                    'Choose original to resolve this capture.\n\n' + r.get('status', 'Missing original') if r else
                    'Capture in WoW\n\nDraw an area and click Capture. Open Captures and choose Send & reload.\n\nYour full-size screenshot stays safe. The companion crops and styles a separate export.')
            self.canvas.itemconfigure(self.empty_text, text=text, state='normal')
            self.canvas.itemconfigure(self.dimensions, text='')
            return
        self.canvas.itemconfigure(self.empty_text, state='hidden')
        image = self.export_image()
        preview = image.copy(); preview.thumbnail((max(1, int(405*self.scale)), max(1, int(215*self.scale))), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(preview)
        self.canvas.itemconfigure(self.preview, image=self.preview_photo)
        self.canvas.coords(self.preview, self.ox+709*self.scale, self.oy+420*self.scale)
        self.canvas.itemconfigure(self.dimensions, text=f'{self.view.get()} · {image.width} × {image.height} px · Full resolution on export')

    def show_full_preview(self):
        if self.images:
            row=self.current() or {}
            PreviewWindow(self.root,self.export_image(),row.get('name',row.get('scene','Image'))+' — '+self.view.get())

    def export_image(self):
        return self.images[['Original', 'Crop', 'Styled'].index(self.view.get())]

    def apply_preset(self):
        value = self.presets[self.preset.get()]
        for k, v in self.fields.items():
            v.set(str(value[k]))
        self.transparent.set(value['transparent']); self.update_check(); self.request_render()

    def choose_color(self, key):
        color = colorchooser.askcolor(self.fields[key].get(), parent=self.root)[1]
        if color:
            self.fields[key].set(color); self.request_render()

    def save_preset(self):
        try:
            style = self.style()
            name = simpledialog.askstring('Save preset', 'Name for this style:', parent=self.root)
            if name and name.strip():
                name = name.strip()[:50]
                if name in PRESETS:
                    raise ValueError('Choose a new name; built-in presets stay available.')
                self.presets[name] = asdict(style); self.preset_combo.configure(values=list(self.presets))
                self.preset.set(name); self.persist(); self.say('Preset saved: ' + name)
        except Exception as error:
            self.error(error)

    def toggle_transparency(self):
        self.transparent.set(not self.transparent.get()); self.update_check(); self.request_render()

    def update_check(self):
        self.check.configure(text='Transparent PNG: ' + ('On' if self.transparent.get() else 'Off'))

    def build_settings(self):
        start, buttons = len(self.nodes), len(self.art_buttons)
        self.text('Settings',507,190,400,22,INK,True)
        self.text('Connect your local files and choose where exports go.',507,240,395,12)
        self.folder_values = {}
        for i,(key,label) in enumerate((('manifest','Capture instructions (ForeverShowcase.lua)'),('screenshots','WoW Screenshots folder'),('output','Default export folder'))):
            y = 295+i*75
            self.text(label,507,y,400,12,INK,True)
            var=tk.StringVar(value=getattr(self,key)); self.folder_values[key]=var
            self.field(tk.Entry(self.canvas,textvariable=var,bg='#f7e8ca',fg=INK,relief='flat'),507,y+25,305,30)
            self.button('Browse…',822,y+25,85,lambda k=key:self.browse_folder(k),28)
        self.update_button = self.button('Check for updates',507,512,165,self.check_updates,28)
        self.text('Companion '+VERSION,689,520,220,11)
        self.button('Save settings',507,558,150,self.save_settings,28)
        self.button('Back',673,558,100,self.setup,28)
        self.settings_nodes=self.nodes[start:]; self.settings_buttons=self.art_buttons[buttons:]
        self.set_group(self.settings_nodes,self.settings_buttons,False)

    def set_group(self,nodes,buttons,visible):
        for node in nodes: self.canvas.itemconfigure(node[1],state='normal' if visible else 'hidden')
        for button in buttons: button.show(visible)

    def setup(self):
        self.settings_open=not self.settings_open
        if self.settings_open:
            for key,var in self.folder_values.items(): var.set(getattr(self,key))
        self.set_group(self.preview_nodes,self.preview_buttons,not self.settings_open)
        self.canvas.itemconfigure(self.preview,state='hidden' if self.settings_open else 'normal')
        self.set_group(self.settings_nodes,self.settings_buttons,self.settings_open)
        self.draw_preview()

    def browse_folder(self,key):
        path = filedialog.askopenfilename(parent=self.root,title='Choose ForeverShowcase.lua',filetypes=[('WoW saved variables','*.lua')]) if key=='manifest' else filedialog.askdirectory(parent=self.root)
        if path: self.folder_values[key].set(path)

    def save_settings(self):
        for key,var in self.folder_values.items(): setattr(self,key,var.get().strip())
        self.output=self.output or str(Path.home()/'Pictures/Forever Showcase')
        self.scan_signature=self.stable_signature=None
        self.persist(); self.setup(); self.say('Settings saved. Watching for a completed capture batch.')

    def check_updates(self):
        if getattr(self,'update_busy',False):return
        if self.batch_running:self.say('Finish the batch export before updating.');return
        self.update_busy=True;self.update_button.configure(state='disabled')
        self.say('Checking public GitHub releases…')
        future=self.pool.submit(updates.check_update)
        def checked():
            if not future.done():self.root.after(100,checked);return
            try:
                release=future.result()
                if not release:
                    self.say('No newer companion release is available.');finish();return
                if not messagebox.askyesno('Companion update',f"Version {release['version']} is available. Download and open its installer? The companion will close after the download.",parent=self.root):finish();return
                self.say('Downloading and verifying the installer…')
                download=self.pool.submit(updates.download_update,release)
                def downloaded():
                    if not download.done():self.root.after(100,downloaded);return
                    try:
                        installer=download.result()
                        if self.batch_running:raise ValueError('Batch export is running. Finish it and check for updates again.')
                        self.persist();updates.launch_installer(installer);self.close()
                    except Exception as error:finish();self.error(error)
                self.root.after(100,downloaded)
            except Exception as error:finish();self.error(error)
        def finish():
            self.update_busy=False;self.update_button.configure(state='normal')
        self.root.after(100,checked)

    def restore_chrome(self, event):
        if event.widget is self.root:
            self.install_chrome()

    def show_window(self):
        self.install_chrome()
        self.root.deiconify()
        self.install_chrome()

    def install_chrome(self):
        # Keep a managed Tk top-level: override-redirect popups do not have a
        # reliable taskbar/minimize lifecycle. Remove only its visual frame.
        import ctypes
        u=ctypes.windll.user32
        u.GetAncestor.argtypes=[ctypes.c_void_p,ctypes.c_uint]; u.GetAncestor.restype=ctypes.c_void_p
        self.hwnd=u.GetAncestor(self.root.winfo_id(),2)
        u.GetWindowLongW.argtypes=[ctypes.c_void_p,ctypes.c_int]
        u.SetWindowLongW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_long]
        u.SetWindowPos.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_uint]
        style=u.GetWindowLongW(self.hwnd,-16)
        ex=u.GetWindowLongW(self.hwnd,-20)
        # WS_CAPTION | WS_THICKFRAME removed; preserve system/minimize controls.
        wanted=(style & ~0x00C40000) | 0x000B0000
        extended=(ex | 0x00040000) & ~0x00000080
        if style != wanted or ex != extended:
            u.SetWindowLongW(self.hwnd,-16,wanted)
            u.SetWindowLongW(self.hwnd,-20,extended)
            # FRAMECHANGED | NOMOVE | NOSIZE | NOZORDER | NOACTIVATE
            u.SetWindowPos(self.hwnd,None,0,0,0,0,0x0037)

    def minimize(self):
        self.canvas.configure(cursor='')
        # Let Tk and Windows agree on the iconic state and normal restoration.
        self.root.iconify()

    def maximize(self):
        if getattr(self,'restore_geometry',None):
            self.root.geometry(self.restore_geometry); self.restore_geometry=None
        else:
            self.restore_geometry=self.root.geometry()
            self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0')

    def drag_start(self,event):
        self.drag_origin=None
        if (event.y-self.oy)/self.scale<145 and self.canvas.find_withtag('current') in ((),(self.bg,),(self.wordmark,)):
            self.drag_origin=(event.x_root,event.y_root,self.root.winfo_x(),self.root.winfo_y())

    def drag_move(self,event):
        if getattr(self,'drag_origin',None):
            x,y,wx,wy=self.drag_origin
            self.move_window(wx+event.x_root-x, wy+event.y_root-y)

    def move_window(self, x, y):
        if sys.platform == 'win32':
            import ctypes
            # Move the existing native surface without a Tk geometry/style
            # reconfiguration on every pointer event. Keep its backing pixels.
            u = ctypes.windll.user32
            u.SetWindowPos(self.hwnd, None, int(x), int(y), 0, 0, 0x0015)
            # Service pending paint work without dispatching nested input events.
            self.root.update_idletasks()
        else:
            self.root.geometry(f'{int(x):+d}{int(y):+d}')

    def scan(self):
        try:
            self.retry_ticks += 1
            # Two identical observations avoid reading WoW while it is rewriting the file.
            manifest = Path(self.manifest) if self.manifest else None
            directory = Path(self.screenshots)
            if not manifest or not manifest.is_file():
                if not self.records:
                    self.say('Waiting for Send & reload in WoW. Use the settings gear if your game is elsewhere.')
            elif directory.is_dir() and self.future is None:
                signature = (str(manifest), manifest.stat().st_mtime_ns, manifest.stat().st_size,
                             str(directory), directory.stat().st_mtime_ns)
                retry = self.retry_ticks % 5 == 0 and any(not r.get('source') for r in self.records)
                if signature == self.stable_signature and (signature != self.scan_signature or retry):
                    self.scan_signature = signature
                    self.future = self.pool.submit(self.read_batch, manifest, directory)
                self.stable_signature = signature
            if self.future is not None and self.future.done():
                future, self.future = self.future, None
                rows = future.result()
                existing = {r['id']: r for r in self.records}
                changed = False
                for row in rows:
                    if row['id'] in self.ignored:
                        continue
                    old = existing.get(row['id'])
                    if old is None:
                        self.records.append(row); changed = True
                    elif not old.get('manual') and (old.get('source') != row.get('source') or old.get('status') != row.get('status')):
                        old.update(row); changed = True
                if changed:
                    self.persist(); self.refresh_list()
                    if not self.selected and self.records:
                        self.selected = self.records[-1]['id']; self.refresh_list()
                    self.load_selected_style();self.request_render(False)
                if changed:
                    self.say(f'Batch loaded: {len(rows)} captures. Select a capture to preview.')
        except Exception as error:
            self.say('Import paused: ' + str(error))
            self.scan_signature = None
        self.root.after(2000, self.scan)

    @staticmethod
    def read_batch(manifest, directory):
        rows = read_manifest(manifest)
        matches = match_batch(rows, directory)
        namespace = hashlib.sha256(str(manifest.resolve()).lower().encode()).hexdigest()[:12]
        for row in rows:
            source, status = matches[row['id']]
            row['id'] = namespace + '-' + row['id']
            row.update(source=str(source) if source else None, status=status)
        return rows

    def choose_image(self):
        return filedialog.askopenfilename(parent=self.root, initialdir=self.screenshots,
                                         filetypes=[('Images', '*.jpg *.jpeg *.png *.tga'), ('All files', '*.*')])

    def locate_original(self):
        row = self.current()
        if not row:
            return
        path = self.choose_image()
        if path:
            try:
                image = open_image(path); crop_image(image, row)
                row.update(source=path, manual=True, status='Original chosen manually')
                self.persist(); self.refresh_list(); self.request_render()
            except Exception as error:
                self.error(error)

    def import_image(self):
        path = self.choose_image()
        if not path:
            return
        try:
            image = open_image(path)
            identity = 'manual-' + datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.records.append(dict(id=identity, addon='Manual import', scene=Path(path).stem, source=path,
                                     x=0, y=0, width=image.width, height=image.height,
                                     screenWidth=image.width, screenHeight=image.height, manual=True, status='Full image'))
            self.selected = identity; self.selected_ids={identity}; self.persist(); self.refresh_list(); self.request_render()
        except Exception as error:
            self.error(error)

    def remove(self):
        if self.selected:
            self.ignored.add(self.selected)
            self.records = [r for r in self.records if r['id'] != self.selected]
            self.selected_ids.discard(self.selected)
            self.selected = None; self.images = None; self.render_generation += 1
            self.rendering = False; self.render_error = None
            self.persist(); self.refresh_list(); self.set_enabled(False); self.draw_preview()
            self.canvas.itemconfigure(self.title_text,text='Your screenshots, ready for the gallery')
            self.canvas.itemconfigure(self.subtitle,text='The same framing across every scene.')
            self.say('Record removed. The original screenshot is unchanged.')

    def save(self, save_as=False):
        if self.batch_running:return
        if len(self.selected_ids)>1:
            self.save_batch(save_as);return
        if not self.images or not self.current():
            return
        r = self.current()
        stem = re.sub(r'[^A-Za-z0-9_.-]+', '-', r['addon']+'-'+r.get('name',r['scene'])).strip('.-')[:100] or 'showcase'
        name = stem + '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.png'
        if save_as:
            path = filedialog.asksaveasfilename(parent=self.root, initialdir=self.output, initialfile=name,
                                              defaultextension='.png', filetypes=[('PNG', '*.png'), ('JPEG (white transparency)', '*.jpg')])
            if not path:
                return
        else:
            path = Path(self.output) / name
            index = 2
            while path.exists():
                path = Path(self.output) / f'{Path(name).stem}-{index}.png'; index += 1
        try:
            # Reject every known original, not only the selected capture's file.
            if Path(path).resolve() in {Path(v['source']).resolve() for v in self.records if v.get('source')}:
                raise ValueError('Choose a different destination; original screenshots are preserved.')
            if Path(path).resolve().parent == Path(self.screenshots).resolve():
                raise ValueError('Export outside the WoW Screenshots folder to preserve its originals.')
            save_image(self.export_image(), path, r['source'])
            self.say('Saved: ' + str(path))
        except Exception as error:
            self.error(error)

    def save_batch(self, choose_folder=False):
        if self.batch_running:return
        destination=filedialog.askdirectory(parent=self.root,initialdir=self.output,title='Save selected images') if choose_folder else self.output
        if not destination:return
        try:default=asdict(self.style())
        except (ValueError,TypeError) as error:self.error(error);return
        rows=[dict(r,style=dict(r.get('style',default))) for r in self.selected_records()]
        if not rows:return
        self.batch_running=True;self.set_enabled(bool(self.images))
        self.say(f'Saving {len(rows)} images…')
        future=self.pool.submit(export_batch,rows,destination,self.view.get(),self.screenshots,[r['source'] for r in self.records if r.get('source')])
        def done():
            if not future.done():self.root.after(100,done);return
            self.batch_running=False;self.set_enabled(bool(self.images))
            try:
                saved,errors=future.result()
                self.say(f'Saved {len(saved)} images to {destination}'+(f' · {len(errors)} failed' if errors else ''))
                if errors:messagebox.showwarning('Batch export',f'Saved {len(saved)} of {len(rows)} images.\n\n'+'\n'.join(errors[:12]),parent=self.root)
            except Exception as error:self.error(error)
        self.root.after(100,done)

    def copy(self):
        if self.images:
            try:
                copy_image(self.export_image(), self.root.winfo_id()); self.say('Image copied. Clipboard transparency is flattened onto white.')
            except Exception as error:
                self.error(error)

    def close(self):
        self.persist(); self.pool.shutdown(wait=False, cancel_futures=True); self.root.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-dir', default=str(Path(os.environ.get('LOCALAPPDATA', Path.home()))/'ForeverShowcase'))
    parser.add_argument('--manifest'); parser.add_argument('--screenshots')
    args = parser.parse_args()
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (OSError, AttributeError):
            pass
    root = tk.Tk()
    App(root, args.state_dir, args.manifest, args.screenshots)
    root.mainloop()


if __name__ == '__main__':
    main()
