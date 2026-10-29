"""Bounded archive/Office parsing. Never extracts paths to disk or fetches links."""
import io,zipfile,re
from pathlib import PurePosixPath
from defusedxml import ElementTree as ET
MAX_TOTAL=50*1024*1024

def safe_entries(body,max_files=1000):
    if not body.startswith(b'PK'):raise ValueError('ZIP/Office signature does not match')
    result={};total=0
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        if len(z.infolist())>max_files:raise ValueError('Archive entry count limit exceeded')
        seen=set()
        for info in z.infolist():
            name=info.filename;p=PurePosixPath(name)
            if '\\' in name or p.is_absolute() or '..' in p.parts or ':' in name or ((info.external_attr>>16)&0o170000)==0o120000:raise ValueError('Unsafe archive path or link')
            if info.flag_bits&1:raise ValueError('Encrypted archives are unsupported')
            if info.is_dir():continue
            if name.casefold() in seen:raise ValueError('Duplicate archive path')
            seen.add(name.casefold());total+=info.file_size
            if info.file_size>25*1024*1024 or total>MAX_TOTAL or info.file_size/max(info.compress_size,1)>200:raise ValueError('Archive expansion limit exceeded')
            with z.open(info) as stream:data=stream.read(min(info.file_size+1,25*1024*1024+1))
            if len(data)!=info.file_size:raise ValueError('Archive size mismatch')
            result[name]=data
    return result

def office(body,filename):
    files=safe_entries(body);pages=[];locations=[];gaps=[];kinds=[]
    if filename.lower().endswith('.docx'):
        if 'word/document.xml' not in files:raise ValueError('DOCX document part missing')
        root=ET.fromstring(files['word/document.xml']);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        lines=[];loc=[]
        for i,p in enumerate(root.findall('.//w:p',ns),1):
            text=''.join(t.text or '' for t in p.findall('.//w:t',ns))
            if text.strip():
                # Lines within a paragraph keep an exact paragraph+line reference.
                for line in text.splitlines():lines.append(line);loc.append({'paragraph':i})
        if any(n.startswith('word/media/') for n in files):gaps.append('Embedded Word images are not interpreted; review coverage')
        pages=['\n'.join(lines)];locations=[loc];kinds=['paragraphs']
    else:
        if 'xl/workbook.xml' not in files:raise ValueError('XLSX workbook part missing')
        ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        strings=[]
        if 'xl/sharedStrings.xml' in files:
            strings=[''.join(t.text or '' for t in si.findall('.//s:t',ns)) for si in ET.fromstring(files['xl/sharedStrings.xml']).findall('s:si',ns)]
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(files['xl/_rels/workbook.xml.rels'])}
        wb=ET.fromstring(files['xl/workbook.xml']);sheets=wb.findall('s:sheets/s:sheet',ns)
        if len(sheets)>50:raise ValueError('50 worksheet limit')
        cells_total=0
        for sheet in sheets:
            rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=rels[rid];path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            if '..' in PurePosixPath(path).parts or path not in files:raise ValueError('Unsafe or missing worksheet reference')
            lines=[];loc=[]
            for row in ET.fromstring(files[path]).findall('.//s:row',ns):
                values=[];refs=[]
                for cell in row.findall('s:c',ns):
                    cells_total+=1
                    if cells_total>50000:raise ValueError('50,000 cell limit')
                    ref=cell.attrib.get('r','?');kind=cell.attrib.get('t');v=cell.find('s:v',ns);value=v.text if v is not None else ''
                    if kind=='s':value=strings[int(value)] if value else ''
                    elif kind=='inlineStr':value=''.join(t.text or '' for t in cell.findall('.//s:t',ns))
                    if cell.find('s:f',ns) is not None:gaps.append('Formula not independently evaluated: '+sheet.attrib['name']+'!'+ref)
                    if value not in (None,''):values.append(str(value));refs.append(ref)
                if values:
                    text=values[0]+(': '+ ' '.join(values[1:]) if len(values)>1 else '')
                    for line in text.splitlines():lines.append(line);loc.append({'worksheet':sheet.attrib['name'],'cell':':'.join([refs[0],refs[-1]])})
            pages.append('\n'.join(lines));locations.append(loc);kinds.append('worksheet')
        if any(n.startswith(('xl/drawings/','xl/externalLinks/')) for n in files):gaps.append('Workbook drawings/external links are not interpreted')
    return dict(pages=pages,locations=locations,kinds=kinds,gaps=sorted(set(gaps)))
