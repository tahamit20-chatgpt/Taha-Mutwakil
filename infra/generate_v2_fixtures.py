"""Create synthetic Office/ZIP fixtures, never company/customer RFQ data."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape
root=Path(__file__).resolve().parents[1]/'fixtures/synthetic'
pump=(root/'go.txt').read_text()+'npsha: 6 m\nquantity: 2 count\n'
(root/'v2-pump.txt').write_text(pump)
standards=pump+'standard: API 610 edition 12\n'
(root/'v2-standards.txt').write_text(standards)
(root/'v2-mixed.txt').write_text(pump+'\nTag: V-101\nvalve_type: demo-valve\nnominal_size: DN50\npressure_class: demo-class\nmaterial: demo-alloy\nliquid: demo-water\nquantity: 1 count\n\nTag: S-101\nmanufacturer: demo-manufacturer\nequipment_model: demo-model\npart_number: DEMO-001\nquantity: 3 count\n')
def write(name,files):
 with ZipFile(root/name,'w',ZIP_DEFLATED) as z:
  for path,body in files.items():z.writestr(path,body)
relationships='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="{target}"/></Relationships>'
types='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>{overrides}</Types>'
write('v2-standards.docx',{'[Content_Types].xml':types.format(overrides='<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'),'_rels/.rels':relationships.format(target='word/document.xml'),'word/document.xml':'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join('<w:p><w:r><w:t>'+escape(line)+'</w:t></w:r></w:p>' for line in standards.splitlines())+'</w:body></w:document>'})
rows=[]
for index,line in enumerate(standards.splitlines(),1):
 values=line.split(':',1)
 cells=''.join(f'<c r="{letter}{index}" t="inlineStr"><is><t>{escape(value.strip())}</t></is></c>' for letter,value in zip(('A','B'),values))
 rows.append(f'<row r="{index}">{cells}</row>')
write('v2-standards.xlsx',{'[Content_Types].xml':types.format(overrides='<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'),'_rels/.rels':relationships.format(target='xl/workbook.xml'),'xl/workbook.xml':'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Duty" sheetId="1" r:id="rId1"/></sheets></workbook>','xl/_rels/workbook.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>','xl/worksheets/sheet1.xml':'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join(rows)+'</sheetData></worksheet>'})
write('v2-package.zip',{'requirements.txt':pump,'references/standards.docx':(root/'v2-standards.docx').read_bytes()})
print('Created synthetic BidFit 2.0 TXT/DOCX/XLSX/ZIP fixtures.')
