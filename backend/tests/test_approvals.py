import json
from datetime import date,timedelta
from pathlib import Path
import pytest
from conftest import login
from test_v2 import ready,acknowledge,process
from test_workflow import load
from app.db import Session,Record
from app.rules.engine import digest
from app.approvals.service import current_status

ROOT=Path(__file__).resolve().parents[2]

def catalog(c):
    r=c.get('/api/v1/approvals/registry');assert r.status_code==200,r.text;return r.json()

def rfq(c,customer='Saudi Aramco',equipment=None):
    eq=equipment or [dict(tag='P-101',product_category='Pump / Pump Set')]
    product='Mixed Package' if len({x['product_category'] for x in eq})>1 else eq[0]['product_category']
    r=c.post('/api/v1/rfqs',json=dict(name='Synthetic customer approval test',classification=dict(product_category=product,market_area='Water',application='Water Supply',customer=customer),equipment=eq))
    assert r.status_code==201,r.text;return r.json()['id']

def assign(c,p,series='RPH',tag='P-101',**extra):
    reg=catalog(c);s=next((x for x in reg['products'] if x['name']==series),None)
    body={**dict(expected_version=load(c,p)['lock_version'],tag=tag,product_series_id=s['id'] if s else None,proposed_vendor_code='10066368',proposed_plant_id='30008606',component_approval='NOT_APPLICABLE',component_evidence='Synthetic scope excludes component suppliers',reason='Review candidate reference only, no engineering certification'),**extra}
    return c.put(f'/api/v1/projects/{p}/approvals/assignment',json=body)

def report(c,p):
    r=c.get(f'/api/v1/projects/{p}/approvals');assert r.status_code==200,r.text;return r.json()

def text(code='6000002356',extra=''):
    return (ROOT/'fixtures/synthetic/v2-pump.txt').read_text()+f'\nrequired_9com: {code}\nvendor_code: 10066368\nplant_id: 30008606\n'+extra

def evidence(c):
    r=c.post('/api/v1/approvals/evidence',json=dict(title='Synthetic current-source fixture',reference='SYNTHETIC-REVIEW-ONLY',source_date=str(date.today()),source_type='SYNTHETIC_TEST',authority='Fictional test authority',notes='Synthetic test only; not a customer approval'))
    assert r.status_code==201,r.text
    e=r.json()
    r=c.post(f"/api/v1/approvals/evidence/{e['id']}/attachment",files={'file':('synthetic.txt',b'SYNTHETIC DEMO\nNot an actual customer approval.')})
    assert r.status_code==200,r.text;return r.json()

def test_idempotent_exact_seed_and_many_series_lookup(client):
    a=catalog(client);b=catalog(client)
    assert [x['id'] for x in a['commodities']]==[x['id'] for x in b['commodities']]
    assert len(a['commodities'])==7 and len(a['products'])==8 and len(a['mappings'])==8
    assert {x['commodity_code'] for x in a['commodities']}=={'6000002283','6000002288','6000002346','6000002350','6000002355','6000002356','6000011675'}
    assert all(x['valid_until'] is None and x['valid_from'] is None and x['original_approval_date']=='2024-04-01' for x in a['commodities'])
    assert a['profiles'][0]['vendor_code']=='10066368' and a['profiles'][0]['plant_id']=='30008606'
    assert all(x['attachment_status']=='PENDING' and not x['document_inspected'] for x in a['evidence'])
    q=client.get('/api/v1/approvals/registry?code=6000002288').json()['commodities']
    assert len(q)==1 and {x['name'] for x in q[0]['product_series']}=={'WKB','RPH-V','WKTR'}
    assert client.get('/api/v1/approvals/registry?product_series=RPH&pump_classification=OH2&product_category=Pump%20%2F%20Pump%20Set&status=REQUIRES_VERIFICATION').json()['commodities'][0]['commodity_code']=='6000002356'

