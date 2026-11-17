#!/usr/bin/env python3
"""Explicitly capture one reviewed staged file as a patch/overlay; never edits the desktop."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('component');p.add_argument('file');p.add_argument('--from-file',required=True,type=Path)
p.add_argument('--omarchy-root',type=Path,default=Path('/usr/share/omarchy'))
a=p.parse_args();lock=json.loads((root/'packaging/upstreams.lock.json').read_text())
record=lock['components'][a.component]['files'][a.file];data=a.from_file.read_bytes()
if 'source' in record:
    source=(a.omarchy_root/record['source']).read_bytes()
    if hashlib.sha256(source).hexdigest()!=record['source_sha256']:
        raise SystemExit('Upstream changed: port and review its source pin separately.')
    destination=root/'patches'/lock['components'][a.component]['id']/(a.file+'.patch')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(''.join(difflib.unified_diff(source.decode().splitlines(True),data.decode().splitlines(True),fromfile=a.file,tofile=a.file)))
    record['patch']=str(destination.relative_to(root))
else:
    (root/record['overlay']).write_bytes(data)
record['sha256']=hashlib.sha256(data).hexdigest()
(root/'packaging/upstreams.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
print('Recorded reviewed change. Rebuild, test, and review git diff before committing.')
