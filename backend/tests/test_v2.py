import io,zipfile,json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.jobs.worker import run_once
from app.documents.office import safe_entries
from app.extraction.service import parse_rich
from conftest import login
from test_workflow import load,upload,accept,evaluate,project
ROOT=Path(__file__).resolve().parents[2]

def create(c,product='Pump / Pump Set',equipment=None):
    body=dict(name='BidFit 2.0 synthetic RFQ',classification=dict(product_category=product,market_area='Water',application='Water Supply',customer='Synthetic customer',rfq_reference='SYN-2026'),equipment=equipment or [dict(tag='P-101',product_category=product)])
    r=c.post('/api/v1/rfqs',json=body);assert r.status_code==201,r.text
    return r.json()['id']

def ready(c,p,text=None):
    s=(ROOT/'fixtures/synthetic/go.txt').read_text()+'npsha: 6 m\n'
    r=upload(c,p,text=(text or s).encode());assert r.status_code==202,r.text
    assert run_once();accept(c,p)

def acknowledge(c,p):
    s=c.get(f'/api/v1/projects/{p}/summary').json()
    r=c.post(f'/api/v1/projects/{p}/summary/reviews',json=dict(expected_version=load(c,p)['lock_version'],summary_hash=s['summary_hash'],reason='Reviewed synthetic summary including all explicit gaps'))
    assert r.status_code==200,r.text
    return s

def process(c,p):
    r=c.post(f'/api/v1/projects/{p}/process-rfq',json={'expected_version':load(c,p)['lock_version']});assert r.status_code==201,r.text;return r.json()

def custom_rule(c,**extra):
    body=dict(criterion_id='CUSTOM1',name='Synthetic head test',field='head',product_category='Pump / Pump Set',operator='range',minimum=1,maximum=100,units='m',source_reference='Synthetic test policy v1 only',capability_reference='Fictional demo boundary only',effective_date='2020-01-01',**extra)
    r=c.post('/api/v1/registry/rules',json=body);assert r.status_code==201,r.text;return r.json()

def test_classification_config_six_areas_and_mixed_validation(client):
    m=client.get('/api/v1/configuration').json()
    assert list(m['markets'])==['Water','Energy','Mining','General Industry','Building Services','Petrochemicals / Chemicals']
    p=create(client);d=load(client,p);assert d['classification']['application']=='Water Supply' and d['workflow_version']=='2.0' and d['name'].endswith(' revised')
    assert client.post('/api/v1/rfqs',json=dict(name='Invalid',classification=dict(product_category='Valve',market_area='Water',application='Fire Protection',customer='Synthetic'),equipment=[dict(tag='V1',product_category='Valve')])).status_code==422
    assert client.post('/api/v1/rfqs',json=dict(name='Wrong category',classification=dict(product_category='Valve',market_area='Water',application='Water Supply',customer='Synthetic'),equipment=[dict(tag='P1',product_category='Pump / Pump Set')])).status_code==422
    login(client,'bob');assert client.put('/api/v1/configuration',json=dict(expected_version=m['lock_version'],customers=m['customers'],markets=m['markets'])).status_code==403

def test_summary_review_is_required_and_new_upload_invalidates_it(client):
    p=create(client);ready(client,p)
    r=client.post(f'/api/v1/projects/{p}/evaluations',json={'expected_version':load(client,p)['lock_version']});assert r.status_code==409
    acknowledge(client,p);r=process(client,p);assert r['snapshot']['outcome']=='GO'
    before={fmt:client.get('/api/v1/evaluations/'+r['id']+'/exports?format='+fmt).content for fmt in ('json','html','csv')}
    original=load(client,p)['document'][0]
    revision=client.post(f'/api/v1/projects/{p}/documents',files={'file':('revision.txt',b'Tag: P-101\nhead: 60 m')},data={'revision_of':original['id']},headers={'Idempotency-Key':'revision-2'})
    assert revision.status_code==202;run_once();accept(client,p)
    docs=load(client,p)['document'];assert len(docs)==2 and docs[1]['version']==2
    assert not client.get(f'/api/v1/projects/{p}/summary').json()['reviewed']
    acknowledge(client,p);new=process(client,p);assert new['snapshot']['outcome']=='INSUFFICIENT DATA'
    assert any(f['compliance_status']=='CONFLICTING INFORMATION' for f in new['snapshot']['compliance_matrix'])
    for fmt,value in before.items():assert client.get('/api/v1/evaluations/'+r['id']+'/exports?format='+fmt).content==value

