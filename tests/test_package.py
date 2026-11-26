import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package', ROOT / 'tools/package.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Packaging(unittest.TestCase):
    def test_allowlist_and_reproducibility(self):
        with TemporaryDirectory() as tmp:
            paths = module.package(tmp)
            initial = [p.read_bytes() for p in paths]
            self.assertEqual(initial, [p.read_bytes() for p in module.package(tmp)])
            with ZipFile(paths[0]) as archive:
                self.assertEqual(set(archive.namelist()), {
                    'ForeverShowcase/ForeverShowcase.toc', 'ForeverShowcase/Core.lua',
                    'ForeverShowcase/Commands.lua', 'ForeverShowcase/Theme.lua', 'ForeverShowcase/UI.lua', 'ForeverShowcase/Presentation.lua', 'ForeverShowcase/Capture.lua', 'ForeverShowcase/CaptureUI.lua',
                    'ForeverShowcase/Media/StagekeeperShell.tga', 'ForeverShowcase/Media/StagekeeperButton.tga',
                    'ForeverShowcase/Media/StagekeeperWordmark.tga'})
                toc = archive.read('ForeverShowcase/ForeverShowcase.toc').decode()
                for line in toc.splitlines():
                    if line and not line.startswith('#'):
                        self.assertIn('ForeverShowcase/' + line, archive.namelist())
                self.assertIn('VERSION = "0.5.2"', archive.read('ForeverShowcase/Core.lua').decode())
                for filename, dimensions in [('StagekeeperShell', (1024,1024)), ('StagekeeperButton', (512,128)), ('StagekeeperWordmark', (1024,256))]:
                    import struct
                    texture = archive.read('ForeverShowcase/Media/' + filename + '.tga')
                    self.assertEqual(texture[2], 2)  # uncompressed true-color TGA
                    self.assertEqual(struct.unpack_from('<HH', texture, 12), dimensions)
                    self.assertEqual(texture[16], 32)  # preserve alpha
            with ZipFile(paths[1]) as archive:
                self.assertEqual(len(archive.namelist()), 2)


if __name__ == '__main__':
    unittest.main()
