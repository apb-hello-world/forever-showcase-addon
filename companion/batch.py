"""Sequential batch rendering with original-file protection and unique exports."""
import re
import unicodedata
from pathlib import Path
from .model import Style, open_image, crop_image, render, save_image
from .exporting import ExportOptions, resize_export

def addon_directory(output, record):
    root=Path(output).expanduser().resolve()
    name=str(record.get('addonTitle') or record.get('addon') or 'Unknown addon')
    name=re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',name)
    name=unicodedata.normalize('NFC',name)
    name=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',name).strip(' .')[:100].rstrip(' .') or 'Unknown addon'
    if name.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:name='_'+name
    destination=(root/name).resolve()
    if destination.parent!=root:raise ValueError('The addon folder must stay inside the selected save location.')
    return destination


def export_batch(records, output, mode, screenshot_folder, originals, options=None):
    options=(options or ExportOptions()).validated()
    output=Path(output).expanduser().resolve()
    if output==Path(screenshot_folder).resolve():
        raise ValueError('Choose an export folder outside the WoW Screenshots folder.')
    originals={Path(p).resolve() for p in originals}
    output.mkdir(parents=True,exist_ok=True)
    saved,errors=[],[]
    for row in records:
        name=row.get('name',row['scene'])
        try:
            if not row.get('source'):raise ValueError('Choose an original image first.')
            destination=addon_directory(output,row)
            if destination==Path(screenshot_folder).resolve():raise ValueError('Choose a save location outside the WoW Screenshots folder.')
            destination.mkdir(parents=True,exist_ok=True)
            image=open_image(row['source'])
            if mode!='Original':image=crop_image(image,row)
            if mode=='Styled':image=render(image,Style(**row['style']).validated())
            image=resize_export(image,options)
            stem=re.sub(r'[^A-Za-z0-9_.-]+','-',row['addon']+'-'+name).strip('.-')[:120] or 'showcase'
            if options.resize:stem+=f'-{image.width}x{image.height}'
            extension=options.extension
            target=destination/(stem+extension);number=2
            while target.exists() or target.resolve() in originals:
                target=destination/f'{stem}-{number}{extension}';number+=1
            # Exclusive reservation prevents racing another export's filename.
            while True:
                try:
                    with target.open('xb'):pass
                    break
                except FileExistsError:
                    target=destination/f'{stem}-{number}{extension}';number+=1
            try:save_image(image,target,row['source'],quality=options.quality)
            except Exception:
                target.unlink(missing_ok=True);raise
            saved.append(str(target))
        except Exception as error:errors.append(f'{name}: {error}')
    return saved,errors
