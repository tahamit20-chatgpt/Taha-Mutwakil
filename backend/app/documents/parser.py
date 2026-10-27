"""Isolated parser entrypoint: finite CPU/address space, no external link fetching."""
import sys, json, resource
resource.setrlimit(resource.RLIMIT_CPU,(20,20))
resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
from app.extraction.service import parse
try:
    print(json.dumps({'pages':parse(sys.stdin.buffer.read(25*1024*1024+1),sys.argv[1])}))
except Exception:
    # No document bodies or parser internals escape through telemetry.
    print(json.dumps({'error':'Invalid/unsupported PDF or TXT; encrypted, malformed, and oversized files are unsupported'}))
    raise SystemExit(2)
