"""Loopback-only synthetic demo supervisor. Ctrl+C stops only its child processes."""
import os, sys, subprocess, time, signal, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
PY=str(ROOT/'.venv/bin/python');env={**os.environ,'PYTHONPATH':str(ROOT/'backend')}
children=[]
def stop_signal(signum,frame): raise KeyboardInterrupt
signal.signal(signal.SIGTERM,stop_signal)
signal.signal(signal.SIGINT,stop_signal)

def wait_url(url):
    for _ in range(80):
        try:
            with urllib.request.urlopen(url,timeout=1) as r:
                if r.status==200:return
        except Exception: time.sleep(.25)
    raise RuntimeError('Readiness failed: '+url)

def start(args,name):
    log=open(ROOT/'.runtime'/f'{name}.log','a')
    p=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    children.append(p);return p
try:
    import socket
    for port in (59000,8000):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1',port))==0: raise RuntimeError(f'Port {port} already occupied; stop your previous demo or choose a clean instance')
    (ROOT/'.runtime/objects').mkdir(parents=True,exist_ok=True)
    subprocess.run(['docker','compose','-f','infra/compose.yml','up','-d','--wait','db'],check=True)
    subprocess.run([str(ROOT/'.venv/bin/alembic'),'upgrade','head'],env=env,check=True)
    start(['node','infra/node_modules/s3rver/bin/s3rver.js','-d','.runtime/objects','-a','127.0.0.1','-p','59000','--silent'],'storage')
    time.sleep(1)
    subprocess.run([PY,'-c','from app.documents.storage import initialize; initialize()'],env=env,check=True)
    start([PY,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000'],'api')
    start([PY,'-m','app.jobs.worker'],'worker')
    wait_url('http://127.0.0.1:8000/api/v1/ready')
    print('BidFit synthetic demo ready. Open http://127.0.0.1:8000 locally. Ctrl+C to stop API, worker, storage.',flush=True)
    while True:
        if any(p.poll() is not None for p in children):raise RuntimeError('Child exited; inspect .runtime/*.log')
        time.sleep(1)
except KeyboardInterrupt: pass
finally:
    for p in children:
        if p.poll() is None: p.terminate()
    for p in children:
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill()
