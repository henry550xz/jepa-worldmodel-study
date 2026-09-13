"""Export only committed, noncredential regular files for disposable workers."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path, PurePosixPath
from study.manifests import provenance


def export(repo, destination):
    repo, destination = Path(repo), Path(destination)
    info = provenance(repo)
    destination.mkdir(parents=True, exist_ok=False)
    entries = subprocess.check_output(['git','-C',str(repo),'ls-tree','-rz','--full-tree','HEAD']).split(b'\0')
    hashes = {}
    for entry in entries:
        if not entry: continue
        header, rawname = entry.split(b'\t',1)
        mode, kind, sha = header.decode().split()
        name = rawname.decode()
        parts = PurePosixPath(name).parts
        if kind != 'blob' or mode not in ('100644','100755'):
            raise ValueError(f'unsupported snapshot entry: {name}')
        if any(x in ('.git','.ssh','.config') or x.startswith('.env') for x in parts) or name.endswith(('.pem','.key')):
            raise ValueError(f'credential-like tracked path refused: {name}')
        content = subprocess.check_output(['git','-C',str(repo),'cat-file','blob',sha])
        if any((b'-----BEGIN '+kind+b'PRIVATE KEY-----') in content
               for kind in (b'', b'OPENSSH ', b'RSA ', b'EC ', b'DSA ')):
            raise ValueError(f'private key marker refused: {name}')
        target = destination/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o755 if mode=='100755' else 0o644)
        hashes[name] = hashlib.sha256(content).hexdigest()
    (destination/'SNAPSHOT.json').write_text(json.dumps(dict(info, files=hashes), indent=2)+'\n')
    return info

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('destination'); a=p.parse_args()
    export(Path(__file__).resolve().parents[1], a.destination)
