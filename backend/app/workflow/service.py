"""BidFit 2.0: additive workflow over the existing tenant-scoped domain store."""
import json,re,uuid
from pathlib import Path
from datetime import date
from sqlalchemy import select,text
from app.db import Record,add,serialize,now
from app.rules.engine import PACK, digest, rollup
CONFIG=Path(__file__).resolve().parents[1]/'configuration'
BASE_MASTER=json.loads((CONFIG/'classification.json').read_text())
BASE_STANDARDS=json.loads((CONFIG/'standards.json').read_text())

def rows(db,tenant,kind,pid=None):
    q=select(Record).where(Record.tenant_id==tenant,Record.kind==kind)
    if pid is not None:q=q.where(Record.project_id==pid)
    return db.scalars(q.order_by(Record.created_at,Record.id)).all()

def ensure_registry(db,tenant):
    if db.scalar(select(Record.id).where(Record.tenant_id==tenant,Record.kind=='master_config').limit(1)):return
    db.execute(text('SELECT pg_advisory_xact_lock(hashtext(:key))'),{'key':'bidfit-registry-'+tenant})
    if rows(db,tenant,'master_config'):return
    add(db,'master_config',tenant,**BASE_MASTER)
    for s in BASE_STANDARDS:
        add(db,'standard_ref',tenant,**s,edition=None,version=1,source_reference='Owner-supplied identifier list only; no licensed clause content',availability='REFERENCE NOT AVAILABLE / REQUIRES REVIEW',approval_status='UNVERIFIED')
    for old in PACK:
        r=dict(criterion_id=old['criterion_id'],name='Training screening: '+old['field'],field=old['field'],product_category='Pump / Pump Set',operator=old['operator'],minimum=old['minimum'],maximum=old['maximum'],allowed_values=old['allowed_values'],units={'flow':'m3/s','head':'m'}.get(old['field'],''),severity='MINOR' if old['waiver_policy']=='WAIVABLE' else 'MAJOR',waiver_policy=old['waiver_policy'],scope='candidate',project_prohibition=False,confirmed_prohibition_value=None,standard_id=None,standard_edition=None,clause_reference=None,market_area=None,application=None,customer=None,source_reference='Inherited synthetic training contract v1 — NOT KSB rules',capability_reference='Fictional demo scope only; no equipment performance claim',effective_date='2000-01-01',namespace='synthetic-demo-v2')
        if old['field']=='prohibition':r.update(scope='project',project_prohibition=True,confirmed_prohibition_value='confirmed-demo-ban',severity='HARD STOP')
        add(db,'engineering_rule',tenant,**r,version=1,approval_status='APPROVED',approved_by='Synthetic fixture initializer; not corporate engineering approval',approved_at=now(),content_hash=digest(r),synthetic_only=True)
    add(db,'quote_template',tenant,name='Preliminary technical draft',version=1,source_reference='BidFit demonstration template; no company commercial terms',approval_status='DRAFT_ONLY',sections=['RFQ context','Equipment','Technical findings','Missing information','Pricing not activated'])

def master(db,tenant):
    ensure_registry(db,tenant)
    return rows(db,tenant,'master_config')[-1]

def validate_classification(db,tenant,classification,equipment):
    from fastapi import HTTPException
    m=master(db,tenant).data
    if classification.market_area not in m['markets'] or classification.application not in m['markets'][classification.market_area]:raise HTTPException(422,'Choose an application in the selected market')
    names=[e.tag for e in equipment]
    if len(names)!=len(set(names)):raise HTTPException(422,'Equipment tags must be unique')
    if classification.product_category!='Mixed Package' and any(e.product_category!=classification.product_category for e in equipment):raise HTTPException(422,'Equipment categories must match, or choose Mixed Package')

def equipment(p):
    return p.data.get('equipment') or [dict(tag=t,product_category='Pump / Pump Set',description='',quantity=None) for t in p.data['tags']]

def source_rows(db,p):
    facts=[serialize(r) for r in rows(db,p.tenant_id,'fact',p.id)]
    docs=[serialize(r) for r in rows(db,p.tenant_id,'document',p.id)]
    for d in docs:d.pop('object_key',None)
    return facts,docs

