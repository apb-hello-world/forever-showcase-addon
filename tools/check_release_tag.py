import os
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from companion.version import VERSION
tag=os.environ['RELEASE_TAG']
addon=re.search(r'^## Version: (.+)$',(ROOT/'ForeverShowcase/ForeverShowcase.toc').read_text(),re.M).group(1).strip()
expected='companion-v'+VERSION if tag.startswith('companion-v') else 'addon-v'+addon
if tag!=expected:raise SystemExit(f'Tag {tag} does not match {expected}')
