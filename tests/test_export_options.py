import tempfile
import unittest
from pathlib import Path
from PIL import Image
from companion.exporting import ExportOptions,resize_export
from companion.batch import export_batch

class ExportSizing(unittest.TestCase):
    def test_width_and_height_lock_use_each_images_ratio(self):
        width=ExportOptions(resize=True,width=850,height=600)
        self.assertEqual(width.dimensions((1655,1117)),(850,574))
        self.assertEqual(width.dimensions((2000,1000)),(850,425))
        self.assertEqual(width.dimensions((1000,2000)),(850,1700))
        height=ExportOptions(resize=True,width=850,height=500,axis='height')
        self.assertEqual(height.dimensions((2000,1000)),(1000,500))
        self.assertEqual(ExportOptions().dimensions((1655,1117)),(1655,1117))

    def test_unlocked_fit_crop_stretch(self):
        image=Image.new('RGBA',(200,100),'red')
        for mode in ('Fit inside','Fill / crop','Stretch'):
            result=resize_export(image,ExportOptions(resize=True,width=100,height=100,maintain_ratio=False,fit=mode))
            self.assertEqual(result.size,(100,100))
            self.assertEqual(result.getpixel((0,0))[3],0 if mode=='Fit inside' else 255)
        self.assertEqual(image.size,(200,100))

    def test_size_limits_and_invalid_values(self):
        for options in (ExportOptions(resize=True,width=0),ExportOptions(format='bad'),ExportOptions(quality=101),ExportOptions(resize=True,width=32768)):
            with self.assertRaises(ValueError):options.dimensions((200,100))

    def test_formats_repeat_exports_and_original_safety(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png'
            Image.new('RGBA',(80,40),(50,100,150,0)).save(source);before=source.read_bytes()
            row=dict(id='one',addon='test',scene='Overview',source=str(source))
            for format,expected in [('PNG','PNG'),('JPEG','JPEG'),('WebP','WEBP')]:
                opts=ExportOptions(format=format,resize=True,width=40)
                saved,errors=export_batch([row],root/'out','Original',root/'screenshots',[source],opts)
                self.assertEqual(errors,[])
                with Image.open(saved[0]) as image:
                    self.assertEqual(image.format,expected);self.assertEqual(image.size,(40,20))
                    if format=='JPEG':self.assertEqual(image.convert('RGB').getpixel((0,0)),(255,255,255))
                    else:self.assertEqual(image.convert('RGBA').getpixel((0,0))[3],0)
            again,errors=export_batch([row],root/'out','Original',root/'screenshots',[source],ExportOptions())
            with Image.open(again[0]) as image:self.assertEqual(image.size,(80,40))
            self.assertEqual(source.read_bytes(),before)

    def test_optional_subfolders_and_mixed_addons(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png'
            Image.new('RGBA',(80,40),'red').save(source)
            rows=[dict(id=name,addon=name,scene='Overview',source=str(source)) for name in ('Spellwright','Wayside')]
            for subfolder in ('','large','thumbnails'):
                saved,errors=export_batch(rows,root/'out','Original',root/'screenshots',[source],ExportOptions(subfolder=subfolder))
                self.assertEqual(errors,[])
                for path,row in zip(saved,rows):
                    self.assertEqual(Path(path).parent,(root/'out'/row['addon']/subfolder).resolve())
            for invalid in ('..','../escape','a/b',r'a\b','D:\\escape','CON','NUL.png','bad.','bad?'):
                with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                    export_batch(rows,root/'out','Original',root/'screenshots',[source],ExportOptions(subfolder=invalid))
