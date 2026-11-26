import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from companion.model import (LuaData, ManifestError, read_manifest, validate_record, match_batch,
                             crop_image, Style, render, save_image)


def record(**kwargs):
    r = dict(id='1800000000-1', addon='demo', scene='one', x=10, y=15, width=20, height=30,
             screenWidth=100, screenHeight=80, localTime='112526_130000', localCompleted='112526_130001',
             requestedAt=1800000000, completedAt=1800000001, exported=True)
    r.update(kwargs)
    return r


def lua_literal(value):
    import json
    if isinstance(value, dict):
        return '{' + ','.join('[' + lua_literal(k) + ']=' + lua_literal(v) for k, v in value.items()) + '}'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return json.dumps(value)


class Companion(unittest.TestCase):
    def test_preview_loading_missing_and_failure_copy(self):
        from unittest.mock import Mock
        from companion.app import App
        app = App.__new__(App)
        app.canvas = Mock(); app.preview='preview'; app.empty_text='text'; app.dimensions='dimensions'
        app.images=None; app.current=lambda: {'status':'Missing screenshot'}
        for loading, error, expected in ((True,None,'Preparing preview'), (False,None,'Choose original'),
                                         (False,'Cannot decode file','Preview unavailable')):
            app.rendering=loading; app.render_error=error; app.canvas.reset_mock()
            app.draw_preview()
            call=next(c for c in app.canvas.itemconfigure.call_args_list if c.args==('text',))
            self.assertTrue(call.kwargs['text'].startswith(expected))

    def test_safe_parser_and_manifest(self):
        source = 'ForeverShowcaseDB = ' + lua_literal(dict(schema=1, captures={1: record()}))
        with TemporaryDirectory() as tmp:
            path = Path(tmp)/'ForeverShowcase.lua'; path.write_text(source)
            self.assertEqual(read_manifest(path)[0]['width'], 20)
        for text in (source + '; os.execute("bad")', 'ForeverShowcaseDB = function() end',
                     'ForeverShowcaseDB = {x=1,x=2}', 'ForeverShowcaseDB = ' + '{' * 40,
                     'ForeverShowcaseDB = {x=1e9999}', 'ForeverShowcaseDB = {x="\\999"}'):
            with self.assertRaises(ManifestError):
                LuaData(text).read()
        parsed = LuaData('ForeverShowcaseDB={ ["x"]="a\\n\\034b", -- comment\n [1]=false, }').read()
        self.assertEqual(parsed['x'], 'a\n"b'); self.assertFalse(parsed[1])

    def test_record_validation(self):
        for changes in ({'x': 99}, {'width': -1}, {'screenWidth': True}, {'localTime': 'bad'}, {'completedAt': 1}):
            with self.assertRaises(ManifestError):
                validate_record(record(**changes))

    def test_matching_ambiguity_wrong_dimensions_partial_and_shared(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp)/'WoWScrnShot_112526_130000.jpg'
            Image.new('RGB', (100,80), 'red').save(p)
            self.assertEqual(match_batch([record()], tmp)[record()['id']][0], p.resolve())
            other = Path(tmp)/'WoWScrnShot_112526_130001.jpg'
            Image.new('RGB', (50,50)).save(other)
            self.assertIsNotNone(match_batch([record()], tmp)[record()['id']][0])
            other.write_bytes(b'partial jpg')
            self.assertIsNotNone(match_batch([record()], tmp)[record()['id']][0])
            Image.new('RGB', (100,80), 'blue').save(other)
            self.assertIsNone(match_batch([record()], tmp)[record()['id']][0])
            other.unlink()
            result = match_batch([record(), record(id='other')], tmp)
            self.assertTrue(all(v[0] is None for v in result.values()))
            self.assertIsNone(match_batch([record(review=True)], tmp)[record()['id']][0])

    def test_pixel_exact_crop_style_and_original_protection(self):
        source = Image.new('RGBA', (100,80), 'red'); source.putpixel((10,15), (0,255,0,255))
        cropped = crop_image(source, record())
        self.assertEqual(cropped.size, (20,30)); self.assertEqual(cropped.getpixel((0,0)), (0,255,0,255))
        clean = render(cropped, Style(0,0,0,0))
        self.assertEqual(clean.tobytes(), cropped.tobytes())
        styled = render(cropped, Style(20,8,2,0,transparent=True))
        self.assertEqual(styled.size, (64,74)); self.assertEqual(styled.getpixel((0,0))[3], 0)
        with self.assertRaises(ValueError):
            crop_image(Image.new('RGB',(90,80)), record())
        with TemporaryDirectory() as tmp:
            path = Path(tmp)/'original.png'; source.save(path); before=path.read_bytes()
            with self.assertRaises(ValueError):
                save_image(styled,path,path)
            self.assertEqual(path.read_bytes(),before)
            destination=Path(tmp)/'export.png'; save_image(styled,destination,path)
            with Image.open(destination) as exported:
                self.assertEqual(exported.size, styled.size)


if __name__ == '__main__':
    unittest.main()
