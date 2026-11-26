"""Embed provenance without changing PNG pixels; export original artwork for WoW."""
from pathlib import Path
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]


def embed_note(path, note):
    raw = path.read_bytes()
    signature = b'\x89PNG\r\n\x1a\n'
    if not raw.startswith(signature):
        raise ValueError(f'Not a PNG: {path}')
    output, pos = bytearray(signature), 8
    while pos < len(raw):
        size = struct.unpack_from('>I', raw, pos)[0]
        kind = raw[pos+4:pos+8]
        data = raw[pos+8:pos+8+size]
        if kind == b'IEND':
            payload = b'Generation provenance\0' + note.encode('latin-1', errors='replace')
            output += struct.pack('>I', len(payload)) + b'tEXt' + payload
            output += struct.pack('>I', zlib.crc32(b'tEXt'+payload) & 0xffffffff)
        if not (kind == b'tEXt' and data.startswith(b'Generation provenance\0')):
            output += raw[pos:pos+size+12]
        pos += size+12
    path.write_bytes(output)


if __name__ == '__main__':
    provenance = (ROOT / 'design/assets/PROVENANCE.md').read_text(encoding='utf-8')
    for name, size in [('StagekeeperShell','1024:1024'), ('StagekeeperButton','512:128'), ('StagekeeperWordmark','1024:256')]:
        source = ROOT / 'design/assets' / (name+'.png')
        note = (ROOT / 'design/assets/WORDMARK-PROMPT.md').read_text(encoding='utf-8') if name == 'StagekeeperWordmark' else provenance
        embed_note(source, note)
        filters = 'scale='+size
        if name == 'StagekeeperWordmark':
            # Measured visible alpha bounds plus a 10-pixel antialias margin.
            # Preserve glyph proportions and center on a power-of-two canvas.
            filters = 'crop=2090:310:48:182,scale=1024:256:force_original_aspect_ratio=decrease,pad=1024:256:(ow-iw)/2:(oh-ih)/2:color=black@0'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(source),'-vf',filters,
                        '-pix_fmt','bgra','-c:v','targa','-rle','0',
                        str(ROOT/'ForeverShowcase/Media'/(name+'.tga'))], check=True)
        print('Exported', name)
