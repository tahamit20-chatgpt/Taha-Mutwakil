"""Deterministic approval evidence checks, never a pump selection engine."""
import json,re
from datetime import date
from pathlib import Path
from sqlalchemy import select,text
from fastapi import HTTPException
from app.db import Record,add,now
from app.rules.engine import digest
from .store import (TABLES,ApprovalProfile,ApprovalEvidence,ApprovalCommodity,
    ProductSeries,ProductApprovalMapping,ApprovalVerification,encode,insert)

SEED=json.loads((Path(__file__).resolve().parents[1]/'configuration/aramco_seed.json').read_text())
POLICY_VERSION='aramco-evidence-completeness-v1'

def entries(db,tenant,model):
    return list(db.scalars(select(model).where(model.tenant_id==tenant).order_by(model.created_at,model.id)))

def get(db,model,rid,tenant,lock=False):
    q=select(model).where(model.id==rid,model.tenant_id==tenant)
    if lock:q=q.with_for_update()
    row=db.scalar(q)
    if not row:raise HTTPException(404,'Approval reference not found')
    return row

def event(db,tenant,actor,action,rid,before=None,after=None,reason=None):
    add(db,'approval_event',tenant,actor=actor,action=action,object_id=rid,before=before,after=after,reason=reason)

def ensure_registry(db,tenant):
    if entries(db,tenant,ApprovalProfile):return
    db.execute(text('SELECT pg_advisory_xact_lock(hashtext(:key))'),{'key':'bidfit-approvals-'+tenant})
    if entries(db,tenant,ApprovalProfile):return
    base=dict(SEED['profile']);key=base.pop('customer_key');vendor=base.pop('vendor_code');plant=base.pop('plant_id')
    profile=insert(db,ApprovalProfile,tenant,customer_key=key,vendor_code=vendor,plant_id=plant,
        data={**base,'current_verification_status':'REQUIRES_VERIFICATION','last_verified_at':None,'verified_by':None,'provenance':SEED['provenance'],'seed_version':SEED['seed_version']})
    sources=[]
    for key in ('letter','presentation'):
        sources.append(insert(db,ApprovalEvidence,tenant,data={**SEED[key],'provenance':SEED['provenance'],
            'input_reference':'docs/ARAMCO_IMPLEMENTATION_REQUEST.md','input_hash':digest(SEED),
            'attachment_status':'PENDING','document_inspected':False,'object_key':None,'sha256':None,
            'authorized_current_source':False,'synthetic':False}))
    commodities={}
    for code,description,category in SEED['commodities']:
        commodities[code]=insert(db,ApprovalCommodity,tenant,profile_id=profile.id,commodity_code=code,evidence_id=sources[0].id,
            data=dict(commodity_description=description,product_category=category,original_approval_date='2024-04-01',original_reference='SQU-26-24',
                historical_evidence_status='REPORTED_HISTORICAL_LISTING_ATTACHMENT_PENDING',historical_original_listing=True,historical_source_evidence_id=sources[0].id,current_status='REQUIRES_VERIFICATION',
                verification_required=True,valid_from=None,valid_until=None,page=None,restrictions='',updated_at=now()))
    for p in SEED['products']:
        product=insert(db,ProductSeries,tenant,name=p['name'],data=dict(product_category='Pump / Pump Set',classification=p['classification'],
            api_classification=p['api_classification'],design_standards=p['design_standards'],manufacturing_reference=None,
            engineering_verification_status='NOT_VERIFIED',engineering_notes=p.get('engineering_notes',''),provenance=SEED['provenance']))
        insert(db,ProductApprovalMapping,tenant,product_series_id=product.id,commodity_id=commodities[p['code']].id,profile_id=profile.id,evidence_id=sources[1].id,
            data=dict(applicable_plant_id=plant,slide=p['slide'],mapping_verification_status='REPORTED_MAPPING_SOURCE_PENDING',engineering_notes=p.get('engineering_notes',''),updated_at=now()))
    add(db,'approval_policy',tenant,policy_id=POLICY_VERSION,policy_version=1,unresolved_design_deviation='INSUFFICIENT DATA',
        rationale='Evidence completeness gate only. Historical listing, mapping, current eligibility, engineering suitability and commercial assessment remain separate.',
        essential_missing='INSUFFICIENT DATA',candidate_mismatch='INSUFFICIENT DATA',unlisted_historical='INSUFFICIENT DATA',
        no_go_authority='No live authoritative blocking rule configured; this module cannot emit NO-GO',
        scope='Workflow evidence policy; not corporate engineering approval',actor='owner-supplied structured import')
    event(db,tenant,'owner-supplied structured import','APPROVAL_REGISTRY_SEEDED',profile.id,after={'seed_version':SEED['seed_version'],'commodity_count':7,'mapping_count':8},reason=SEED['provenance'])

