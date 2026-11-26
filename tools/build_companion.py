"""Local portable Windows build. No installer, publishing, or game-file writes."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
import py_compile
for source in (ROOT / 'companion').glob('*.py'):
    py_compile.compile(str(source), doraise=True)
args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--onedir',
        '--name', 'ForeverShowcaseCompanion', '--paths', str(ROOT),
        '--distpath', str(ROOT / 'dist'), '--workpath', str(ROOT / 'build/companion'),
        '--specpath', str(ROOT / 'build')]
for name in ('StagekeeperShell.png', 'StagekeeperButton.png', 'StagekeeperWordmark-runtime.png'):
    args.extend(['--add-data', f'{ROOT / "design/assets" / name};design/assets'])
args.append(str(ROOT / 'companion/launcher.py'))
subprocess.run(args, cwd=ROOT, check=True)
