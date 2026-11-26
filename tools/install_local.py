"""Back up and hash-verify the single local runtime. Never touch saved variables."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ForeverShowcase'
TARGET = Path('E:/World of Warcraft/_forever_/Interface/AddOns/ForeverShowcase')
BACKUP = ROOT.parent / 'backups' / ('showcase-before-0.5.0-' + datetime.now().strftime('%Y%m%d-%H%M%S'))

if TARGET.is_dir():
    BACKUP.mkdir(parents=True, exist_ok=False)
    shutil.copytree(TARGET, BACKUP / TARGET.name)
TARGET.mkdir(parents=True, exist_ok=True)
receipt = {'version': '0.5.0', 'target': str(TARGET), 'backup': str(BACKUP), 'files': {}}
for source in SOURCE.rglob('*'):
    if source.is_file():
        relative = source.relative_to(SOURCE)
        target = TARGET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        assert expected == hashlib.sha256(target.read_bytes()).hexdigest(), str(target)
        receipt['files'][relative.as_posix()] = expected
(ROOT / 'design/installation-0.5.0.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(f'Installed and hash-verified {len(receipt["files"])} runtime files. Backup: {BACKUP}')