def policy(db,tenant):
    from app.workflow.service import rows
    return rows(db,tenant,'approval_policy')[-1]

def public_evidence(row):
    result=encode(row);result.pop('object_key',None);return result

def catalog(db,tenant):
    ensure_registry(db,tenant)
    return dict(profiles=[encode(x) for x in entries(db,tenant,ApprovalProfile)],
        commodities=[encode(x) for x in entries(db,tenant,ApprovalCommodity)],
        products=[encode(x) for x in entries(db,tenant,ProductSeries)],
        mappings=[encode(x) for x in entries(db,tenant,ProductApprovalMapping)],
        evidence=[public_evidence(x) for x in entries(db,tenant,ApprovalEvidence)],
        verifications=[encode(x) for x in entries(db,tenant,ApprovalVerification)],policy={**policy(db,tenant).data,'id':policy(db,tenant).id},
        provenance=SEED['provenance'],notice='Commodity listing and internal portfolio references do not establish current approval or technical compliance.')

def registry_hash(db,tenant):
    # Include the evaluation date so a verification that expires tomorrow cannot
    # leave today's recommendation apparently current tomorrow. No expiry is invented.
    return digest({'registry':catalog(db,tenant),'evaluation_date':date.today().isoformat()})

def applicable(p):
    c=p.data.get('classification') or {}
    aliases={'saudi aramco','aramco','saudi arabian oil company'}
    return any(re.sub(r'\s+',' ',str(c.get(key,'')).strip()).casefold() in aliases for key in ('customer','customer_profile','end_user'))

def current_status(commodity,verifications,evidence):
    vs=[v for v in verifications if v['commodity_id']==commodity['id']]
    latest=vs[-1] if vs else None
    base=dict(status='REQUIRES_VERIFICATION',last_verified_at=latest['verification_date'] if latest else None,
        verified_by=latest['reviewed_by'] if latest else None,verification_record=latest,
        reason='No authorized current verification is available. A 2024 historical listing is not a live approval.')
    if not latest:return base
    source=next(x for x in evidence if x['id']==latest['evidence_id'])
    base['source']=source
    if not latest.get('effective_authorized'):
        base['reason']='Recorded review is not authorized current evidence; demonstration or metadata-only records cannot verify customer approval.'
        return base
    today=date.today().isoformat()
    if latest.get('valid_from') and today<latest['valid_from'] or latest.get('valid_until') and today>latest['valid_until']:
        base['reason']='The explicitly supplied validity period does not cover the evaluation date.';return base
    if latest['verification_date']!=today and not (latest.get('valid_from') and latest.get('valid_until') and latest['valid_from']<=today<=latest['valid_until']):
        base['reason']='Verification is evidence as of its recorded date only; no current validity period was supplied.';return base
    base.update(status=latest['status'],reason=latest['reviewer_notes']);return base

def accepted(facts,field):
    all_fs=[f for f in facts if f['field']==field and f['status']!='REJECTED']
    values={str(f['normalized_value']) for f in all_fs if f['status']=='ACCEPTED' and f['normalized_value'] is not None}
    unreviewed=any(f['status']!='ACCEPTED' for f in all_fs)
    return (next(iter(values)) if len(values)==1 and not unreviewed else None),all_fs,len(values)>1 or unreviewed

