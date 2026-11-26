"""Independent, resizable image inspector. Never changes the exported image."""
import math
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, image, title):
        super().__init__(parent)
        self.title('Forever Showcase — '+title)
        self.configure(bg='#28190f')
        self.image = image.copy()
        self.fit = True
        self.zoom = 1.0
        self.pending = None
        self.geometry(f'{min(1200,self.winfo_screenwidth()-100)}x{min(850,self.winfo_screenheight()-100)}')
        self.minsize(480,320)
        bar=tk.Frame(self,bg='#28190f',padx=12,pady=10);bar.pack(fill='x')
        for label,command in [('Fit window',self.fit_window),('100%',lambda:self.set_zoom(1)),('−',lambda:self.set_zoom(self.zoom/1.25)),('+',lambda:self.set_zoom(self.zoom*1.25))]:
            tk.Button(bar,text=label,command=command,cursor='hand2',bg='#48161b',fg='#f9ebcc',activebackground='#6b2830',activeforeground='white',relief='flat',padx=12).pack(side='left',padx=3)
        self.info=tk.Label(bar,bg='#28190f',fg='#f9ebcc');self.info.pack(side='right')
        body=tk.Frame(self,bg='#28190f');body.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(body,bg='#211c17',highlightthickness=0,xscrollincrement=24,yscrollincrement=24)
        x=ttk.Scrollbar(body,orient='horizontal',command=self.canvas.xview)
        y=ttk.Scrollbar(body,orient='vertical',command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=x.set,yscrollcommand=y.set)
        self.canvas.grid(row=0,column=0,sticky='nsew');y.grid(row=0,column=1,sticky='ns');x.grid(row=1,column=0,sticky='ew')
        body.rowconfigure(0,weight=1);body.columnconfigure(0,weight=1)
        self.item=self.canvas.create_image(0,0,anchor='nw')
        self.canvas.bind('<Configure>',self.resize)
        self.canvas.bind('<MouseWheel>',lambda e:self.canvas.yview_scroll(-int(e.delta/120),'units'))
        self.canvas.bind('<Shift-MouseWheel>',lambda e:self.canvas.xview_scroll(-int(e.delta/120),'units'))
        self.canvas.bind('<Control-MouseWheel>',lambda e:self.set_zoom(self.zoom*(1.25 if e.delta>0 else .8)))
        self.canvas.bind('<ButtonPress-1>',lambda e:self.canvas.scan_mark(e.x,e.y))
        self.canvas.bind('<B1-Motion>',lambda e:self.canvas.scan_dragto(e.x,e.y,gain=1))
        self.canvas.configure(cursor='fleur')
        self.bind('<Escape>',lambda e:self.destroy())
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.after_idle(self.render)
        # Use the standard managed window lifecycle with a dark native caption.
        try:
            import ctypes
            u=ctypes.windll.user32
            u.GetAncestor.argtypes=[ctypes.c_void_p,ctypes.c_uint];u.GetAncestor.restype=ctypes.c_void_p
            dark=ctypes.c_int(1)
            dwm=ctypes.windll.dwmapi.DwmSetWindowAttribute
            dwm.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint]
            dwm(u.GetAncestor(self.winfo_id(),2),20,ctypes.byref(dark),4)
        except (AttributeError,OSError): pass

    def resize(self,event):
        if self.pending: self.after_cancel(self.pending)
        self.pending=self.after(60,self.render)

    def fit_window(self):
        self.fit=True;self.render()

    def set_zoom(self,value):
        self.fit=False
        maximum=min(4,math.sqrt(50_000_000/(self.image.width*self.image.height)))
        self.zoom=max(.05,min(maximum,value));self.render()

    def render(self):
        self.pending=None
        w,h=max(1,self.canvas.winfo_width()),max(1,self.canvas.winfo_height())
        if self.fit:self.zoom=min(1,w/self.image.width,h/self.image.height)
        size=(max(1,round(self.image.width*self.zoom)),max(1,round(self.image.height*self.zoom)))
        rendered=self.image if size==self.image.size else self.image.resize(size,Image.Resampling.LANCZOS)
        self.photo=ImageTk.PhotoImage(rendered)
        self.canvas.itemconfigure(self.item,image=self.photo)
        self.canvas.coords(self.item,max(0,(w-size[0])//2),max(0,(h-size[1])//2))
        self.canvas.configure(scrollregion=(0,0,max(w,size[0]),max(h,size[1])))
        if self.fit:self.canvas.xview_moveto(0);self.canvas.yview_moveto(0)
        self.info.configure(text=f'{self.image.width} × {self.image.height} px  ·  {self.zoom:.0%}')

    def destroy(self):
        if self.pending:self.after_cancel(self.pending);self.pending=None
        super().destroy()
