"""Package every retained follow-up file, with credential scan and SHA-256 inventory.

No model calls. Benchmark implementation remains the immutable source archive of
the original release. This adds one archive without altering those original assets.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUN=ROOT/'experiments/followup_repetitions_20260923'
OUT=ROOT/'experiments/publication_20260923'


def main():
    spec=importlib.util.spec_from_file_location('release_pack',ROOT/'research/2026-09-dgf-bench/package_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original=ROOT/'experiments/preflight_balanced_300_20260922/dataset'
    checked=0
    for case in (RUN/'dataset').glob('DGF-*'):
        for p in case.rglob('*'):
            if p.is_file():
                source=original/p.relative_to(RUN/'dataset')
                assert p.read_bytes()==source.read_bytes(), str(p)
                checked+=1
    archive=OUT/'dgf-bench-repetitions-20260924.zip';inventory=[]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(p for p in RUN.rglob('*') if p.is_file()):
            rel=path.relative_to(RUN).as_posix();data=path.read_bytes()
            assert path.name!='.env' and path.suffix not in {'.key','.pem'}
            module.scan(data,rel)
            if path.suffix=='.docx':
                with zipfile.ZipFile(path) as doc:
                    for name in doc.namelist():
                        if name.endswith('.xml'):module.scan(doc.read(name),rel+'/'+name)
            z.writestr(rel,data)
            inventory.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        z.writestr('FILE_MANIFEST.json',json.dumps(inventory,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for item in inventory:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
    result={'asset':archive.name,'release_tag':'dgf-bench-300-20260923',
        'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'archive_bytes':archive.stat().st_size,'experiment_files':len(inventory),
        'uncompressed_experiment_bytes':sum(x['bytes'] for x in inventory),
        'byte_verified_dossier_files':checked,
        'scope':'Every retained file in followup_repetitions_20260923, unmodified, including dataset, Word documents, architectures, model traces, final scores, ledgers, retained error checkpoints, configs and summaries. FILE_MANIFEST.json is added at archive root.',
        'source':'Use dgf-bench-300-source.zip from the same release for the frozen benchmark implementation; follow-up orchestration and analysis scripts are in research/2026-09-followup/.',
        'historical_metadata':'Resume overwrites top-level manifests and summary files; these describe the latest invocation, not the full initial execution. Error checkpoints and usage ledgers retain failed attempts.'}
    (HERE/'repetition_archive_manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (HERE/'repetition-SHA256SUMS.txt').write_text(f"{result['sha256']}  {archive.name}\n",encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
