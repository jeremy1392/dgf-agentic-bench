"""Archive the complete recorded run, dataset, and exact benchmark sources.

Maintainer utility; no inference calls. Refuses likely credentials and verifies ZIP CRCs.
Run from the repository root. Original experiment files are not changed.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments/publication_20260923'
DEST = Path(__file__).resolve().parent
RUN = 'experiments/run_20260922_214402_941347'
DATA = 'experiments/preflight_balanced_300_20260922'
PATTERNS = [
    re.compile(rb'sk-or-v1-[A-Za-z0-9_-]{40,}'),
    re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{40,})'),
    re.compile(rb'(?i)bearer\s+[A-Za-z0-9_.-]{35,}'),
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'(?i)["\'](?:api_key|api-key|access_token|client_secret)["\']\s*:\s*["\']([^"\']{20,})["\']'),
]


def scan(data, name):
    for pattern in PATTERNS:
        if pattern.search(data):
            raise RuntimeError('Potential credential; inspect locally before publication: ' + name)


def build(name, files, prefix):
    archive = OUT / name
    inventory = []
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for index, p in enumerate(files):
            data = p.read_bytes()
            rel = p.relative_to(ROOT).as_posix()
            scan(data, rel)
            if p.suffix == '.docx':
                with zipfile.ZipFile(p) as doc:
                    for member in doc.namelist():
                        if member.endswith('.xml'):
                            scan(doc.read(member), rel + '/' + member)
            target = prefix + rel
            z.writestr(target, data)
            inventory.append({'path': target, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            if (index+1) % 5000 == 0:
                print(name, index+1, 'files', flush=True)
        z.writestr('FILE_MANIFEST.json', json.dumps(inventory, indent=2))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.infolist()) == len(files)+1
    result = {'asset': name, 'file_count': len(files), 'uncompressed_bytes': sum(x['bytes'] for x in inventory),
              'archive_bytes': archive.stat().st_size, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
    print(json.dumps(result), flush=True)
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    run = sorted(p for p in (ROOT/RUN).rglob('*') if p.is_file())
    dataset = sorted(p for p in (ROOT/DATA).rglob('*') if p.is_file())
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    excluded = ('paper/', 'docs/', 'assets/readme/', 'research/', '.github/')
    source = {ROOT/p for p in tracked if p and not p.startswith(excluded)
              and p not in {'README.md', 'REPO_MANIFEST.json'} and (ROOT/p).is_file()}
    source.update(ROOT.glob('*.py'))
    source.update(p for p in (ROOT/'tests').rglob('*.py') if p.is_file())
    source = sorted(p for p in source if '__pycache__' not in p.parts)
    for p in source:
        assert p.name != '.env' and p.suffix not in {'.key', '.pem'}
    archives = [build('dgf-bench-300-run.zip', run, ''),
                build('dgf-bench-300-dataset.zip', dataset, ''),
                build('dgf-bench-300-source.zip', source, 'benchmark_source/')]
    manifest = {'release_tag': 'dgf-bench-300-20260923', 'scope': 'Entire final run directory, entire prepared dataset directory, and benchmark source snapshot; no files removed from the two experiment directories.',
                'archives': archives, 'protocol_identity': json.loads((ROOT/RUN/'results/protocol_identity.json').read_text(encoding='utf-8')),
                'notes': ['FILE_MANIFEST.json inside each ZIP provides per-file SHA-256 and byte counts.',
                          'The run archive includes superseded partial reports; use analysis_20260923_final for final statistics.',
                          'Dataset ground truth is published for offline evaluation; agent tools did not expose it during inference.',
                          'Archived absolute paths are historical metadata; the offline reproduction script takes the extraction root explicitly.']}
    (DEST/'release_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    (DEST/'SHA256SUMS.txt').write_text(''.join(f"{a['sha256']}  {a['asset']}\n" for a in archives), encoding='utf-8')


if __name__ == '__main__':
    main()