def test_missing_npsha_and_unavailable_standard_never_pass(client):
    p=create(client);ready(client,p,(ROOT/'fixtures/synthetic/go.txt').read_text()+'standard: API 610 edition 12\n')
    s=acknowledge(client,p);assert any(m['field']=='npsha' for m in s['missing'])
    st=client.get(f'/api/v1/projects/{p}/standards').json();assert st['explicit'][0]['code']=='API 610' and st['explicit'][0]['edition']=='12'
    r=process(client,p)['snapshot'];assert r['outcome']=='INSUFFICIENT DATA'
    rows=r['compliance_matrix'];assert any(x['field']=='npsha' and x['compliance_status']=='MISSING INFORMATION' for x in rows)
    assert any(x.get('standard_reference')=='API 610' and x['result']=='UNKNOWN' for x in rows)
    assert st['explicit'][0]['source']['line_start']

def test_standard_suggestions_do_not_become_mandatory_and_editions_conflict(client):
    p=create(client);ready(client,p);acknowledge(client,p)
    assert process(client,p)['snapshot']['outcome']=='GO'
    upload(client,p,text=b'Tag: P-101\nstandard: API 610 edition 12\nstandard: API 610 edition 11',key='standards');run_once();accept(client,p);acknowledge(client,p)
    r=process(client,p)['snapshot'];assert r['outcome']=='INSUFFICIENT DATA'
    assert any(x['compliance_status']=='CONFLICTING INFORMATION' and x.get('standard_reference')=='API 610' for x in r['compliance_matrix'])

def test_draft_rules_approval_permissions_versioning_and_staleness(client):
    p=create(client);ready(client,p);acknowledge(client,p)
    r=custom_rule(client)
    run=process(client,p);assert run['snapshot']['outcome']=='INSUFFICIENT DATA'
    login(client,'bob');assert client.post('/api/v1/registry/rules/'+r['id']+'/approve',json={'reason':'Synthetic engineering test'}).status_code==403
    login(client,'alice');a=client.post('/api/v1/registry/rules/'+r['id']+'/approve',json={'reason':'Approved for isolated synthetic training only'});assert a.status_code==200,a.text
    assert client.post('/api/v1/evaluations/'+run['id']+'/adjudications',json=dict(disposition='ACKNOWLEDGED',reason='Review outcome',evidence='Synthetic source')).status_code==409
    assert process(client,p)['snapshot']['outcome']=='GO'
    assert client.post('/api/v1/registry/rules/'+r['id']+'/approve',json={'reason':'Second approval'}).status_code==409
    assert custom_rule(client)['version']==2

def test_mixed_package_never_uses_pump_rules_for_valves_or_parts(client):
    eq=[dict(tag='P-101',product_category='Pump / Pump Set'),dict(tag='V-101',product_category='Valve'),dict(tag='S-101',product_category='Spare Parts')]
    p=create(client,'Mixed Package',eq);ready(client,p);acknowledge(client,p)
    r=process(client,p)['snapshot'];assert r['outcome']=='INSUFFICIENT DATA'
    assert len(r['tags'])==3 and r['tags'][0]['outcome']=='GO'
    for tag in r['tags'][1:]:assert not any(f['criterion_id']=='D01' for f in tag['results'])

