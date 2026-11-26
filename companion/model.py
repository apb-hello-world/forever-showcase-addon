"""Read-only WoW imports, conservative matching, and nondestructive image exports."""
from __future__ import annotations

import io
import re
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageColor

Image.MAX_IMAGE_PIXELS = 40_000_000
MAX_BYTES = 8 * 1024 * 1024


class ManifestError(ValueError):
    pass


class LuaData:
    """A bounded literal reader, never a Lua interpreter. Accept SavedVariables syntax."""
    def __init__(self, source: str):
        if len(source) > MAX_BYTES:
            raise ManifestError('Capture manifest is too large.')
        self.source = source.lstrip('\ufeff')
        self.pos = 0
        self.items = 0

    def space(self):
        while self.pos < len(self.source):
            if self.source[self.pos].isspace():
                self.pos += 1
            elif self.source.startswith('--', self.pos):
                end = self.source.find('\n', self.pos)
                self.pos = len(self.source) if end < 0 else end + 1
            else:
                break

    def take(self, text):
        self.space()
        if self.source.startswith(text, self.pos):
            self.pos += len(text)
            return True
        return False

    def require(self, text):
        if not self.take(text):
            raise ManifestError(f'Expected {text!r} at character {self.pos}.')

    def string(self):
        quote = self.source[self.pos]
        self.pos += 1
        result = []
        escapes = {'n': '\n', 'r': '\r', 't': '\t', 'b': '\b', 'f': '\f',
                   'v': '\v', 'a': '\a', '\\': '\\', '"': '"', "'": "'"}
        while self.pos < len(self.source):
            c = self.source[self.pos]
            self.pos += 1
            if c == quote:
                return ''.join(result)
            if c == '\\':
                if self.pos == len(self.source):
                    break
                c = self.source[self.pos]
                self.pos += 1
                if c.isdigit():
                    digits = c
                    while len(digits) < 3 and self.pos < len(self.source) and self.source[self.pos].isdigit():
                        digits += self.source[self.pos]
                        self.pos += 1
                    code = int(digits)
                    if code > 255:
                        raise ManifestError('Invalid string escape.')
                    result.append(chr(code))
                elif c in escapes:
                    result.append(escapes[c])
                elif c == '\n':
                    result.append('\n')
                else:
                    raise ManifestError('Unsupported string escape.')
            else:
                result.append(c)
        raise ManifestError('Unfinished string; waiting for WoW to finish saving.')

    def value(self, depth=0):
        self.space()
        self.items += 1
        if depth > 24 or self.items > 50000:
            raise ManifestError('Capture manifest exceeds the data limits.')
        if self.pos >= len(self.source):
            raise ManifestError('Incomplete capture manifest.')
        c = self.source[self.pos]
        if c in "\"'":
            return self.string()
        if c == '{':
            self.pos += 1
            table, index = {}, 1
            while not self.take('}'):
                if self.take('['):
                    key = self.value(depth + 1)
                    if not isinstance(key, (str, int)) or isinstance(key, bool):
                        raise ManifestError('Invalid table key.')
                    self.require(']'); self.require('=')
                else:
                    self.space()
                    match = re.match(r'([A-Za-z_]\w*)\s*=', self.source[self.pos:])
                    if match:
                        key = match[1]
                        self.pos += match.end()
                    else:
                        key, index = index, index + 1
                if key in table:
                    raise ManifestError('Duplicate table key.')
                table[key] = self.value(depth + 1)
                if self.take('}'):
                    return table
                if not self.take(',') and not self.take(';'):
                    raise ManifestError('Missing table separator.')
            return table
        token = re.match(r'(?:-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true\b|false\b|nil\b)', self.source[self.pos:])
        if not token:
            raise ManifestError('Only literal SavedVariables data is accepted.')
        self.pos += token.end()
        text = token[0]
        if text in ('true', 'false', 'nil'):
            return {'true': True, 'false': False, 'nil': None}[text]
        value = float(text) if any(c in text for c in '.eE') else int(text)
        if not math.isfinite(value):
            raise ManifestError('Nonfinite number.')
        return value

    def read(self):
        self.require('ForeverShowcaseDB'); self.require('=')
        result = self.value()
        self.take(';'); self.space()
        if self.pos != len(self.source):
            raise ManifestError('Unexpected code after capture data.')
        return result


def integer(row, key, low=0, high=100000):
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high or int(value) != value:
        raise ManifestError(f'Invalid {key}.')
    return int(value)


