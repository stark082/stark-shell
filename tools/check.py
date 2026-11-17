#!/usr/bin/env python3
"""Offline release consistency checks; does not contact a running desktop."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    files = [p for p in ROOT.rglob('*.json') if '.build' not in p.parts and '.git' not in p.parts]
    for path in files:
        json.loads(path.read_text())
    lock = json.loads((ROOT/'packaging/upstreams.lock.json').read_text())
    ids = set()
    for name, component in lock['components'].items():
        assert component['id'] not in ids, name
        ids.add(component['id'])
        manifest = json.loads((ROOT/component['files']['manifest.json']['overlay']).read_text())
        assert manifest['schemaVersion'] == 1 and manifest['id'] == component['id']
        assert manifest['version'] == lock['release'], name
        assert not manifest['id'].startswith('omarchy.')
        for entry in manifest['entryPoints'].values():
            assert entry in component['files'], (name, entry)
        for rel, record in component['files'].items():
            assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
            if 'overlay' in record:
                content = (ROOT/record['overlay']).read_bytes()
                assert hashlib.sha256(content).hexdigest() == record['sha256'], rel
            if 'patch' in record:
                assert (ROOT/record['patch']).is_file()
    fonts = json.loads((ROOT/'packaging/fonts.lock.json').read_text())
    for name, expected in fonts['files'].items():
        assert hashlib.sha256((ROOT/'fonts/ShantellSans'/name).read_bytes()).hexdigest() == expected
    for path in ROOT.glob('*.sh'):
        subprocess.run(['bash','-n',path],check=True)
    assert not any('/home/stark' in p.read_text(errors='ignore') for p in (ROOT/'overlays').rglob('*.qml'))
    print(f'Validated {len(files)} JSON files, {len(ids)} plugin blueprints, font hashes, and Bash syntax.')

if __name__ == '__main__': main()