def summary(db,p):
    facts,docs=source_rows(db,p)
    m=master(db,p.tenant_id).data;groups=[];missing=[];conflicts=[]
    for item in equipment(p):
        tag=item['tag'];fields={}
        for f in facts:
            if f['tag']==tag and f['status']!='REJECTED':fields.setdefault(f['field'],[]).append(f)
        for field,fs in fields.items():
            values={json.dumps(f['normalized_value'],sort_keys=True) for f in fs if f['normalized_value'] is not None}
            if len(values)>1:conflicts.append(dict(tag=tag,field=field,fact_ids=[f['id'] for f in fs],reason='Conflicting requirements; upload order does not establish precedence'))
        quantities=fields.get('quantity',[])
        if item.get('quantity') is not None and any(f['status']=='ACCEPTED' and f['normalized_value']!=item['quantity'] for f in quantities):
            conflicts.append(dict(tag=tag,field='quantity',fact_ids=[f['id'] for f in quantities],reason='Equipment register quantity differs from accepted document quantity; correct classification or evidence'))
        for field in m['required_fields'].get(item['product_category'],[]):
            if not any(f['status']=='ACCEPTED' and f['normalized_value'] is not None for f in fields.get(field,[])):
                missing.append(dict(tag=tag,field=field,reason='Missing accepted input; no value inferred'))
        groups.append(dict(**item,fields=fields))
    coverage_gaps=[dict(document_id=d['id'],filename=d['filename'],gaps=d.get('gaps') or ['Document processing not complete']) for d in docs if d.get('state') not in ('NEEDS_REVIEW','READY_FOR_EVALUATION','EXPANDED') or d.get('gaps')]
    base=dict(project_name=p.data['name'],classification=p.data.get('classification'),equipment=groups,documents=docs,missing=missing,conflicts=conflicts,coverage_gaps=coverage_gaps,unreviewed_count=sum(f['status']=='PROPOSED' for f in facts),notes=p.data.get('summary_notes',''),method='DEMO_PATTERN_NOT_AI' if all(f['method']=='DEMO_PATTERN_NOT_AI' for f in facts) else 'LLM_PROPOSALS_REQUIRE_REVIEW')
    base['summary_hash']=digest(base)
    reviews=rows(db,p.tenant_id,'summary_review',p.id)
    base['reviewed']=any(r.data['summary_hash']==base['summary_hash'] for r in reviews)
    return base

def active_rules(db,tenant):
    ensure_registry(db,tenant)
    grouped={}
    for r in rows(db,tenant,'engineering_rule'):grouped.setdefault(r.data['criterion_id'],[]).append(r)
    return [max([r for r in rs if r.data['approval_status']=='APPROVED'] or rs,key=lambda r:r.data['version']) for rs in grouped.values()]

def registry_hash(db,tenant):
    return digest([dict(id=r.id,**r.data) for r in active_rules(db,tenant)])

def standard_code(value):
    # Identifiers and editions only, never copyrighted clauses or inferred requirements.
    for code in [s['code'] for s in BASE_STANDARDS]+['API 598','ASME B16.34']:
        if value.upper().startswith(code.upper()):
            tail=value[len(code):].strip(' ,:;-')
            tail=re.sub(r'^(edition|ed\.?|rev\.?)\s*','',tail,flags=re.I).strip()
            return code,tail or None
    return value,None

def standards(db,p):
    ensure_registry(db,p.tenant_id)
    registry=rows(db,p.tenant_id,'standard_ref');facts,_=source_rows(db,p)
    decisions=rows(db,p.tenant_id,'standard_review',p.id)
    selected={}
    for r in decisions:selected[(r.data['tag'],r.data['code'],r.data.get('edition'))]=serialize(r)
    required=[];suggested=[];c=p.data.get('classification') or {}
    rules=active_rules(db,p.tenant_id)
    for f in facts:
        if f['field']!='standard' or f['status']=='REJECTED':continue
        code,edition=standard_code(str(f['normalized_value'] or f['raw_value']))
        available=[r for r in rules if r.data['approval_status']=='APPROVED' and r.data.get('standard_edition')==edition and any(s.id==r.data.get('standard_id') and s.data['code']==code for s in registry)]
        required.append(dict(tag=f['tag'],code=code,edition=edition,explicit=True,source=f['source'],fact_id=f['id'],fact_status=f['status'],review=selected.get((f['tag'],code,edition)),approved_rule_ids=[r.id for r in available],availability='SYNTHETIC RULES ONLY' if available else 'REFERENCE NOT AVAILABLE / REQUIRES REVIEW'))
    for item in equipment(p):
        for ref in registry:
            d=ref.data
            if d.get('products') and item['product_category'] not in d['products']:continue
            if d.get('customer') and d['customer'] not in (c.get('customer'),c.get('customer_profile')):continue
            key=(item['tag'],d['code'],d.get('edition'))
            if any((r['tag'],r['code'],r['edition'])==key for r in required):continue
            suggested.append(dict(tag=item['tag'],code=d['code'],edition=d.get('edition'),standard_id=ref.id,explicit=False,reason=d.get('reason','Reference selected for review'),review=selected.get(key),availability=d['availability']))
    return dict(suggested=suggested,explicit=required,notice='Suggestions are never mandatory from market segment alone. Confirm product, application, contract edition and authority.')