def validate_record(row):
    if not isinstance(row, dict):
        raise ManifestError('Invalid capture record.')
    result = {}
    for key in ('id', 'addon', 'scene', 'localTime', 'localCompleted'):
        value = row.get(key)
        if not isinstance(value, str) or not value or len(value) > 200:
            raise ManifestError(f'Invalid {key}.')
        result[key] = value
    for key in ('x', 'y', 'width', 'height', 'screenWidth', 'screenHeight'):
        result[key] = integer(row, key, 0 if key in ('x', 'y') else 1, 32768)
    if result['x'] + result['width'] > result['screenWidth'] or result['y'] + result['height'] > result['screenHeight']:
        raise ManifestError('Crop falls outside the screenshot.')
    if result['screenWidth'] * result['screenHeight'] > Image.MAX_IMAGE_PIXELS:
        raise ManifestError('Screenshot resolution exceeds the 40 megapixel limit.')
    for key in ('requestedAt', 'completedAt'):
        result[key] = integer(row, key, 0, 10_000_000_000)
    if not 0 <= result['completedAt'] - result['requestedAt'] <= 15:
        raise ManifestError('Invalid capture time interval.')
    for key in ('localTime', 'localCompleted'):
        try:
            datetime.strptime(result[key], '%m%d%y_%H%M%S')
        except ValueError as error:
            raise ManifestError('Invalid local capture time.') from error
    if isinstance(row.get('name'), str):
        result['name'] = row['name'][:512]
    if isinstance(row.get('addonTitle'), str):
        result['addonTitle'] = row['addonTitle'][:512]
    result['review'] = bool(row.get('review'))
    result['exported'] = row.get('exported') is True
    return result


