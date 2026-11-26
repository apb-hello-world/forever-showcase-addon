import unittest
from PIL import Image,ImageChops,ImageStat
from companion.preview import viewport_tile

class PreviewRendering(unittest.TestCase):
    def test_actual_size_is_exact_crop(self):
        image=Image.effect_noise((256,192),60).convert('RGBA')
        bounds=(30,20,160,120)
        self.assertEqual(viewport_tile(image,image.size,bounds).tobytes(),image.crop(bounds).tobytes())

    def test_zoom_tile_matches_full_image_reference(self):
        image=Image.effect_noise((256,192),60).convert('RGBA')
        for scale in (.5,1.25,2,4):
            size=(round(image.width*scale),round(image.height*scale))
            bounds=(12,16,min(size[0],112),min(size[1],86))
            tile=viewport_tile(image,size,bounds)
            expected=image.resize(size,Image.Resampling.LANCZOS).crop(bounds)
            self.assertLessEqual(max(ImageStat.Stat(ImageChops.difference(tile,expected)).mean),1)

    def test_large_zoom_allocates_only_requested_pixels(self):
        image=Image.new('RGBA',(3840,2160),(20,30,40,128))
        tile=viewport_tile(image,(15360,8640),(9000,5000,10280,5800))
        self.assertEqual(tile.size,(1280,800))
        self.assertEqual(tile.getpixel((500,500)),(19,29,39,128))
