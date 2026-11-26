import hashlib
import tempfile
import unittest
from pathlib import Path
from dataclasses import asdict
from unittest.mock import patch
from PIL import Image
from companion.batch import export_batch, addon_directory
from companion.model import Style
from companion import updates

class BatchAndUpdates(unittest.TestCase):
    def test_batch_styles_unique_files_and_partial_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png';Image.new('RGB',(40,30),'red').save(source)
            before=source.read_bytes()
            row=dict(id='a',addon='Test',scene='Editor',source=str(source),x=0,y=0,width=20,height=10,screenWidth=40,screenHeight=30,style=asdict(Style(padding=0,shadow=0,border=0,radius=0)))
            saved,errors=export_batch([row,dict(row,id='b'),dict(row,id='c',source=None)],root/'exports','Styled',root/'screenshots',[source])
            self.assertEqual(Path(saved[0]).parent,root/'exports'/'Test')
            self.assertEqual(len(saved),2);self.assertEqual(len(errors),1);self.assertNotEqual(saved[0],saved[1])
            with Image.open(saved[0]) as image:self.assertEqual(image.size,(20,10))
            self.assertEqual(source.read_bytes(),before)
            with self.assertRaises(ValueError):export_batch([row],root/'screenshots','Styled',root/'screenshots',[source])

    def test_mixed_addons_and_display_name_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png';Image.new('RGB',(10,10),'red').save(source)
            row=dict(addon='spellwright',addonTitle='Spellwright',scene='Editor',source=str(source),style=asdict(Style()))
            saved,errors=export_batch([row,dict(row,addon='wayside',addonTitle='Wayside'),dict(row,addon='legacy',addonTitle='')],root/'exports','Original',root/'screenshots',[source])
            self.assertEqual(errors,[])
            self.assertEqual({Path(p).parent.name for p in saved},{'Spellwright','Wayside','legacy'})
            for name in ('../outside','C:\\elsewhere','CON','...','|cffffffffSpellwright|r'):
                folder=addon_directory(root,dict(addon=name))
                self.assertEqual(folder.parent,root.resolve())
                self.assertNotIn(folder.name,('CON','..','.'))
            self.assertEqual(addon_directory(root,dict(addon='|cffffffffSpellwright|r')).name,'Spellwright')

    def release(self,number='0.7.0'):
        tag='companion-v'+number;name=f'ForeverShowcaseCompanion-Setup-{number}.exe'
        return dict(tag_name=tag,assets=[dict(name=n,browser_download_url=updates.PREFIX+tag+'/'+n) for n in (name,name+'.sha256')])

    def test_only_new_stable_companion_releases(self):
        r=self.release()
        self.assertEqual(updates.select_release([r],'0.6.0')['version'],'0.7.0')
        self.assertIsNone(updates.select_release([r],'0.7.0'))
        self.assertIsNone(updates.select_release([dict(r,prerelease=True)],'0.6.0'))
        self.assertIsNone(updates.select_release([dict(r,tag_name='addon-v0.7.0')],'0.6.0'))
        r['assets'][0]['browser_download_url']='https://example.com/evil.exe'
        self.assertIsNone(updates.select_release([r],'0.6.0'))

    def test_download_rejects_checksum_mismatch(self):
        import io
        release=updates.select_release([self.release()],'0.6.0')
        with patch.object(updates,'read_url',return_value=b'0'*64),patch.object(updates,'urlopen',return_value=io.BytesIO(b'incorrect installer')):
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):updates.download_update(release)

    def test_download_verified_bytes(self):
        import io
        content=b'installer fixture';release=updates.select_release([self.release()],'0.6.0')
        with tempfile.TemporaryDirectory() as d,patch.object(updates.tempfile,'mkdtemp',return_value=d),patch.object(updates,'read_url',return_value=hashlib.sha256(content).hexdigest().encode()),patch.object(updates,'urlopen',return_value=io.BytesIO(content)):
            target=updates.download_update(release);self.assertEqual(target.read_bytes(),content)