def test_v2_isolation_and_studios_and_draft_export(client):
    p=create(client);ready(client,p);acknowledge(client,p);run=process(client,p)
    family=client.post('/api/v1/library/product-families',json=dict(name='Synthetic unvalidated family',product_category='Pump / Pump Set',source_reference='Synthetic training datasheet',source_revision='A')).json()
    candidate=client.post(f'/api/v1/projects/{p}/selection/candidates',json=dict(expected_version=load(client,p)['lock_version'],tag='P-101',family_id=family['id'],evidence_reference='Synthetic manual reference')).json()
    assert candidate['status']=='UNVERIFIED'
    studios=client.get(f'/api/v1/projects/{p}/studios').json()
    q=client.post(f'/api/v1/projects/{p}/quotations',json=dict(expected_version=load(client,p)['lock_version'],evaluation_id=run['id'],template_id=studios['templates'][0]['id']));assert q.status_code==201,q.text
    assert q.json()['snapshot']['prices'] is None
    qid=q.json()['id'];assert 'NOT FOR SUBMISSION' in client.get('/api/v1/quotations/'+qid+'/export').text
    login(client,'outsider')
    for route in ['/summary','/standards','/studios']:
        assert client.get('/api/v1/projects/'+p+route).status_code==404
    assert client.get('/api/v1/knowledge').json()==[]
    assert client.get('/api/v1/quotations/'+qid+'/export').status_code==404
    assert client.post('/api/v1/selection/candidates/'+candidate['id']+'/reviews',json=dict(disposition='REFERENCE_REVIEWED',reason='Attempt unauthorized review')).status_code==404

def test_conservative_override_cannot_unlock_unknown_or_hard_stop(client):
    p=create(client);ready(client,p,(ROOT/'fixtures/synthetic/no-go.txt').read_text());acknowledge(client,p);r=process(client,p)
    assert r['snapshot']['outcome']=='NO-GO'
    assert client.post('/api/v1/evaluations/'+r['id']+'/adjudications',json=dict(disposition='OVERRIDE',requested_outcome='GO',reason='Commercial interest',evidence='No valid new evidence')).status_code==422
    assert client.post('/api/v1/evaluations/'+r['id']+'/adjudications',json=dict(disposition='CLARIFICATION_REQUESTED',reason='Request updated requirement',evidence='Synthetic source page 1')).status_code==200

