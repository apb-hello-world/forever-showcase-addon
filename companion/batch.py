"""Sequential batch rendering with original-file protection and unique exports."""
import re
from pathlib import Path
from .model import Style, open_image, crop_image, render, save_image

def export_batch(records, output, mode, screenshot_folder, originals):
    output=Path(output).resolve()
    if output==Path(screenshot_folder).resolve():
        raise ValueError('Choose an export folder outside the WoW Screenshots folder.')
    originals={Path(p).resolve() for p in originals}
    output.mkdir(parents=True,exist_ok=True)
    saved,errors=[],[]
    for row in records:
        name=row.get('name',row['scene'])
        try:
            if not row.get('source'):raise ValueError('Choose an original image first.')
            image=open_image(row['source'])
            if mode!='Original':image=crop_image(image,row)
            if mode=='Styled':image=render(image,Style(**row['style']).validated())
            stem=re.sub(r'[^A-Za-z0-9_.-]+','-',row['addon']+'-'+name).strip('.-')[:120] or 'showcase'
            target=output/(stem+'.png');number=2
            while target.exists() or target.resolve() in originals:
                target=output/f'{stem}-{number}.png';number+=1
            # Exclusive reservation prevents racing another export's filename.
            while True:
                try:
                    with target.open('xb'):pass
                    break
                except FileExistsError:
                    target=output/f'{stem}-{number}.png';number+=1
            try:save_image(image,target,row['source'])
            except Exception:
                target.unlink(missing_ok=True);raise
            saved.append(str(target))
        except Exception as error:errors.append(f'{name}: {error}')
    return saved,errors
