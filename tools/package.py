"""Deterministic allowlisted archives; no publication or installation."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def package(output=None):
    output = Path(output or ROOT / 'dist')
    output.mkdir(parents=True, exist_ok=True)
    specs = (
        ('ForeverShowcase', ROOT, ('ForeverShowcase.toc', 'Core.lua', 'Theme.lua', 'UI.lua', 'Presentation.lua', 'Capture.lua', 'CaptureUI.lua', 'Commands.lua', 'SelfShowcase.lua',
                                 'Media/StagekeeperShell.tga', 'Media/StagekeeperButton.tga', 'Media/StagekeeperWordmark.tga')),
        ('ForeverShowcaseExample', ROOT / 'examples', ('ForeverShowcaseExample.toc', 'Example.lua')),
    )
    paths = []
    for name, base, files in specs:
        version = next(line.split(':', 1)[1].strip() for line in
                       (base / name / files[0]).read_text().splitlines() if line.startswith('## Version:'))
        path = output / f'{name}-{version}.zip'
        with ZipFile(path, 'w', compression=ZIP_DEFLATED) as archive:
            for filename in files:
                info = ZipInfo(f'{name}/{filename}', date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, (base / name / filename).read_bytes())
        paths.append(path)
    return paths


if __name__ == '__main__':
    for path in package():
        print(path)