def zipped(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for name,body in files.items():z.writestr(name,body)
    return b.getvalue()

def test_safe_zip_paths_and_partial_coverage(client):
    for name in ['../escape.txt','/absolute.txt','C:/drive.txt','a\\b.txt']:
        with pytest.raises(ValueError,match='Unsafe'):safe_entries(zipped({name:b'x'}))
    with pytest.raises(ValueError,match='expansion'):safe_entries(zipped({'bomb.txt':b'a'*1000000}))
    p=create(client)
    r=upload(client,p,text=zipped({'go.txt':(ROOT/'fixtures/synthetic/go.txt').read_bytes(),'drawing.dwg':b'unsupported relevant drawing'}),filename='bundle.zip');assert r.status_code==202
    assert run_once();assert run_once();accept(client,p)
    docs=load(client,p)['document'];assert len(docs)==3 and any(d['state']=='EXPANDED' for d in docs)
    acknowledge(client,p);assert process(client,p)['snapshot']['outcome']=='INSUFFICIENT DATA'
    assert not run_once()

def test_office_exact_sources(client):
    docx=zipped({'word/document.xml':b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Tag: P-101</w:t></w:r></w:p><w:p><w:r><w:t>head: 50 m</w:t></w:r></w:p></w:body></w:document>'})
    rich=parse_rich(docx,'synthetic.docx');assert rich['locations'][0][1]['paragraph']==2
    p=create(client);upload(client,p,text=docx,filename='synthetic.docx');run_once()
    f=load(client,p)['fact'][0];assert f['source']['paragraph']==2 and f['source']['page'] is None
    xlsx=zipped({'xl/workbook.xml':b'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Duty" r:id="r1"/></sheets></workbook>','xl/_rels/workbook.xml.rels':b'<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/></Relationships>','xl/worksheets/sheet1.xml':b'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row><c r="A1" t="inlineStr"><is><t>Tag</t></is></c><c r="B1" t="inlineStr"><is><t>P-101</t></is></c></row><row><c r="A2" t="inlineStr"><is><t>head</t></is></c><c r="B2" t="inlineStr"><is><t>50 m</t></is></c></row></sheetData></worksheet>'})
    upload(client,p,text=xlsx,filename='synthetic.xlsx',key='xlsx');run_once()
    f=load(client,p)['fact'][-1];assert f['source']['worksheet']=='Duty' and f['source']['cell']=='A2:B2'

def test_legacy_rfq_can_be_adopted_without_losing_original_facts(client):
    p=project(client);upload(client,p);run_once();accept(client,p);old=evaluate(client,p)
    d=load(client,p)
    body=dict(name=d['name']+' revised',classification=dict(product_category='Pump / Pump Set',market_area='Water',application='Water Supply',customer='Synthetic'),equipment=[dict(tag='P-101',product_category='Pump / Pump Set')],expected_version=d['lock_version'])
    r=client.put(f'/api/v1/projects/{p}/classification',json=body);assert r.status_code==200,r.text
    d=load(client,p);assert len(d['fact'])==10 and d['evaluation'][0]['id']==old['id'] and d['workflow_version']=='2.0' and d['name'].endswith(' revised')

def test_logo_file_preserved_exactly_and_permissions(client,tmp_path,monkeypatch):
    import app.workflow.routes as routes
    from PIL import Image
    monkeypatch.setattr(routes,'ROOT',tmp_path);(tmp_path/'.runtime').mkdir()
    body=io.BytesIO();Image.new('RGB',(2,2),'white').save(body,'PNG');data=body.getvalue()
    assert client.post('/api/v1/branding/logo',files={'file':('original.png',data)}).status_code==200
    assert client.get('/api/v1/branding/logo').content==data
    login(client,'bob');assert client.post('/api/v1/branding/logo',files={'file':('original.png',data)}).status_code==403

def test_rule_semantics_and_pressure_basis(client):
    from app.workflow.models import RuleInput
    from app.extraction.service import normalize
    from pydantic import ValidationError
    assert normalize('part_number','  ','')[0] is None
    payload=dict(criterion_id='PRESSURE1',name='Synthetic pressure boundary',field='pressure',product_category='Pump / Pump Set',operator='range',maximum=200000,units='Pa',source_reference='Synthetic gauge pressure policy',effective_date='2020-01-01')
    with pytest.raises(ValidationError):RuleInput.model_validate(payload)
    payload['pressure_basis']='gauge'
    p=create(client);ready(client,p,(ROOT/'fixtures/synthetic/go.txt').read_text()+'npsha: 6 m\npressure: 1 bar\n')
    r=client.post('/api/v1/registry/rules',json=payload);assert r.status_code==201
    assert client.post('/api/v1/registry/rules/'+r.json()['id']+'/approve',json={'reason':'Synthetic test basis validation'}).status_code==200
    acknowledge(client,p);r=process(client,p)['snapshot'];assert r['outcome']=='INSUFFICIENT DATA'
    assert any(f['criterion_id']=='PRESSURE1' and f['compliance_status']=='MISSING INFORMATION' for f in r['compliance_matrix'])

def test_register_quantity_conflict_and_price_gates(client):
    p=create(client,equipment=[dict(tag='P-101',product_category='Pump / Pump Set',quantity=1)])
    ready(client,p,(ROOT/'fixtures/synthetic/v2-pump.txt').read_text());s=acknowledge(client,p)
    assert any(c['field']=='quantity' for c in s['conflicts'])
    assert process(client,p)['snapshot']['outcome']=='INSUFFICIENT DATA'
    payload=dict(expected_version=load(client,p)['lock_version'],tag='P-101',price_kind='Approved Selling Price',amount=100,currency='SAR',valid_until='2030-01-01',source_reference='Synthetic price reference',source_revision='A')
    assert client.post(f'/api/v1/projects/{p}/pricing/references',json=payload).status_code==422
    payload['price_kind']='Target Selling Price'
    r=client.post(f'/api/v1/projects/{p}/pricing/references',json=payload)
    assert r.status_code==201 and r.json()['approval_status']=='DRAFT_UNAPPROVED'