def test_historical_rph_match_is_not_current_verification_or_go(client):
    p=rfq(client);ready(client,p,text());assert assign(client,p).status_code==200
    a=report(client,p)['assessments'][0]
    assert a['required_9com']==a['matched_9com']=='6000002356' and a['product_series']['name']=='RPH'
    assert a['vendor_code']=='10066368' and a['relevant_plant_id']=='30008606'
    assert a['current_approval_verification']['status']=='REQUIRES_VERIFICATION'
    assert len(a['checks'])==10 and a['checks'][2]['decision_impact']=='NONE'
    assert a['checks'][1]['requirement_evidence'][0]['quote']=='required_9com: 6000002356'
    assert a['checks'][1]['requirement_evidence'][0]['line_start']>0
    acknowledge(client,p);run=process(client,p);s=run['snapshot']
    assert s['outcome']=='INSUFFICIENT DATA' and s['approval_registry_hash'] and s['customer_approvals']['assessments'][0]['matched_9com']=='6000002356'
    assert s['run_hash']==digest({k:v for k,v in s.items() if k!='run_hash'})
    for fmt in ('json','html','csv'):
        data=client.get(f"/api/v1/evaluations/{run['id']}/exports?format={fmt}").text
        assert '6000002356' in data and 'REQUIRES_VERIFICATION' in data and 'SQU-26-24' in data and s['run_hash'] in data

def test_megacpk_design_references_do_not_certify_iso(client):
    p=rfq(client);ready(client,p,text('6000002350'));assert assign(client,p,'MegaCPK').status_code==200
    a=report(client,p)['assessments'][0];assert a['matched_9com']=='6000002350'
    standards=client.get(f'/api/v1/projects/{p}/standards').json()
    refs=[x for x in standards['suggested'] if x.get('product_series_id')==a['product_series_id']]
    assert {x['code'] for x in refs}=={'ISO 2858','ISO 5199'} and all(not x['explicit'] for x in refs)
    assert not standards['explicit']
    acknowledge(client,p);s=process(client,p)['snapshot'];assert s['outcome']=='INSUFFICIENT DATA'
    assert not any(x.get('standard_reference') in ('ISO 2858','ISO 5199') and x['compliance_status']=='COMPLIANT' for x in s['compliance_matrix'])

def test_omega_api610_deviation_and_configuration_policy(client):
    p=rfq(client);ready(client,p,text('6000002355','standard: API 610 edition 12\n'));assert assign(client,p,'Omega').status_code==200
    a=report(client,p)['assessments'][0];assert a['matched_9com']=='6000002355' and a['omega_api610_deviation']
    assert a['checks'][-1]['criterion_id']=='ARAMCO-011' and a['checks'][-1]['decision_impact']=='INSUFFICIENT DATA'
    reg=catalog(client)
    change=client.put('/api/v1/approvals/policy',json=dict(expected_version=reg['policy']['policy_version'],unresolved_design_deviation='CONDITIONAL GO',rationale='Synthetic policy requires a defined engineering deviation acceptance before participation.'))
    assert change.status_code==200
    assert report(client,p)['assessments'][0]['checks'][-1]['decision_impact']=='CONDITIONAL GO'
    acknowledge(client,p);assert process(client,p)['snapshot']['outcome']=='INSUFFICIENT DATA' # Current approval still missing.

def test_unlisted_code_and_missing_explicit_code_are_not_negative_approval_claims(client):
    p=rfq(client);ready(client,p,text('9999999999'));assign(client,p)
    a=report(client,p)['assessments'][0];assert a['historical_approval_evidence'] is None and a['matched_9com'] is None
    acknowledge(client,p);assert process(client,p)['snapshot']['outcome']=='INSUFFICIENT DATA'
    p2=rfq(client);ready(client,p2,(ROOT/'fixtures/synthetic/v2-pump.txt').read_text());assign(client,p2)
    a=report(client,p2)['assessments'][0]
    assert a['required_9com'] is None and a['suggested_9com']==['6000002356'] and a['required_9com_status']=='NOT_SPECIFIED'
    assert len(catalog(client)['commodities'])==7

def test_other_customer_preserves_existing_decision_and_no_aramco_requirements(client):
    p=rfq(client,'Saudi Water Authority');ready(client,p)
    assert not report(client,p)['applicable']
    assert assign(client,p).status_code==422
    acknowledge(client,p);s=process(client,p)['snapshot']
    assert s['outcome']=='GO' and 'customer_approvals' not in s and not any(x['criterion_id'].startswith('ARAMCO-') for x in s['compliance_matrix'])

def test_mixed_package_isolation_and_parts_commodity_has_no_pump_model(client):
    eq=[dict(tag='P-101',product_category='Pump / Pump Set'),dict(tag='V-101',product_category='Valve'),dict(tag='S-101',product_category='Spare Parts')]
    p=rfq(client,equipment=eq);ready(client,p,text()+'\nTag: V-101\nrequired_9com: 6000002356\nTag: S-101\nrequired_9com: 6000011675\n')
    assign(client,p)
    assert assign(client,p,tag='V-101').status_code==422
    a={x['equipment_tag_id']:x for x in report(client,p)['assessments']}
    assert a['V-101']['matched_9com'] is None and a['V-101']['historical_approval_evidence'] is None and not a['V-101']['candidate_suggestions']
    assert a['S-101']['matched_9com']=='6000011675' and a['S-101']['product_series'] is None and not a['S-101']['candidate_suggestions']
    acknowledge(client,p);assert len(process(client,p)['snapshot']['tags'])==3