def finding(criterion,tag,product,status,reason,**kw):
    return dict(criterion_id=criterion,tag=tag,product_category=product,result={'COMPLIANT':'PASS','NON-COMPLIANT':'FAIL','DEVIATION':'FAIL','NOT APPLICABLE':'NOT_APPLICABLE'}.get(status,'UNKNOWN'),compliance_status=status,reason=reason,field=kw.pop('field',None),decision_impact=kw.pop('decision_impact','NONE' if status in ('COMPLIANT','NOT APPLICABLE') else 'INSUFFICIENT DATA'),severity=kw.pop('severity',None),method='Deterministic evidence/rule comparison; synthetic namespace',fact_ids=kw.pop('fact_ids',[]),requirement_evidence=kw.pop('requirement_evidence',[]),capability_evidence=kw.pop('capability_evidence',None),rule_version=kw.pop('rule_version',None),rule_hash=kw.pop('rule_hash',None),authority=kw.pop('authority','No approved authority supplied'),clarification=None if status in ('COMPLIANT','NOT APPLICABLE') else 'Engineer: '+reason,approval_status=kw.pop('approval_status','REQUIRES ENGINEERING REVIEW'),**kw)

def compliance(db,p):
    from fastapi import HTTPException
    s=summary(db,p)
    if not s['reviewed']:raise HTTPException(409,'Review the current RFQ summary before PROCESS RFQ')
    facts,docs=source_rows(db,p);rs=active_rules(db,p.tenant_id);std=standards(db,p);output=[]
    for item in equipment(p):
        tag=item['tag'];product=item['product_category'];findings=[];hard=False
        item_facts=[f for f in facts if f['tag']==tag and f['status']!='REJECTED']
        for miss in s['missing']:
            if miss['tag']==tag:findings.append(finding('INPUT_'+miss['field'].upper(),tag,product,'MISSING INFORMATION',miss['reason'],field=miss['field']))
        for conflict in s['conflicts']:
            if conflict['tag']==tag:findings.append(finding('CONFLICT_'+conflict['field'].upper(),tag,product,'CONFLICTING INFORMATION',conflict['reason'],field=conflict['field'],fact_ids=conflict['fact_ids']))
        if not docs or s['coverage_gaps']:findings.append(finding('COVERAGE',tag,product,'NOT VERIFIED','Missing or incomplete document coverage; resolve every relevant file'))
        applicable_count=0
        for row in rs:
            r=row.data
            if r['product_category']!=product:continue
            context=p.data.get('classification') or {}
            selectors=[('market_area','market_area'),('application','application'),('customer','customer')]
            if any(r.get(key) and context.get(value)!=r[key] for key,value in selectors):continue
            if r.get('standard_id'):
                ref=db.get(Record,r['standard_id'])
                checks=[x for x in std['explicit']+std['suggested'] if x['tag']==tag and ref and x['code']==ref.data['code'] and x['edition']==r['standard_edition']]
                if not checks or not any(x.get('review') and x['review']['disposition']=='APPLICABLE' for x in checks):continue
            applicable_count+=1
            fs=[f for f in item_facts if f['field']==r['field']]
            accepted=[f for f in fs if f['status']=='ACCEPTED' and f['normalized_value'] is not None]
            vals={json.dumps(f['normalized_value'],sort_keys=True) for f in accepted}
            basis_facts=[f for f in item_facts if f['field']=='pressure_basis' and f['status']=='ACCEPTED']
            status='NOT VERIFIED';reason='Required rule is not approved or is not yet effective';impact='INSUFFICIENT DATA'
            if r['approval_status']=='APPROVED' and date.fromisoformat(r['effective_date'])<=date.today():
                if r.get('pressure_basis') and (not basis_facts or any(f['normalized_value']!=r['pressure_basis'] for f in basis_facts)):
                    status='MISSING INFORMATION';reason='Explicit pressure basis matching the rule is missing or conflicting'
                elif len(vals)>1:status='CONFLICTING INFORMATION';reason='Accepted requirements contradict one another'
                elif not accepted:status='MISSING INFORMATION';reason='Missing accepted '+r['field']
                elif len(accepted)!=len(fs):status='REQUIRES ENGINEERING REVIEW';reason='Unreviewed evidence for '+r['field']
                else:
                    v=accepted[0]['normalized_value']
                    ok=r['operator']=='present' or (v in r['allowed_values'] if r['operator']=='enum_in' else (r['minimum'] is None or v>=r['minimum']) and (r['maximum'] is None or v<=r['maximum']))
                    if ok:status='COMPLIANT';reason='Positively supported against the identified synthetic screening rule only';impact='NONE'
                    elif r['project_prohibition'] and str(v)==r['confirmed_prohibition_value']:
                        status='NON-COMPLIANT';reason='Confirmed non-waivable synthetic project prohibition';impact='NO-GO';hard=True
                    elif r['waiver_policy']=='WAIVABLE':status='DEVIATION';reason='Explicit waivable deviation under synthetic rule; obtain acceptance';impact='CONDITIONAL GO'
                    else:status='NON-COMPLIANT';reason='Candidate/policy check fails; complete approved portfolio exclusion is unavailable';impact='INSUFFICIENT DATA'
            findings.append(finding(r['criterion_id'],tag,product,status,reason,field=r['field'],decision_impact=impact,severity=r['severity'],fact_ids=[f['id'] for f in fs],requirement_evidence=[f['source'] for f in fs],capability_evidence=r.get('capability_reference'),rule_id=row.id,rule_version=r['version'],rule_hash=r['content_hash'],authority=r['source_reference'],required_condition=dict(operator=r['operator'],minimum=r['minimum'],maximum=r['maximum'],allowed_values=r['allowed_values'],units=r['units']),standard_id=r.get('standard_id'),standard_edition=r.get('standard_edition'),clause_reference=r.get('clause_reference'),waiver_policy=r['waiver_policy'],scope=r['scope'],approval_status=r['approval_status']))
        if applicable_count==0:findings.append(finding('RULE_COVERAGE',tag,product,'NOT VERIFIED','No approved product-specific engineering coverage; no selection/capability inferred'))
        checked=set()
        for ref in std['explicit']+[x for x in std['suggested'] if x.get('review') and x['review']['disposition']=='APPLICABLE']:
            if ref['tag']!=tag:continue
            key=(ref['code'],ref['edition'])
            if key in checked:continue
            checked.add(key)
            decision=ref.get('review');status='NOT VERIFIED';reason='REFERENCE NOT AVAILABLE / REQUIRES REVIEW'
            if decision and decision['disposition']=='NOT_APPLICABLE':status='NOT APPLICABLE';reason=decision['reason']
            elif not decision or decision['disposition']!='APPLICABLE':reason='Standards applicability requires engineering confirmation'
            elif ref.get('approved_rule_ids'):status='NOT VERIFIED';reason='Synthetic clause checks exist; full standard compliance has not been verified'
            other=[x for x in std['explicit'] if x['tag']==tag and x['code']==ref['code'] and x['edition']!=ref['edition']]
            if other:status='CONFLICTING INFORMATION';reason='Contradictory standard editions; explicit precedence evidence required'
            findings.append(finding('STD_'+str(len(checked)),tag,product,status,reason,standard_reference=ref['code'],standard_edition=ref['edition'],requirement_evidence=[ref['source']] if ref.get('source') else [],fact_ids=[ref['fact_id']] if ref.get('fact_id') else []))
        outcome='NO-GO' if hard else 'INSUFFICIENT DATA' if any(f['decision_impact']=='INSUFFICIENT DATA' for f in findings) else 'CONDITIONAL GO' if any(f['decision_impact']=='CONDITIONAL GO' for f in findings) else 'GO'
        output.append(dict(tag=tag,product_category=product,outcome=outcome,results=findings,hydraulic_selection='UNVERIFIED — no approved curves or compatibility data',coverage_complete=not s['coverage_gaps'] and bool(docs)))
    return s,output,std,rs