def read_manifest(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ManifestError('Capture manifest is too large.')
    data = LuaData(path.read_text(encoding='utf-8')).read()
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ManifestError('Unsupported capture format; update the companion.')
    table = data.get('captures', {})
    if not isinstance(table, dict) or len(table) > 200:
        raise ManifestError('Invalid capture list.')
    rows, seen = [], set()
    for row in table.values():
        result = validate_record(row)
        if result['id'] in seen:
            raise ManifestError('Duplicate capture IDs.')
        seen.add(result['id'])
        if result['exported']:
            rows.append(result)
    return rows


SHOT = re.compile(r'^WoWScrnShot_(\d{6}_\d{6})(?:[_-]\d+)?\.(?:jpg|jpeg|png|tga)$', re.I)


def open_image(path):
    with Image.open(path) as source:
        if source.width * source.height > Image.MAX_IMAGE_PIXELS:
            raise ValueError('Image exceeds the 40 megapixel limit.')
        source.load()
        return source.convert('RGBA')


def candidates(record, directory):
    """Conservative filename-time AND dimensions match. Never choose newest."""
    start = datetime.strptime(record['localTime'], '%m%d%y_%H%M%S') - timedelta(seconds=1)
    end = datetime.strptime(record['localCompleted'], '%m%d%y_%H%M%S') + timedelta(seconds=1)
    matches = []
    for path in Path(directory).iterdir():
        match = SHOT.match(path.name)
        if not match or not path.is_file():
            continue
        try:
            timestamp = datetime.strptime(match[1], '%m%d%y_%H%M%S')
            if not start <= timestamp <= end:
                continue
            with Image.open(path) as image:
                if image.size == (record['screenWidth'], record['screenHeight']):
                    image.verify()
                    matches.append(path.resolve())
        except (OSError, ValueError):
            continue
    return sorted(matches)


def match_batch(records, directory):
    matches = {r['id']: candidates(r, directory) for r in records}
    owners = {}
    for identity, paths in matches.items():
        for path in paths:
            owners.setdefault(path, set()).add(identity)
    return {r['id']: (paths[0] if len(paths := matches[r['id']]) == 1 and len(owners[paths[0]]) == 1 and not r.get('review', False) else None,
                     'Review required' if r.get('review', False) else 'Missing screenshot' if not paths else
                     'Choose original' if len(paths) != 1 or len(owners[paths[0]]) != 1 else 'Ready')
            for r in records}


def crop_image(source, record):
    if source.size != (record['screenWidth'], record['screenHeight']):
        raise ValueError('Original dimensions do not match the capture. Choose the full-size WoW screenshot.')
    x, y = record['x'], record['y']
    return source.crop((x, y, x + record['width'], y + record['height']))


@dataclass
class Style:
    padding: int = 32
    radius: int = 16
    border: int = 2
    shadow: int = 12
    background: str = '#201914'
    border_color: str = '#b89655'
    transparent: bool = False

    def validated(self):
        for key, maximum in (('padding', 256), ('radius', 256), ('border', 32), ('shadow', 64)):
            value = getattr(self, key)
            if type(value) is not int or not 0 <= value <= maximum:
                raise ValueError(f'{key.capitalize()} must be between 0 and {maximum}.')
        ImageColor.getrgb(self.background); ImageColor.getrgb(self.border_color)
        return self


PRESETS = {'Stagekeeper': asdict(Style()), 'Clean': asdict(Style(0, 0, 0, 0)),
           'Gallery ivory': asdict(Style(40, 12, 1, 10, '#eee4ce', '#9e8254')),
           'Transparent': asdict(Style(20, 18, 2, 8, transparent=True))}


def render(crop, style):
    s = style.validated()
    border = s.border
    w, h = crop.size
    radius = min(s.radius, w // 2, h // 2)
    panel = Image.new('RGBA', (w + 2 * border, h + 2 * border))
    mask = Image.new('L', (w, h))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w-1, h-1), radius, fill=255)
    from PIL import ImageChops
    inner = crop.convert('RGBA').copy()
    inner.putalpha(ImageChops.multiply(inner.getchannel('A'), mask))
    if border:
        ImageDraw.Draw(panel).rounded_rectangle((0, 0, panel.width-1, panel.height-1), radius + border,
                                                fill=ImageColor.getrgb(s.border_color) + (255,))
    panel.alpha_composite(inner, (border, border))
    # Reserve the shadow's extent even when requested padding is smaller.
    margin = max(s.padding, s.shadow * 3)
    size = (panel.width + margin * 2, panel.height + margin * 2)
    if size[0] * size[1] > 50_000_000:
        raise ValueError('Styled image exceeds the export size limit.')
    output = Image.new('RGBA', size, (0, 0, 0, 0) if s.transparent else ImageColor.getrgb(s.background) + (255,))
    if s.shadow:
        alpha = Image.new('L', size)
        alpha.paste(panel.getchannel('A'), (margin, margin + s.shadow))
        alpha = alpha.filter(ImageFilter.GaussianBlur(s.shadow)).point(lambda v: v * 110 // 255)
        shadow = Image.new('RGBA', size, (0, 0, 0, 0)); shadow.putalpha(alpha)
        output.alpha_composite(shadow)
    output.alpha_composite(panel, (margin, margin))
    return output


def save_image(image, destination, original=None):
    destination = Path(destination)
    if original and destination.resolve() == Path(original).resolve():
        raise ValueError('Choose a different destination; originals are preserved.')
    if destination.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        raise ValueError('Choose PNG or JPEG for export.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() in ('.jpg', '.jpeg'):
        flat = Image.new('RGB', image.size, 'white')
        flat.paste(image, mask=image.getchannel('A'))
        flat.save(destination, quality=95)
    else:
        image.save(destination, format='PNG')


def copy_image(image, owner):
    """CF_DIB ownership passes to Windows only after successful SetClipboardData."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    user = ctypes.WinDLL('user32', use_last_error=True)
    kernel.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t); kernel.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel.GlobalLock.argtypes = (wintypes.HGLOBAL,); kernel.GlobalLock.restype = ctypes.c_void_p
    kernel.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
    kernel.GlobalFree.argtypes = (wintypes.HGLOBAL,); kernel.GlobalFree.restype = wintypes.HGLOBAL
    user.OpenClipboard.argtypes = (wintypes.HWND,); user.OpenClipboard.restype = wintypes.BOOL
    user.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE); user.SetClipboardData.restype = wintypes.HANDLE
    output = io.BytesIO()
    flat = Image.new('RGB', image.size, 'white'); flat.paste(image, mask=image.getchannel('A'))
    flat.save(output, format='BMP'); data = output.getvalue()[14:]
    handle = kernel.GlobalAlloc(0x0002, len(data))
    if not handle:
        raise OSError('Cannot allocate clipboard image.')
    opened = False
    try:
        pointer = kernel.GlobalLock(handle)
        if not pointer:
            raise OSError('Cannot access clipboard memory.')
        ctypes.memmove(pointer, data, len(data)); kernel.GlobalUnlock(handle)
        opened = bool(user.OpenClipboard(owner))
        if not opened:
            raise OSError('Clipboard is busy. Try Copy again.')
        if not user.EmptyClipboard():
            raise OSError('Windows could not open an empty clipboard: ' + str(ctypes.WinError(ctypes.get_last_error())))
        if not user.SetClipboardData(8, handle):
            raise OSError('Windows could not copy the image: ' + str(ctypes.WinError(ctypes.get_last_error())))
        handle = None
    finally:
        if opened:
            user.CloseClipboard()
        if handle:
            kernel.GlobalFree(handle)
