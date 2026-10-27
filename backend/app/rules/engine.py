"""Demo screening policy, never a KSB capability claim or hydraulic selection."""
import hashlib, json, math
from pydantic import BaseModel, ConfigDict
from typing import Literal

def digest(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
class Rule(BaseModel):
    model_config=ConfigDict(extra='forbid')
    criterion_id: str
    field: str
    operator: Literal['range','enum_in','coverage']
    minimum: float | None=None
    maximum: float | None=None
    allowed_values: list[str]=[]
    status: Literal['APPROVED','DRAFT']='APPROVED'
    version: int=1
    authority: str='Synthetic screening contract v1; not KSB data'
    synthetic_only: bool=True
    waiver_policy: Literal['NON_WAIVABLE','WAIVABLE']='NON_WAIVABLE'
    scope: Literal['tag','candidate']='tag'
    def valid(self):
        return self.operator!='range' or self.minimum is not None or self.maximum is not None
# Positive support is required against an intentionally tiny fictional training scope.
RULES=[Rule(criterion_id='D01',field='flow',operator='range',minimum=.001,maximum=.1),
 Rule(criterion_id='D02',field='head',operator='range',minimum=1,maximum=100),
 Rule(criterion_id='D03',field='liquid',operator='enum_in',allowed_values=['demo-water']),
 Rule(criterion_id='D04',field='material',operator='enum_in',allowed_values=['demo-alloy']),
 Rule(criterion_id='D05',field='approval',operator='enum_in',allowed_values=['demo-approved']),
 Rule(criterion_id='D06',field='npsh_basis',operator='enum_in',allowed_values=['demo-datum']),
 Rule(criterion_id='D07',field='prohibition',operator='enum_in',allowed_values=['none']),
 Rule(criterion_id='D08',field='action',operator='enum_in',allowed_values=['none'],waiver_policy='WAIVABLE')]
PACK=[r.model_dump() for r in RULES]
PACK_HASH=digest(PACK)

def rollup(outcomes):
    return next((s for s in ['NO-GO','INSUFFICIENT DATA','CONDITIONAL GO','GO'] if s in outcomes),'INSUFFICIENT DATA')

def evaluate_tag(tag, facts, coverage=True, synthetic=True, rules=RULES):
    results=[]; hard=False; unknown=not coverage; conditional=False
    for rule in rules:
        fs=[f for f in facts if f['tag']==tag and f['field']==rule.field and f['status']!='REJECTED']
        accepted=[f for f in fs if f['status']=='ACCEPTED']
        values={json.dumps(f['normalized_value'],sort_keys=True) for f in accepted}
        result='UNKNOWN'; reason='Missing or unreviewed requirement'; impact='INSUFFICIENT DATA'
        if not synthetic or not rule.synthetic_only: reason='No approved live engineering rules/capability coverage'
        elif rule.status!='APPROVED' or not rule.valid(): reason='Required rule draft or invalid'
        elif len(values)>1: reason='Conflicting accepted requirements; reject superseded evidence with justification'
        elif len(accepted)!=len(fs) or not accepted: reason='Engineer review required or missing requirement'
        elif accepted[0]['normalized_value'] is None: reason='Normalization unresolved'
        else:
            value=accepted[0]['normalized_value']
            ok=(rule.minimum is None or value>=rule.minimum) and (rule.maximum is None or value<=rule.maximum) if rule.operator=='range' else value in rule.allowed_values
            if ok: result='PASS'; reason='Positively supported within fictional demo scope'; impact='NONE'
            else:
                result='FAIL'; reason='Outside fictional demo screening contract'
                if rule.scope=='tag' and rule.field=='prohibition' and value=='confirmed-demo-ban':
                    hard=True; impact='NO-GO'; reason='Engineer-reviewed explicit synthetic project prohibition'
                elif rule.waiver_policy=='WAIVABLE': conditional=True; impact='CONDITIONAL GO'
                else: unknown=True; reason+='; no complete approved portfolio scope — clarify alternatives'
        if result=='UNKNOWN': unknown=True
        results.append(dict(criterion_id=rule.criterion_id,field=rule.field,result=result,reason=reason,decision_impact=impact,
            fact_ids=[f['id'] for f in fs],rule_version=rule.version,rule_hash=digest(rule.model_dump()),
            authority=rule.authority,capability_evidence='Fictional demonstration scope v1 only' if synthetic else None,
            waiver_policy=rule.waiver_policy,scope=rule.scope,
            clarification=None if result=='PASS' else 'Engineer: resolve '+rule.field+' with cited evidence before real use.'))
    if not coverage: results.append(dict(criterion_id='COVERAGE',result='UNKNOWN',reason='Missing, failed, unreadable or unmapped document coverage',decision_impact='INSUFFICIENT DATA'))
    outcome='NO-GO' if hard else 'INSUFFICIENT DATA' if unknown or not results else 'CONDITIONAL GO' if conditional else 'GO'
    return dict(tag=tag,outcome=outcome,results=results,hydraulic_selection='UNVERIFIED — no approved curves',coverage_complete=coverage)

def power(q_m3h, head_m, density, efficiency):
    if not all(math.isfinite(x) for x in (q_m3h,head_m,density,efficiency)): raise ValueError('Finite inputs required')
    if q_m3h<0 or head_m<0 or density<=0 or not 0<efficiency<=1: raise ValueError('Invalid physical inputs')
    hydraulic=density*9.80665*(q_m3h/3600)*head_m
    return {'hydraulic_kw':hydraulic/1000,'shaft_kw':hydraulic/efficiency/1000}

def pressure_head(pressure_pa, density, basis):
    if not all(math.isfinite(x) for x in (pressure_pa,density)): raise ValueError('Finite inputs required')
    if density<=0 or basis not in ('gauge','absolute'): raise ValueError('Density and explicit pressure basis required')
    return pressure_pa/(density*9.80665)
