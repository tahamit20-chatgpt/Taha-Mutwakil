"""Record installed Python and locked npm license metadata for review (not legal advice)."""
import json, importlib.metadata as m
from pathlib import Path
rows=['# Dependency license inventory','','Generated from installed package metadata and package locks. Review notices before redistribution.','', '| Package | Version | License metadata |','|---|---|---|']
for dist in sorted(m.distributions(),key=lambda d:d.metadata['Name'].lower()):
    md=dist.metadata
    license=md.get('License-Expression') or md.get('License') or '; '.join(c.split(' :: ')[-1] for c in md.get_all('Classifier',[]) if c.startswith('License ::')) or 'Not declared — review upstream'
    license=license.splitlines()[0][:200].replace('|',' / ')
    rows.append(f"| Python: {md['Name']} | {dist.version} | {license} |")
for name in ('frontend','infra'):
    data=json.loads(Path(name,'package-lock.json').read_text())
    for path,entry in sorted(data['packages'].items()):
        if path: rows.append(f"| npm ({name}): {path.removeprefix('node_modules/')} | {entry.get('version','')} | {entry.get('license','Not declared — review upstream')} |")
rows+=['','PostgreSQL container: PostgreSQL License. System Chromium: BSD and bundled third-party notices. Synthetic fixtures are generated for this prototype; uploaded specifications remain owner-provided material.']
Path('docs/LICENSES.md').write_text('\n'.join(rows)+'\n')
