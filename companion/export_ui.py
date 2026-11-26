"""Reusable export dialog: options stay open for successive output variants."""
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from .batch import export_batch, addon_directory
from .exporting import ExportOptions

WOOD,IVORY,INK,PAPER='#28190f','#f9ebcc','#362313','#f7e8ca'

class ExportWindow(tk.Toplevel):
    def __init__(self,app,rows,mode,reference):
        super().__init__(app.root)
        self.app,self.rows,self.mode,self.reference=app,rows,mode,reference
        self.busy=False;self.poll=None;self.syncing=False;self.original=True;self.axis='width'
        self.title('Forever Showcase - Export images')
        self.configure(bg=WOOD);self.resizable(False,False)
        self.transient(app.root)
        self.format=tk.StringVar(value='PNG');self.quality=tk.StringVar(value='95')
        self.width=tk.StringVar(value=str(reference[0]));self.height=tk.StringVar(value=str(reference[1]))
        self.lock=tk.BooleanVar(value=True);self.fit=tk.StringVar(value='Fit inside')
        self.folder=tk.StringVar(value=app.output)
        self.summary=tk.StringVar();self.status=tk.StringVar(value='Ready. Existing exports will not be overwritten.')
        self.form=tk.Frame(self,bg=WOOD,padx=24,pady=20);self.form.pack(fill='both',expand=True)
        f=self.form;f.columnconfigure(1,weight=1)
        self.label(f'Export {len(rows)} image'+('s' if len(rows)!=1 else ''),0,0,3,font=('Segoe UI',18,'bold'))
        self.label(f'{mode} output · Addon folders are created automatically',1,0,3)
        self.label('File type',2,0)
        self.format_box=self.combo(self.format,['PNG','JPEG','WebP'],2,1)
        self.format_box.bind('<<ComboboxSelected>>',lambda e:self.refresh_summary())
        self.label('Quality',3,0)
        self.quality_box=tk.Spinbox(f,from_=1,to=100,textvariable=self.quality,width=8,bg=PAPER,fg=INK,relief='flat',highlightthickness=1,highlightbackground='#a18456')
        self.quality_box.grid(row=3,column=1,sticky='w',pady=4)
        self.label('PNG/WebP keep transparency. JPEG uses white.',4,0,3)
        presets=tk.Frame(f,bg=WOOD);presets.grid(row=5,column=0,columnspan=3,sticky='w',pady=(12,6))
        self.button(presets,'Original size',self.original_size).pack(side='left',padx=(0,10))
        self.button(presets,'850 px wide',self.width_850).pack(side='left')
        self.label('Width (px)',6,0);self.entry(self.width,6,1,12)
        self.label('Height (px)',7,0);self.entry(self.height,7,1,12)
        tk.Checkbutton(f,text='Maintain aspect ratio',variable=self.lock,command=self.lock_changed,bg=WOOD,fg=IVORY,activebackground=WOOD,activeforeground=IVORY,selectcolor='#48161b',cursor='hand2').grid(row=8,column=0,columnspan=3,sticky='w',pady=5)
        self.label('When unlocked',9,0)
        self.fit_box=self.combo(self.fit,['Fit inside','Fill / crop','Stretch'],9,1)
        self.fit_box.bind('<<ComboboxSelected>>',lambda e:self.refresh_summary())
        tk.Label(f,textvariable=self.summary,bg=WOOD,fg=IVORY,justify='left',anchor='nw',height=3,wraplength=540,font=('Segoe UI',10)).grid(row=10,column=0,columnspan=3,sticky='w',pady=(6,10))
        self.label('Base export folder',11,0,3)
        destination=tk.Frame(f,bg=WOOD);destination.grid(row=12,column=0,columnspan=3,sticky='ew',pady=(4,8))
        destination.columnconfigure(0,weight=1)
        tk.Entry(destination,textvariable=self.folder,bg=PAPER,fg=INK,relief='flat',highlightthickness=1,highlightbackground='#a18456',width=52).grid(row=0,column=0,sticky='ew',ipady=5)
        self.button(destination,'Browse...',self.browse).grid(row=0,column=1,padx=(10,0))
        tk.Label(f,textvariable=self.status,bg=WOOD,fg=IVORY,justify='left',anchor='nw',height=4,wraplength=540,font=('Segoe UI',10)).grid(row=13,column=0,columnspan=3,sticky='w',pady=(8,8))
        actions=tk.Frame(f,bg=WOOD);actions.grid(row=14,column=0,columnspan=3,sticky='ew')
        self.export_button=self.button(actions,'Export images' if len(rows)>1 else 'Export image',self.export);self.export_button.pack(side='right')
        self.close_button=self.button(actions,'Close',self.close_window);self.close_button.pack(side='right',padx=10)
        self.button(actions,'Reset to defaults',self.reset).pack(side='left')
        self.width.trace_add('write',lambda *args:self.dimension_changed('width'))
        self.height.trace_add('write',lambda *args:self.dimension_changed('height'))
        self.protocol('WM_DELETE_WINDOW',self.close_window);self.bind('<Escape>',lambda e:self.close_window())
        self.folder.trace_add('write',lambda *args:self.show_destination())
        self.show_destination()
        self.refresh_summary();self.update_idletasks()
        width=max(640,self.winfo_reqwidth());height=self.winfo_reqheight()+10
        x=min(max(0,app.root.winfo_x()+80),max(0,self.winfo_screenwidth()-width-20))
        y=min(max(0,app.root.winfo_y()+20),max(0,self.winfo_screenheight()-height-70))
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.grab_set()
        try:
            import ctypes
            u=ctypes.windll.user32
            u.GetAncestor.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.GetAncestor.restype=ctypes.c_void_p
            dark=ctypes.c_int(1);fn=ctypes.windll.dwmapi.DwmSetWindowAttribute
            fn.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint]
            fn(u.GetAncestor(self.winfo_id(),2),20,ctypes.byref(dark),4)
        except (AttributeError,OSError):pass

    def label(self,text,row,column,span=1,font=('Segoe UI',11)):
        tk.Label(self.form,text=text,bg=WOOD,fg=IVORY,font=font,anchor='w').grid(row=row,column=column,columnspan=span,sticky='w',pady=3,padx=(0,16))

    def entry(self,var,row,column,width):
        widget=tk.Entry(self.form,textvariable=var,width=width,bg=PAPER,fg=INK,relief='flat',highlightthickness=1,highlightbackground='#a18456',font=('Segoe UI',11))
        widget.grid(row=row,column=column,sticky='w',ipady=4,pady=3)
        return widget

    def combo(self,var,values,row,column):
        widget=ttk.Combobox(self.form,textvariable=var,values=values,state='readonly',width=22,style='Showcase.TCombobox')
        widget.grid(row=row,column=column,columnspan=2,sticky='w',pady=4)
        return widget

    def button(self,parent,label,command):
        return tk.Button(parent,text=label,command=command,cursor='hand2',bg='#48161b',fg=IVORY,activebackground='#6b2830',activeforeground='white',relief='flat',highlightthickness=1,highlightbackground='#a18456',padx=12,pady=6)

    def dimension_changed(self,axis):
        if self.syncing:return
        self.original=False;self.axis=axis
        if self.lock.get():
            try:
                value=int((self.width if axis=='width' else self.height).get())
                if value<=0:raise ValueError()
                other=round(value*self.reference[1]/self.reference[0]) if axis=='width' else round(value*self.reference[0]/self.reference[1])
                self.syncing=True
                (self.height if axis=='width' else self.width).set(str(max(1,other)))
            except ValueError:pass
            finally:self.syncing=False
        self.refresh_summary()

    def original_size(self):
        self.syncing=True
        self.width.set(str(self.reference[0]));self.height.set(str(self.reference[1]));self.lock.set(True)
        self.syncing=False;self.original=True;self.axis='width';self.refresh_summary()

    def width_850(self):
        self.lock.set(True);self.width.set('850')

    def lock_changed(self):
        self.original=False
        self.dimension_changed(self.axis)

    def options(self):
        try:
            return ExportOptions(self.format.get(),95 if self.format.get()=='PNG' else int(self.quality.get()),not self.original,int(self.width.get()),int(self.height.get()),self.lock.get(),self.axis,self.fit.get()).validated()
        except ValueError as error:
            if 'invalid literal' in str(error):raise ValueError('Enter whole numbers for dimensions and quality.') from error
            raise

    def refresh_summary(self):
        self.quality_box.configure(state='disabled' if self.format.get()=='PNG' else 'normal')
        self.fit_box.configure(state='disabled' if self.lock.get() else 'readonly')
        try:
            option=self.options();size=option.dimensions(self.reference)
            if self.original:message='Original size: every image keeps its full exported dimensions.'
            elif self.lock.get():message=f'{size[0]} x {size[1]} px for the active image. Each selected image keeps its own aspect ratio using this {self.axis}.'
            else:message=f'All images: {size[0]} x {size[1]} px. '+{'Fit inside':'Adds transparent padding to fit; JPEG padding is white.','Fill / crop':'Crops around the center to fill the chosen dimensions.','Stretch':'Stretches the image to the exact dimensions.'}[self.fit.get()]
            self.summary.set(message)
        except ValueError as error:self.summary.set(str(error))

    def show_destination(self):
        if self.busy:return
        try:
            if not self.folder.get().strip():
                self.status.set('Choose a base export folder.');return
            folders=list(dict.fromkeys(str(addon_directory(self.folder.get(),row)) for row in self.rows))
            if len(folders)==1:
                self.status.set('Images will be saved in:\n'+folders[0])
            else:
                names=', '.join(Path(folder).name for folder in folders)
                self.status.set('Images will be saved in addon subfolders:\n'+names)
        except (ValueError,OSError) as error:self.status.set(str(error))

    def browse(self):
        folder=filedialog.askdirectory(parent=self,initialdir=self.folder.get(),title='Choose export base folder')
        if folder:self.folder.set(folder)

    def reset(self):
        self.format.set('PNG');self.quality.set('95');self.fit.set('Fit inside');self.folder.set(self.app.output)
        self.original_size();self.show_destination()

    def export(self):
        if self.busy or self.app.batch_running:return
        try:
            options=self.options();options.dimensions(self.reference)
            folder=self.folder.get().strip()
            if not folder:raise ValueError('Choose an export folder.')
        except ValueError as error:self.status.set(str(error));return
        self.busy=True;self.app.batch_running=True;self.export_button.configure(state='disabled')
        self.app.set_enabled(bool(self.app.images));self.status.set(f'Exporting {len(self.rows)} images...')
        future=self.app.pool.submit(export_batch,self.rows,folder,self.mode,self.app.screenshots,[r['source'] for r in self.app.records if r.get('source')],options)
        def finished():
            self.poll=None
            if not future.done():self.poll=self.after(100,finished);return
            self.busy=False;self.app.batch_running=False;self.export_button.configure(state='normal');self.app.set_enabled(bool(self.app.images))
            try:
                saved,errors=future.result()
                destinations=list(dict.fromkeys(str(Path(path).parent) for path in saved))
                location=destinations[0] if len(destinations)==1 else 'addon subfolders in '+folder
                message=f'Exported {len(saved)} of {len(self.rows)} images to {location}.'
                if errors:message+=' '+str(len(errors))+' images could not be exported.'
                else:message+=' Change settings to export another version, or reset for full size.'
                self.status.set(message);self.app.say(f'Exported {len(saved)} images.'+(f' {len(errors)} failed.' if errors else ''))
                if errors:messagebox.showwarning('Export results','\n'.join(errors[:12]),parent=self)
            except Exception as error:self.status.set(str(error))
        self.poll=self.after(100,finished)

    def close_window(self):
        if self.busy:self.status.set('Export is still running. This window will remain available when it finishes.');return
        self.destroy()

    def destroy(self):
        if self.poll:self.after_cancel(self.poll);self.poll=None
        super().destroy()
