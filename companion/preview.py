"""Independent, resizable image inspector. Never changes the exported image."""
import math
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def viewport_tile(image, scaled_size, bounds):
    """Render only visible display pixels, including filter support at edges."""
    left,top,right,bottom=bounds
    width,height=right-left,bottom-top
    if scaled_size==image.size:return image.crop(bounds)
    sx,sy=image.width/scaled_size[0],image.height/scaled_size[1]
    box=(left*sx,top*sy,right*sx,bottom*sy)
    # Crop before resizing so Pillow also limits alpha conversion/filter work.
    support=math.ceil(3*max(1,sx,sy))
    crop=(max(0,math.floor(box[0])-support),max(0,math.floor(box[1])-support),min(image.width,math.ceil(box[2])+support),min(image.height,math.ceil(box[3])+support))
    region=image.crop(crop)
    local=(box[0]-crop[0],box[1]-crop[1],box[2]-crop[0],box[3]-crop[1])
    return region.resize((width,height),Image.Resampling.LANCZOS,box=local)


class PreviewWindow(tk.Toplevel):
    def __init__(self, parent, image, title):
        super().__init__(parent)
        self.title('Forever Showcase â€” '+title)
        self.configure(bg='#28190f')
        self.image = image.copy()
        self.fit = True
        self.zoom = 1.0
        self.pending = None
        self.paint_pending = None
        self.zoom_anchor = None
        self.scroll_seen = {}
        self.geometry(f'{min(1200,self.winfo_screenwidth()-100)}x{min(850,self.winfo_screenheight()-100)}')
        self.minsize(480,320)
        bar=tk.Frame(self,bg='#28190f',padx=12,pady=10);bar.pack(fill='x')
        for label,command in [('Fit window',self.fit_window),('100%',lambda:self.set_zoom(1)),('âˆ’',lambda:self.set_zoom(self.zoom/1.25)),('+',lambda:self.set_zoom(self.zoom*1.25))]:
            tk.Button(bar,text=label,command=command,cursor='hand2',bg='#48161b',fg='#f9ebcc',activebackground='#6b2830',activeforeground='white',relief='flat',padx=12).pack(side='left',padx=3)
        self.info=tk.Label(bar,bg='#28190f',fg='#f9ebcc');self.info.pack(side='right')
        body=tk.Frame(self,bg='#28190f');self.body=body;body.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(body,bg='#211c17',highlightthickness=0,xscrollincrement=24,yscrollincrement=24)
        x=ttk.Scrollbar(body,orient='horizontal',command=lambda *args:self.scroll('x',*args))
        y=ttk.Scrollbar(body,orient='vertical',command=lambda *args:self.scroll('y',*args))
        self.horizontal,self.vertical=x,y
        self.canvas.configure(xscrollcommand=lambda a,b:self.scrolled('x',a,b),yscrollcommand=lambda a,b:self.scrolled('y',a,b))
        self.canvas.grid(row=0,column=0,sticky='nsew')
        body.rowconfigure(0,weight=1);body.columnconfigure(0,weight=1)
        self.item=self.canvas.create_image(0,0,anchor='nw')
        self.canvas.bind('<Configure>',self.resize)
        self.canvas.bind('<MouseWheel>',self.wheel_zoom)
        self.canvas.bind('<Shift-MouseWheel>',lambda e:self.scroll('x','scroll',-int(e.delta/120),'units'))
        self.canvas.bind('<Control-MouseWheel>',self.wheel_zoom)
        self.canvas.bind('<ButtonPress-1>',lambda e:self.canvas.scan_mark(e.x,e.y))
        self.canvas.bind('<B1-Motion>',self.pan)
        self.canvas.configure(cursor='fleur')
        self.bind('<Escape>',lambda e:self.destroy())
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.pending=self.after_idle(self.render)
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

    def schedule_render(self):
        if self.pending is None:self.pending=self.after(16,self.render)

    def resize(self,event):
        self.schedule_render()

    def fit_window(self):
        self.fit=True;self.zoom_anchor=None;self.schedule_render()

    def set_zoom(self,value):
        if self.zoom_anchor is None and hasattr(self,'rendered_size'):
            w,h=self.canvas.winfo_width(),self.canvas.winfo_height()
            ox,oy=self.origin
            self.zoom_anchor=((self.canvas.canvasx(w/2)-ox)/self.rendered_size[0],(self.canvas.canvasy(h/2)-oy)/self.rendered_size[1])
        self.fit=False
        self.zoom=max(.05,min(4,value));self.schedule_render()

    def wheel_zoom(self,event):
        if event.delta:self.set_zoom(self.zoom*(1.25 if event.delta>0 else .8))
        return 'break'

    def scroll(self,axis,*args):
        getattr(self.canvas,axis+'view')(*args)
        self.schedule_paint()

    def pan(self,event):
        self.canvas.scan_dragto(event.x,event.y,gain=1)
        self.schedule_paint()

    def scrolled(self,axis,first,last):
        (self.horizontal if axis=='x' else self.vertical).set(first,last)
        value=(first,last)
        if self.scroll_seen.get(axis)!=value:
            self.scroll_seen[axis]=value
            self.schedule_paint()

    def schedule_paint(self):
        if self.paint_pending is None:self.paint_pending=self.after(16,self.paint)

    def render(self):
        if self.pending:self.after_cancel(self.pending)
        self.pending=None
        # Decide overflow against the whole viewport, then account for the
        # space consumed by necessary bars. This avoids fit/bar feedback loops.
        full_w,full_h=max(1,self.body.winfo_width()),max(1,self.body.winfo_height())
        if self.fit:self.zoom=min(1,full_w/self.image.width,full_h/self.image.height)
        size=(max(1,round(self.image.width*self.zoom)),max(1,round(self.image.height*self.zoom)))
        need_x=need_y=False
        for _ in range(3):
            w=full_w-(self.vertical.winfo_reqwidth() if need_y else 0)
            h=full_h-(self.horizontal.winfo_reqheight() if need_x else 0)
            need_x,need_y=size[0]>w,size[1]>h
        if need_x:self.horizontal.grid(row=1,column=0,sticky='ew')
        else:self.horizontal.grid_remove()
        if need_y:self.vertical.grid(row=0,column=1,sticky='ns')
        else:self.vertical.grid_remove()
        w=max(1,full_w-(self.vertical.winfo_reqwidth() if need_y else 0))
        h=max(1,full_h-(self.horizontal.winfo_reqheight() if need_x else 0))
        self.rendered_size=size
        self.origin=(max(0,(w-size[0])//2),max(0,(h-size[1])//2))
        self.canvas.configure(scrollregion=(0,0,max(w,size[0]),max(h,size[1])))
        if self.zoom_anchor is not None and not self.fit:
            fx,fy=self.zoom_anchor
            self.canvas.xview_moveto((self.origin[0]+fx*size[0]-w/2)/max(w,size[0]))
            self.canvas.yview_moveto((self.origin[1]+fy*size[1]-h/2)/max(h,size[1]))
        self.zoom_anchor=None
        if not need_x:self.canvas.xview_moveto(0)
        if not need_y:self.canvas.yview_moveto(0)
        self.info.configure(text=f'{self.image.width} Ã— {self.image.height} px  Â·  {self.zoom:.0%}')
        self.paint()

    def paint(self):
        if self.paint_pending:self.after_cancel(self.paint_pending)
        self.paint_pending=None
        if not hasattr(self,'rendered_size'):return
        w,h=self.canvas.winfo_width(),self.canvas.winfo_height()
        ox,oy=self.origin
        # A small surrounding margin keeps short drag movements covered while
        # the next frame is queued. Allocation never follows the full zoom size.
        left=max(0,math.floor(self.canvas.canvasx(0)-ox)-96)
        top=max(0,math.floor(self.canvas.canvasy(0)-oy)-96)
        right=min(self.rendered_size[0],math.ceil(self.canvas.canvasx(w)-ox)+96)
        bottom=min(self.rendered_size[1],math.ceil(self.canvas.canvasy(h)-oy)+96)
        if right<=left or bottom<=top:return
        key=(self.rendered_size,left,top,right,bottom)
        if key==getattr(self,'tile_key',None):return
        rendered=viewport_tile(self.image,self.rendered_size,(left,top,right,bottom))
        photo=ImageTk.PhotoImage(rendered)
        self.canvas.itemconfigure(self.item,image=photo)
        self.canvas.coords(self.item,ox+left,oy+top)
        self.photo=photo;self.tile_key=key

    def destroy(self):
        if self.paint_pending:self.after_cancel(self.paint_pending);self.paint_pending=None
        if self.pending:self.after_cancel(self.pending);self.pending=None
        super().destroy()
