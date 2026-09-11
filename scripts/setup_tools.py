"""Install checksum-pinned portable tools under .tools; nothing is installed globally."""
import hashlib
from pathlib import Path
import shutil
import urllib.request
import zipfile
from common import REPO, read_json, safe_child, save_json

def main():
    lock=read_json(REPO/'tools.lock.json')
    downloads=REPO/'.tools/downloads'
    downloads.mkdir(parents=True,exist_ok=True)
    installed=[]
    for item in lock:
        name=item['name']; filename=item['url'].rsplit('/',1)[-1]
        archive=downloads/(name+'-'+item['version']+'-'+filename)
        if not archive.exists():
            print(f'Downloading {name} {item["version"]}',flush=True)
            with urllib.request.urlopen(item['url'],timeout=60) as source, archive.open('wb') as dest:shutil.copyfileobj(source,dest)
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError(f'SHA256 mismatch: {archive}. Remove this local download and retry.')
        dest=REPO/'.tools'/name
        dest.mkdir(parents=True,exist_ok=True)
        if filename.endswith('.zip'):
            with zipfile.ZipFile(archive) as zipped:
                for member in zipped.infolist():safe_child(dest,member.filename)
                zipped.extractall(dest)
        else:shutil.copy2(archive,dest/filename)
        installed.append({**item,'installed':str(dest.relative_to(REPO))})
        print(f'Installed {name}',flush=True)
    save_json(REPO/'.tools/installed.json',installed)

if __name__=='__main__':main()
