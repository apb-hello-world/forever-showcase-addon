"""Build the per-user installer and its release checksum."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from companion.version import VERSION
compiler=os.environ.get('ISCC') or shutil.which('ISCC')
if not compiler:
    compiler=next((str(p) for p in [Path(os.environ.get('LOCALAPPDATA',''))/'Programs/Inno Setup 6/ISCC.exe',Path('C:/Program Files (x86)/Inno Setup 6/ISCC.exe')] if p.is_file()),None)
if not compiler:raise SystemExit('Install Inno Setup 6 or set ISCC to its compiler path.')
subprocess.run([compiler,'/Q','/DAppVersion='+VERSION,str(ROOT/'installer/companion.iss')],check=True,cwd=ROOT)
installer=ROOT/'dist'/f'ForeverShowcaseCompanion-Setup-{VERSION}.exe'
installer.with_suffix('.exe.sha256').write_text(hashlib.sha256(installer.read_bytes()).hexdigest()+'  '+installer.name+'\n',encoding='ascii')
print(installer)