def test_vendor_plant_conflict_and_required_code_proposals_are_not_guessed(client):
    p=rfq(client);ready(client,p,text(extra='required_9com: 6000002350\n'))
    assert assign(client,p,proposed_vendor_code='00000000',proposed_plant_id='00000000').status_code==200
    a=report(client,p)['assessments'][0]
    assert a['required_9com'] is None and a['required_9com_status']=='CONFLICTING_OR_UNREVIEWED'
    assert a['checks'][4]['compliance_status']=='CONFLICTING INFORMATION' and a['checks'][5]['compliance_status']=='CONFLICTING INFORMATION'
    from app.extraction.service import normalize
    assert normalize('required_9com','0000000001','')[0]=='0000000001'
    assert normalize('required_9com','guessed','')[0] is None

def test_admin_permissions_private_evidence_and_cross_project_isolation(client):
    reg=catalog(client);p=rfq(client);e=evidence(client)
    assert 'object_key' not in e and client.get('/api/v1/approvals/evidence/'+e['id']+'/content').content.startswith(b'SYNTHETIC DEMO')
    source=reg['evidence'][0]
    assert client.get('/api/v1/approvals/evidence/'+source['id']+'/content').status_code==404
    login(client,'bob')
    assert client.post('/api/v1/approvals/evidence',json=dict(title='Attempt',reference='No authority',source_type='SYNTHETIC_TEST',authority='Nobody',notes='Unauthorized test')).status_code==403
    assert client.post('/api/v1/approvals/products',json=dict(name='Other',product_category='Valve',classification='Valve',reason='Unauthorized attempt')).status_code==403
    assert client.get(f'/api/v1/projects/{p}/approvals').status_code==404
    login(client,'outsider')
    assert client.get('/api/v1/approvals/evidence/'+e['id']).status_code==404
    assert client.get('/api/v1/approvals/evidence/'+e['id']+'/content').status_code==404
    assert client.get(f'/api/v1/projects/{p}/approvals').status_code==404
    assert client.put(f'/api/v1/projects/{p}/approvals/assignment',json=dict(expected_version=1,tag='P-101',reason='Cross-tenant assignment attempt')).status_code==404

def test_verification_append_only_preserves_frozen_reports_and_stales_current_run(client):
    p=rfq(client);ready(client,p,text());assign(client,p);acknowledge(client,p);run=process(client,p)
    previous={fmt:client.get(f"/api/v1/evaluations/{run['id']}/exports?format={fmt}").content for fmt in ('json','html','csv')}
    reg=catalog(client);commodity=next(x for x in reg['commodities'] if x['commodity_code']=='6000002356');e=evidence(client)
    body=dict(evidence_id=e['id'],status='VERIFIED',verification_date=str(date.today()),authorized_current_source=True,reviewer_notes='Synthetic verification fixture, never actual approval',supersedes_verification_id=None)
    url=f"/api/v1/approvals/commodities/{commodity['id']}/verifications"
    v=client.post(url,json=body);assert v.status_code==201,v.text
    assert not v.json()['effective_authorized']
    assert report(client,p)['assessments'][0]['current_approval_verification']['status']=='REQUIRES_VERIFICATION'
    assert client.post(url,json=body).status_code==409
    body.update(status='SUPERSEDED',supersedes_verification_id=v.json()['id'])
    assert client.post(url,json=body).status_code==201
    assert len(catalog(client)['verifications'])==2
    assert load(client,p)['evaluation'][-1]['is_stale']
    assert client.post(f"/api/v1/evaluations/{run['id']}/adjudications",json=dict(disposition='ACKNOWLEDGED',reason='Review current evidence',evidence='Synthetic source')).status_code==409
    for fmt,content in previous.items():assert client.get(f"/api/v1/evaluations/{run['id']}/exports?format={fmt}").content==content
    assert not client.get(f'/api/v1/projects/{p}/summary').json()['reviewed']
    acknowledge(client,p);assert process(client,p)['snapshot']['outcome']=='INSUFFICIENT DATA'

