"""Opt-in updates from public GitHub release assets. No authentication required."""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .version import VERSION, REPOSITORY

API=f'https://api.github.com/repos/{REPOSITORY}/releases?per_page=100'
PREFIX=f'https://github.com/{REPOSITORY}/releases/download/'
LIMIT=250*1024*1024

def version(value):
    if not re.fullmatch(r'\d+\.\d+\.\d+',value):raise ValueError('Invalid release version.')
    return tuple(map(int,value.split('.')))

def read_url(url,limit):
    request=Request(url,headers={'User-Agent':'ForeverShowcaseCompanion/'+VERSION,'Accept':'application/vnd.github+json' if url.startswith('https://api.github.com/') else 'application/octet-stream'})
    with urlopen(request,timeout=30) as response:
        data=response.read(limit+1)
    if len(data)>limit:raise ValueError('Update response exceeded its size limit.')
    return data

def select_release(releases,current=VERSION):
    candidates=[]
    for release in releases:
        tag=release.get('tag_name','')
        if release.get('draft') or release.get('prerelease') or not re.fullmatch(r'companion-v\d+\.\d+\.\d+',tag):continue
        number=tag.removeprefix('companion-v')
        if version(number)<=version(current):continue
        name=f'ForeverShowcaseCompanion-Setup-{number}.exe'
        assets={a.get('name'):a for a in release.get('assets',[])}
        if name not in assets or name+'.sha256' not in assets:continue
        urls=[assets[n].get('browser_download_url','') for n in (name,name+'.sha256')]
        if any(url!=PREFIX+tag+'/'+n for url,n in zip(urls,(name,name+'.sha256'))):continue
        candidates.append(dict(version=number,name=name,url=urls[0],checksum_url=urls[1]))
    return max(candidates,key=lambda r:version(r['version']),default=None)

def check_update():
    try:payload=json.loads(read_url(API,4*1024*1024))
    except HTTPError as error:
        if error.code==404:return None
        if error.code in (403,429):raise ValueError('GitHub update checks are temporarily rate limited. Try again later.') from error
        raise
    if not isinstance(payload,list):raise ValueError('Invalid GitHub release response.')
    return select_release(payload)

def download_update(release):
    # Revalidate the exact expected release URL before downloading executable code.
    number=release['version'];version(number)
    name=f'ForeverShowcaseCompanion-Setup-{number}.exe'
    base=PREFIX+'companion-v'+number+'/'
    if release['url']!=base+name or release['checksum_url']!=base+name+'.sha256':raise ValueError('Unexpected update source.')
    checksum=read_url(release['checksum_url'],4096).decode('ascii').strip().split()[0]
    if not re.fullmatch(r'[a-fA-F0-9]{64}',checksum):raise ValueError('Invalid installer checksum.')
    folder=Path(tempfile.mkdtemp(prefix='ForeverShowcase-update-'))
    target=folder/name
    try:
        digest=hashlib.sha256();total=0
        with urlopen(Request(release['url'],headers={'User-Agent':'ForeverShowcaseCompanion/'+VERSION}),timeout=30) as response,target.open('wb') as output:
            while chunk:=response.read(1024*1024):
                total+=len(chunk)
                if total>LIMIT:raise ValueError('Installer exceeds the download limit.')
                digest.update(chunk);output.write(chunk)
        if digest.hexdigest().lower()!=checksum.lower():raise ValueError('Installer checksum mismatch; update was not run.')
        return target
    except Exception:
        target.unlink(missing_ok=True);folder.rmdir();raise

def launch_installer(path):
    if not getattr(sys,'frozen',False):raise ValueError('Install updates from the packaged companion.')
    # The installer resolves its existing per-user install location using its AppId.
    return subprocess.Popen([str(path),'/CURRENTUSER','/NORESTART'],close_fds=True)
