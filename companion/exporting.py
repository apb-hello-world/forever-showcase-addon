"""Final-image export sizing, independent of capture and styling settings."""
from dataclasses import dataclass
from PIL import Image,ImageOps

@dataclass(frozen=True)
class ExportOptions:
    format: str = 'PNG'
    quality: int = 95
    resize: bool = False
    width: int = 850
    height: int = 850
    maintain_ratio: bool = True
    axis: str = 'width'
    fit: str = 'Fit inside'

    def validated(self):
        if self.format not in ('PNG','JPEG','WebP'):raise ValueError('Choose PNG, JPEG or WebP.')
        if type(self.quality) is not int or not 1<=self.quality<=100:raise ValueError('Quality must be between 1 and 100.')
        if self.axis not in ('width','height'):raise ValueError('Invalid sizing axis.')
        if self.fit not in ('Fit inside','Fill / crop','Stretch'):raise ValueError('Invalid resize behavior.')
        if self.resize:
            for name,value in [('Width',self.width),('Height',self.height)]:
                if type(value) is not int or not 1<=value<=32768:raise ValueError(name+' must be between 1 and 32768 pixels.')
        return self

    @property
    def extension(self):return {'PNG':'.png','JPEG':'.jpg','WebP':'.webp'}[self.format]

    def dimensions(self,source):
        self.validated()
        if not self.resize:return source
        w,h=self.width,self.height
        if self.maintain_ratio:
            if self.axis=='width':h=max(1,round(w*source[1]/source[0]))
            else:w=max(1,round(h*source[0]/source[1]))
        if w>32768 or h>32768 or w*h>50_000_000:raise ValueError('Export dimensions exceed the 50 megapixel limit.')
        return w,h


def resize_export(image,options):
    size=options.dimensions(image.size)
    if size==image.size:return image
    if options.maintain_ratio or options.fit=='Stretch':return image.resize(size,Image.Resampling.LANCZOS)
    if options.fit=='Fill / crop':return ImageOps.fit(image,size,Image.Resampling.LANCZOS)
    contained=ImageOps.contain(image,size,Image.Resampling.LANCZOS)
    output=Image.new('RGBA',size,(0,0,0,0))
    output.alpha_composite(contained.convert('RGBA'),((size[0]-contained.width)//2,(size[1]-contained.height)//2))
    return output