def assessments(db,p):
    from app.workflow.service import equipment,source_rows,rows,finding
    if not applicable(p):
        return dict(applicable=False,status='NOT_APPLICABLE',notice='Saudi Aramco approval checks do not apply to this customer.',assessments=[])
    c=catalog(db,p.tenant_id);profile=c['profiles'][0];facts,_=source_rows(db,p)
    assignments={r.data['tag']:r for r in rows(db,p.tenant_id,'approval_assignment',p.id)}
    results=[]
    for item in equipment(p):
        tag=item['tag'];category=item['product_category'];fs=[f for f in facts if f['tag']==tag]
        required,code_facts,code_conflict=accepted(fs,'required_9com')
        a=assignments[tag].data if tag in assignments else {}
        series=next((x for x in c['products'] if x['id']==a.get('product_series_id')),None)
        # Never apply a pump mapping to valves or parts, including after a
        # classification edit that makes a previous assignment incompatible.
        if series and series['product_category']!=category:series=None
        commodity=next((x for x in c['commodities'] if x['commodity_code']==required and x['product_category']==category),None)
        mappings=[x for x in c['mappings'] if series and x['product_series_id']==series['id'] and x['profile_id']==profile['id']]
        mapped=next((x for x in mappings if commodity and x['commodity_id']==commodity['id']),None)
        current=current_status(commodity,c['verifications'],c['evidence']) if commodity else dict(status='REQUIRES_VERIFICATION',reason='No matched historical commodity; obtain a current authorized classification and approval source.',verification_record=None)
        used_sources={x['id'] for x in c['evidence'] if x['source_type']=='OFFICIAL_HISTORICAL_LETTER_REPORTED_BY_OWNER'}
        used_sources.update(x['evidence_id'] for x in mappings)
        if commodity:used_sources.update([commodity['evidence_id'],commodity.get('historical_source_evidence_id')])
        if current.get('verification_record'):used_sources.add(current['verification_record']['evidence_id'])
        relevant_sources=[x for x in c['evidence'] if x['id'] in used_sources]
        suggested_codes=[x['commodity_code'] for x in c['commodities'] if any(m['commodity_id']==x['id'] for m in mappings)]
        product_type,_,_=accepted(fs,'pump_type')
        suggestions=[]
        if category=='Pump / Pump Set':
            suggestions=[dict(id=x['id'],name=x['name'],classification=x['classification'],label='INFERRED CANDIDATE — REQUIRES ENGINEER VERIFICATION') for x in c['products'] if x['product_category']==category and (not product_type or (x.get('api_classification') and x['api_classification'].casefold()==product_type.casefold()) or x['name'].casefold()==product_type.casefold())]
        check_rows=[]
        def check(number,status,reason,impact='INSUFFICIENT DATA',sources=None,**kw):
            check_rows.append(finding(f'ARAMCO-{number:03}',tag,category,status,reason,decision_impact=impact,
                requirement_evidence=sources or [],authority='Versioned approval evidence-completeness policy; not engineering certification',
                rule_version=c['policy']['policy_version'],rule_hash=digest(c['policy']),approval_status='WORKFLOW EVIDENCE POLICY',
                supporting_references=relevant_sources,method='Deterministic approval-reference comparison; source attachments and live authorization pending',**kw))
        check(1,'COMPLIANT','Applicable: Saudi Aramco is the selected customer profile, customer or end user.','NONE')
        check(2,'CONFLICTING INFORMATION' if code_conflict else 'COMPLIANT' if required else 'MISSING INFORMATION',
            'Conflicting or unreviewed 9COM evidence; no precedence inferred.' if code_conflict else f'Explicit reviewed customer-required 9COM: {required}.' if required else 'Required 9COM not specified in accepted RFQ evidence. Suggested mappings cannot fill this requirement.',
            'NONE' if required else 'INSUFFICIENT DATA',sources=[f['source'] for f in code_facts],field='required_9com')
        original_listing=bool(commodity and commodity.get('historical_original_listing'))
        check(3,'COMPLIANT' if original_listing else 'NOT VERIFIED',
            f'Listed in owner-reported historical evidence SQU-26-24 ({required}); source letter attachment pending. Not current verification.' if original_listing else 'Not Listed in Available Historical Evidence for this item category, or required 9COM is missing. A new registry reference does not establish a listing in the 2024 letter or prove current non-approval.',
            'NONE' if original_listing else 'INSUFFICIENT DATA')
        parts_only=category=='Spare Parts' and commodity and required=='6000011675' and not series
        check(4,'COMPLIANT' if mapped or parts_only else 'NOT VERIFIED',
            'Matched internal product-to-commodity mapping; presentation attachment pending. Exact configuration remains unverified.' if mapped else 'Parts commodity only — no automatic pump-model association.' if parts_only else 'Candidate not selected, category mismatch, or no matching internal product mapping; not evidence of current ineligibility.',
            'NONE' if mapped or parts_only else 'INSUFFICIENT DATA')
        identifier_values={}
        for number,key,proposed_key,expected in [(5,'vendor_code','proposed_vendor_code',profile['vendor_code']),(6,'plant_id','proposed_plant_id',profile['plant_id'])]:
            extracted,source_fs,conflict=accepted(fs,key);proposed=a.get(proposed_key)
            if proposed and extracted and proposed!=extracted:conflict=True
            actual=proposed or extracted;identifier_values[proposed_key]=actual
            ok=actual==expected and not conflict
            check(number,'COMPLIANT' if ok else 'CONFLICTING INFORMATION' if conflict else 'NOT VERIFIED',
                f'{key}: {actual} matches historical reference {expected}; current eligibility still separate.' if ok else f'{key}: {actual or "Unknown"}; historical reference {expected}. Resolve missing, mismatched or contradictory identifiers.',
                'NONE' if ok else 'INSUFFICIENT DATA',sources=[f['source'] for f in source_fs],field=key)
        current_ok=current['status']=='VERIFIED'
        current_conditional=current['status']=='CONDITIONAL'
        check(7,'COMPLIANT' if current_ok else 'DEVIATION' if current_conditional else 'NOT VERIFIED',current['reason'],
            'NONE' if current_ok else 'CONDITIONAL GO' if current_conditional else 'INSUFFICIENT DATA',field='current_approval_verification')
        check(8,'REQUIRES ENGINEERING REVIEW','Evaluated Separately: duty, materials, configuration, manufacture and hydraulic suitability require independent engineering evidence.','NONE')
        check(9,'REQUIRES ENGINEERING REVIEW','Evaluated Separately: actual RFQ standards, editions and deviations govern; portfolio design references are not contractual requirements or compliance certificates.','NONE')
        component=a.get('component_approval','PENDING')
        explicit_components,component_fs,component_conflict=accepted(fs,'component_approval')
        na_supported=component=='NOT_APPLICABLE' and not component_conflict and not explicit_components
        check(10,'NOT APPLICABLE' if na_supported else 'NOT VERIFIED',
            'Engineer recorded not applicable: '+a.get('component_evidence','') if na_supported else 'Applicable component supplier / 9CAT approval evidence is pending. A free-text assertion cannot verify current component approval.',
            'NONE' if na_supported else 'INSUFFICIENT DATA',sources=[f['source'] for f in component_fs],field='component_approval')
        api610=any(f['field']=='standard' and f['status']!='REJECTED' and re.search(r'API\s*610',str(f['normalized_value'] or f['raw_value']),re.I) for f in fs)
        api610=api610 or any(r.data['tag']==tag and re.search(r'API\s*610',r.data['code'],re.I) and r.data['disposition']=='APPLICABLE' for r in rows(db,p.tenant_id,'standard_review',p.id))
        omega_deviation=bool(series and series['name'].casefold()=='omega' and api610)
        if omega_deviation:
            check(11,'REQUIRES ENGINEERING REVIEW','Omega: owner-supplied portfolio describes BB1 with deviations from API 610. Obtain configuration-specific deviation review and customer acceptance. Full API 610 compliance is not established.',c['policy']['unresolved_design_deviation'],field='api_610_deviations')
        impact='INSUFFICIENT DATA' if any(x['decision_impact']=='INSUFFICIENT DATA' for x in check_rows) else 'CONDITIONAL GO' if any(x['decision_impact']=='CONDITIONAL GO' for x in check_rows) else 'NONE'
        results.append(dict(rfq_id=p.id,equipment_tag_id=tag,customer_id=profile['customer_key'],product_category=category,
            required_9com=required,required_9com_status='CONFLICTING_OR_UNREVIEWED' if code_conflict else 'EXTRACTED_AND_REVIEWED' if required else 'NOT_SPECIFIED',
            product_series=series,product_series_id=series['id'] if series else None,candidate_suggestions=suggestions,
            matched_9com=required if mapped or parts_only else None,suggested_9com=suggested_codes,suggestion_label='INFERRED CANDIDATE — NOT A CUSTOMER REQUIREMENT',
            vendor_code=profile['vendor_code'],relevant_plant_id=profile['plant_id'],**identifier_values,
            historical_approval_evidence=commodity,historical_listing='LISTED_IN_OWNER_SUPPLIED_HISTORICAL_DATA_ATTACHMENT_PENDING' if original_listing else 'NOT_LISTED_IN_AVAILABLE_HISTORICAL_EVIDENCE_OR_UNKNOWN',
            current_approval_verification=current,technical_compliance_status='EVALUATED SEPARATELY — NOT CERTIFIED',
            supporting_references=relevant_sources,mapping=mapped,assignment=a or None,decision_impact=impact,
            required_action='Verify source attachments, current customer approval and item-specific engineering requirements before relying on preliminary eligibility.',
            omega_api610_deviation=omega_deviation,checks=check_rows))
    return dict(applicable=True,status='EVIDENCE_REVIEW_REQUIRED',profile=profile,assessments=results,
        policy=c['policy'],registry_hash=registry_hash(db,p.tenant_id),evaluated_at_date=date.today().isoformat(),
        notice='Historical records were supplied as structured text; the named PDF/PPTX attachments are pending. Approval matching never establishes technical compliance or commercial attractiveness.')

def design_references(db,p):
    if not applicable(p):return []
    report=assessments(db,p);references=[]
    for item in report['assessments']:
        series=item['product_series']
        if not series:continue
        for code in series['design_standards']:
            references.append(dict(tag=item['equipment_tag_id'],code=code,edition=None,explicit=False,
                reason=f"{series['name']} portfolio design reference supplied by owner; not contractual applicability or certification. "+series.get('engineering_notes',''),
                availability='DESIGN REFERENCE ONLY — SOURCE PRESENTATION PENDING',product_series_id=series['id'],mapping=item['mapping']))
    return references
