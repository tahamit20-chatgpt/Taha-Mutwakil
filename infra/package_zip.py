"""Create a portable source/built-UI ZIP without machine state or credentials."""
import hashlib,json,stat,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'artifacts/BidFit-MVP.zip'
OUT.parent.mkdir(parents=True,exist_ok=True)
exclude={'.git','.runtime','.venv','.pytest_cache','__pycache__','node_modules','test-results','playwright-report','artifacts','downloads'}
allowed_roots={'backend','frontend','infra','docs','fixtures','migrations','.github'}
allowed_files={'.gitattributes','README.md','START_HERE.md','BIDFIT_2_0_WINDOWS.txt','alembic.ini','.gitignore','.dockerignore','.env.example','compose.local.yml','start-local.sh','start-local.bat','START_BIDFIT_WINDOWS.bat','STOP_BIDFIT_WINDOWS.bat','WINDOWS-START-HERE.txt','WINDOWS_START_HERE.html','WINDOWS_VERIFICATION.txt'}
files=[]
for path in sorted(ROOT.rglob('*')):
    rel=path.relative_to(ROOT)
    if any(part in exclude for part in rel.parts):continue
    if path.is_symlink():raise RuntimeError('Refusing symlink '+str(rel))
    if not path.is_file():continue
    if path.suffix=='.pyc' or path.name=='.env' or path.name.startswith('.env.') and path.name!='.env.example':continue
    if rel.parts[0] not in allowed_roots and str(rel) not in allowed_files:continue
    files.append(path)
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    def write(name,body,executable=False):
        info=zipfile.ZipInfo('BidFit-MVP/'+name)
        info.create_system=3;info.external_attr=((stat.S_IFREG|(0o755 if executable else 0o644))<<16)
        info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,body)
    for path in files:
        rel=str(path.relative_to(ROOT));body=path.read_bytes()
        # Native Windows launcher: CRLF, independent of checkout autocrlf.
        if rel.endswith('.bat'):body=body.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
        manifest[rel]=hashlib.sha256(body).hexdigest()
        write(rel,body,path.suffix in ('.sh','.command'))
    write('PACKAGE_MANIFEST.json',json.dumps({'format':1,'files_sha256':manifest,'notes':'Pinned dependencies fetched at first build; no private data or paid API credentials included'},indent=2).encode())
with zipfile.ZipFile(OUT) as archive:
    assert archive.testzip() is None
    names=archive.namelist()
    for required in ['START_HERE.md','.env.example','compose.local.yml','frontend/dist/index.html','backend/requirements.lock','frontend/package-lock.json','infra/package-lock.json','fixtures/synthetic/go.pdf','start-local.bat','start-local.sh']:
        assert 'BidFit-MVP/'+required in names,required
    for name in names:
        assert not any(p in exclude for p in Path(name).parts),name
    for name,sha in manifest.items():assert hashlib.sha256(archive.read('BidFit-MVP/'+name)).hexdigest()==sha
sha=hashlib.sha256(OUT.read_bytes()).hexdigest()
OUT.with_suffix('.zip.sha256').write_text(sha+'  '+OUT.name+'\n')
print(json.dumps({'zip':str(OUT),'files':len(manifest)+1,'bytes':OUT.stat().st_size,'sha256':sha},indent=2))
