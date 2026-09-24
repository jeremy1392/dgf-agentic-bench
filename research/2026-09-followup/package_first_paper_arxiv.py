"""Prepare a minimal manuscript LaTeX upload and external integrity records.

This never submits to arXiv, edits TeX, chooses a license, or compiles a PDF.
Pass the publisher-verified final PDF explicitly. Dependencies are followed from
main.tex; ancillary data and unused files are not included. The inventory remains
outside the source ZIP so arXiv does not mistake it for article content.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ZIP_NAME='The_Last_Human_Gate_arXiv_source.zip'
PDF_NAME='The_Last_Human_Gate.pdf'
DEFAULT_OUTPUT=ROOT/'experiments/publication_20260924_first_paper'
INPUT=re.compile(r'\\(input|include|rowsinput)\s*\{([^{}]+)\}')
GRAPHIC=re.compile(r'\\includegraphics\*?\s*(?:\[[^\]]*\])?\s*\{([^{}]+)\}')
LOCAL_STYLE=re.compile(r'\\(?:usepackage|RequirePackage|documentclass)\s*(?:\[[^\]]*\])?\s*\{([^{}]+)\}')
UNSUPPORTED=re.compile(r'\\(?:bibliography|addbibresource|graphicspath|includepdf|lstinputlisting|verbatiminput|import|subimport|inputminted)\b')
VALID_FILENAME=re.compile(r'^[a-zA-Z0-9_+.,=\-]+$')
FIGURE_SUFFIXES=('.pdf','.png','.jpg','.jpeg')


def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_comments(text):
    lines=[]
    for line in text.splitlines():
        stop=len(line)
        for index,char in enumerate(line):
            if char!='%':continue
            slashes=0;position=index-1
            while position>=0 and line[position]=='\\':slashes+=1;position-=1
            if slashes%2==0:stop=index;break
        lines.append(line[:stop])
    return '\n'.join(lines)


def resolve_literal(source_dir,raw,suffixes):
    raw=raw.strip()
    if any(char in raw for char in ('#','\\','{','}')):
        raise ValueError('Nonliteral TeX dependency needs explicit support: '+raw)
    path=Path(raw)
    if path.is_absolute():raise ValueError('Absolute TeX dependency is not portable: '+raw)
    options=[path] if path.suffix else [path.with_suffix(suffix) for suffix in suffixes]
    for relative in options:
        candidate=source_dir/relative
        if not candidate.resolve().is_relative_to(source_dir):
            raise ValueError('Dependency escapes the manuscript directory: '+raw)
        if not candidate.is_file():continue
        # Windows accepts incorrect case; arXiv's compiler does not. Check each
        # component against its on-disk spelling before storing the ZIP name.
        cursor=source_dir
        for part in relative.parts:
            if part in ('.','..') or not VALID_FILENAME.fullmatch(part):
                raise ValueError('Unsupported arXiv filename component: '+part)
            exact=next((child for child in cursor.iterdir() if child.name==part),None)
            if exact is None:raise ValueError('Dependency case differs from disk: '+raw)
            cursor=exact
        return cursor
    raise FileNotFoundError('Missing TeX dependency: '+raw)


def collect_dependencies(source_dir):
    """Follow the current manuscript's literal input and graphics dependencies.

    Standard TeX packages/classes are supplied by the TeX distribution. Any local
    .sty/.cls file named by the manuscript is also included and inspected. Novel
    import mechanisms fail closed rather than silently producing an incomplete ZIP.
    """
    source_dir=source_dir.resolve()
    entry=source_dir/'main.tex'
    if not entry.is_file():raise FileNotFoundError('Expected main.tex at source-directory root')
    pending=[entry];files=set();edges=[]
    while pending:
        path=pending.pop()
        if path in files:continue
        files.add(path)
        if path.suffix.lower() not in {'.tex','.sty','.cls'}:continue
        text=strip_comments(path.read_text(encoding='utf-8'))
        unknown=UNSUPPORTED.search(text)
        if unknown:raise ValueError(f'Unimplemented dependency command {unknown.group(0)} in {path.name}')
        for command,raw in INPUT.findall(text):
            target=resolve_literal(source_dir,raw,('.tex',))
            edges.append({'from':path.relative_to(source_dir).as_posix(),'command':command,
                'to':target.relative_to(source_dir).as_posix()})
            pending.append(target)
        for raw in GRAPHIC.findall(text):
            target=resolve_literal(source_dir,raw,FIGURE_SUFFIXES)
            if target.suffix.lower() not in FIGURE_SUFFIXES:raise ValueError('Unsupported figure format: '+raw)
            edges.append({'from':path.relative_to(source_dir).as_posix(),'command':'includegraphics',
                'to':target.relative_to(source_dir).as_posix()})
            pending.append(target)
        for names in LOCAL_STYLE.findall(text):
            for name in names.split(','):
                name=name.strip()
                for extension in ('.sty','.cls'):
                    candidate=source_dir/(name+extension)
                    if candidate.is_file():pending.append(resolve_literal(source_dir,name+extension,(extension,)))
    for path in files:
        relative=path.relative_to(source_dir)
        if path.name in {'main.pdf',PDF_NAME} or relative.parts[0] in {'anc','build','reviews','.timeline_review'}:
            raise ValueError('Nonminimal dependency detected; review manuscript references: '+relative.as_posix())
        if path.suffix.lower() not in {'.tex','.sty','.cls',*FIGURE_SUFFIXES}:
            raise ValueError('Unexpected dependency type: '+relative.as_posix())
    return sorted(files,key=lambda p:p.relative_to(source_dir).as_posix()),edges


def load_scanner():
    path=ROOT/'research/2026-09-dgf-bench/package_release.py'
    spec=importlib.util.spec_from_file_location('arxiv_release_scan',path)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    return helper.scan


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manuscript',choices=('first','second'),default='first')
    parser.add_argument('--source-dir',type=Path,help='Directory containing main.tex and dependencies')
    parser.add_argument('--pdf',type=Path,required=True,help='Explicit final PDF, already compiled and visually verified by the publisher')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--manifest-dir',type=Path,default=HERE)
    args=parser.parse_args()
    second=args.manuscript=='second'
    zip_name='DGF_Bench_arXiv_source.zip' if second else ZIP_NAME
    pdf_name='From_Governance_Reviews_to_Task_Substitution.pdf' if second else PDF_NAME
    manifest_name='second_paper_arxiv_manifest.json' if second else 'first_paper_arxiv_manifest.json'
    checksum_name='second-paper-arxiv-SHA256SUMS.txt' if second else 'first-paper-SHA256SUMS.txt'
    title=('The Last Human Gate: Forward Deployed Engineering for Governance Automation'
           if second else 'The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance')
    bibliography='sections/references.tex' if second else 'sections/91_references.tex'
    source=(args.source_dir or ROOT/('paper2' if second else 'paper')).resolve()
    pdf=args.pdf.resolve()
    output=(args.output_dir or (ROOT/'experiments/publication_20260924_second_paper' if second else DEFAULT_OUTPUT)).resolve()
    if not pdf.is_file() or pdf.suffix.lower()!='.pdf':raise FileNotFoundError('A final PDF must be supplied')
    files,edges=collect_dependencies(source)
    scanner=load_scanner()
    inventory=[]
    for path in files:
        rel=path.relative_to(source).as_posix();data=path.read_bytes();scanner(data,rel)
        inventory.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    scanner(pdf.read_bytes(),pdf_name)
    output.mkdir(parents=True,exist_ok=True);archive=output/zip_name
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for path,row in zip(files,inventory):
            # Fixed timestamps avoid timestamp-only differences on repackaging.
            info=zipfile.ZipInfo(row['path'],date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            bundle.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert set(bundle.namelist())=={row['path'] for row in inventory}
        assert 'main.tex' in bundle.namelist()
        for row in inventory:assert hashlib.sha256(bundle.read(row['path'])).hexdigest()==row['sha256']
        assert not any(name.lower().endswith(('.aux','.log','.out','.toc','.md','.json','.zip')) for name in bundle.namelist())
    published_pdf=output/pdf_name
    if pdf!=published_pdf:shutil.copyfile(pdf,published_pdf)
    assert sha256(pdf)==sha256(published_pdf)
    assets=[{'asset':zip_name,'bytes':archive.stat().st_size,'sha256':sha256(archive)},
            {'asset':pdf_name,'bytes':published_pdf.stat().st_size,'sha256':sha256(published_pdf)}]
    manifest={'status':'PREPARED_FOR_AUTHOR_REVIEW_NOT_SUBMITTED','title':title,
        'entry_point':'main.tex','compiler':'PDFLaTeX','bibliography':f'Inline thebibliography in {bibliography}; no BibTeX step required',
        'source_directory':str(source),'supplied_final_pdf':str(pdf),'assets':assets,
        'source_file_count':len(inventory),'source_inventory':inventory,'dependency_edges':edges,
        'source_archive_scope':'Only main.tex, recursively used TeX/table fragments, used figures and any local TeX styles. No compiled article PDF or inventory is injected into the source ZIP.',
        'excluded':'Unused documents, README/license notices, ancillary raw data, review notes and build outputs. Research artifacts remain available from the public repository/release.',
        'checks':{'secret_scan':'PASS','zip_crc':'PASS','file_hashes':'PASS','case_sensitive_paths':'PASS'},
        'compilation_note':'This packaging script does not compile. The publisher must extract and compile this ZIP independently, inspect the rendered result, and ensure the supplied PDF corresponds to the final source.',
        'license_choice':'Reserved to the author during arXiv submission; preparing this package does not select or change a license.',
        'submitted_to_arxiv':False,'script_sha256':sha256(Path(__file__))}
    args.manifest_dir.mkdir(parents=True,exist_ok=True)
    for path in (args.manifest_dir/manifest_name,output/manifest_name):
        path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    checksum=''.join(f"{asset['sha256']}  {asset['asset']}\n" for asset in assets)
    for path in (args.manifest_dir/checksum_name,output/checksum_name):
        path.write_text(checksum,encoding='utf-8')
    print(json.dumps({'status':manifest['status'],'source_file_count':len(inventory),'assets':assets},indent=2))


if __name__=='__main__':main()