def test_historical_letter_cannot_verify_current_and_demo_claim_cannot_bypass_source(client):
    reg=catalog(client);commodity=reg['commodities'][0]
    url=f"/api/v1/approvals/commodities/{commodity['id']}/verifications"
    body=dict(evidence_id=reg['evidence'][0]['id'],status='VERIFIED',verification_date=str(date.today()),authorized_current_source=True,reviewer_notes='Attempt to reuse historical evidence')
    assert client.post(url,json=body).status_code==422
    e=evidence(client);body['evidence_id']=e['id'];body['verification_date']=str(date.today()+timedelta(days=1))
    assert client.post(url,json=body).status_code==422
    login(client,'bob');body['verification_date']=str(date.today())
    assert client.post(url,json=body).status_code==403

def test_admin_mapping_and_commodity_revisions_keep_original_audit_sources(client):
    reg=catalog(client);e=evidence(client);c=next(x for x in reg['commodities'] if x['commodity_code']=='6000002356')
    payload=dict(profile_id=c['profile_id'],commodity_code=c['commodity_code'],commodity_description=c['commodity_description'],product_category=c['product_category'],evidence_id=e['id'],original_approval_date=c['original_approval_date'],expected_version=c['version'],reason='Synthetic newer reference, retain historical letter')
    assert client.post('/api/v1/approvals/commodities',json=payload).status_code==201
    assert client.post('/api/v1/approvals/commodities',json=payload).status_code==409
    history=client.get('/api/v1/approvals/history').json()
    change=next(x for x in history if x['action']=='COMMODITY_SOURCE_REVISED')
    assert change['before']['evidence_id']==c['evidence_id'] and change['after']['evidence_id']==e['id']
    assert client.get('/api/v1/approvals/evidence/'+c['evidence_id']).status_code==200
    product=next(x for x in reg['products'] if x['name']=='WKB')
    old=next(x for x in reg['mappings'] if x['product_series_id']==product['id'])
    mp=dict(product_series_id=product['id'],commodity_id=old['commodity_id'],evidence_id=e['id'],slide=3,reason='Synthetic mapping source revision',expected_version=old['version'])
    assert client.post('/api/v1/approvals/mappings',json=mp).status_code==201
    assert len(catalog(client)['mappings'])==8

def test_current_verification_dates_do_not_invent_expiry_or_perpetual_approval():
    today=str(date.today());past=str(date.today()-timedelta(days=5))
    c={'id':'c'};source={'id':'e'}
    v=dict(id='v',commodity_id='c',evidence_id='e',effective_authorized=True,verification_date=today,reviewed_by='Authorized reviewer',status='VERIFIED',reviewer_notes='Unit fixture only',valid_from=None,valid_until=None)
    assert current_status(c,[v],[source])['status']=='VERIFIED'
    v['verification_date']=past
    assert current_status(c,[v],[source])['status']=='REQUIRES_VERIFICATION'
    v.update(valid_from=past,valid_until=today)
    assert current_status(c,[v],[source])['status']=='VERIFIED'
    v['valid_until']=past
    assert current_status(c,[v],[source])['status']=='REQUIRES_VERIFICATION'

def test_additive_migration_retains_existing_rfq_and_evaluation(client):
    """Exercise an actual 0001-shaped database upgrade with existing records."""
    import os,sys,subprocess
    from sqlalchemy import text as sql_text
    from app.db import engine,add
    from app.approvals.store import TABLES
    from test_workflow import project,evaluate,upload,accept
    from app.jobs.worker import run_once
    p=project(client);upload(client,p);run_once();accept(client,p);run=evaluate(client,p)
    original=run['snapshot'];hash_before=original['run_hash']
    for model in reversed(TABLES):model.__table__.drop(engine,checkfirst=True)
    with engine.begin() as conn:
        conn.execute(sql_text('CREATE TABLE IF NOT EXISTS alembic_version (version_num varchar(32) NOT NULL PRIMARY KEY)'))
        conn.execute(sql_text('DELETE FROM alembic_version'));conn.execute(sql_text("INSERT INTO alembic_version VALUES ('0001')"))
    r=subprocess.run([sys.executable,'-m','alembic','upgrade','head'],cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'backend'),'DATABASE_URL':engine.url.render_as_string(hide_password=False)},capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    assert load(client,p)['evaluation'][0]['snapshot']==original and load(client,p)['evaluation'][0]['snapshot']['run_hash']==hash_before
    assert len(catalog(client)['commodities'])==7
