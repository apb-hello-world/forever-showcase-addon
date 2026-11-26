"""Back up and hash-verify the single local runtime. Never touch saved variables."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ForeverShowcase'
TARGET = Path('E:/World of Warcraft/_forever_/Interface/AddOns/ForeverShowcase')
VERSION = next(line.split(':',1)[1].strip() for line in (SOURCE / 'ForeverShowcase.toc').read_text(encoding='utf-8').splitlines() if line.startswith('## Version:'))
BACKUP = ROOT.parent / 'backups' / ('showcase-before-' + VERSION + '-' + datetime.now().strftime('%Y%m%d-%H%M%S'))

if TARGET.is_dir():
    BACKUP.mkdir(parents=True, exist_ok=False)
    shutil.copytree(TARGET, BACKUP / TARGET.name)
TARGET.mkdir(parents=True, exist_ok=True)
receipt = {'version': VERSION, 'target': str(TARGET), 'backup': str(BACKUP), 'files': {}}
for source in SOURCE.rglob('*'):
    if source.is_file():
        relative = source.relative_to(SOURCE)
        target = TARGET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        assert expected == hashlib.sha256(target.read_bytes()).hexdigest(), str(target)
        receipt['files'][relative.as_posix()] = expected
(ROOT / ('design/installation-' + VERSION + '.json')).write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(f'Installed and hash-verified {len(receipt["files"])} runtime files. Backup: {BACKUP}')
