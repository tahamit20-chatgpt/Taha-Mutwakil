export type Identity={user:string;tenant:string;role:string;csrf:string;demo:boolean;permissions?:string[]};
export type Fact={id:string;tag:string;field:string;raw_value:string;raw_unit:string;reviewed_value?:string;reviewed_unit?:string;normalized_value:string|number|null;normalized_unit:string;status:string;lock_version:number;warnings:string[];method:string;source:{document_version_id:string;page:number|null;line_start:number;quote:string;worksheet?:string;cell?:string;paragraph?:number}};
export type Finding={criterion_id:string;field?:string;result:string;reason:string;decision_impact:string;clarification?:string;fact_ids?:string[];authority?:string;capability_evidence?:string;rule_hash?:string;compliance_status?:string;product_category?:string;severity?:string;requirement_evidence?:Fact["source"][];rule_version?:number;standard_reference?:string;standard_edition?:string;clause_reference?:string;required_condition?:unknown;approval_status?:string};
export type Snapshot={outcome:string;project_version:number;run_hash:string;tags:{tag:string;outcome:string;results:Finding[];hydraulic_selection:string}[]};
export type Run={id:string;created_at:string;snapshot:Snapshot;is_stale?:boolean};
export type Project={id:string;name:string;tags:string[];lock_version:number;commercial:string;classification?:Classification;equipment?:Equipment[];workflow_version?:string;latest_outcome?:string;last_updated?:string;workflow_stage?:string;created_at?:string;document:{id:string;filename:string;state:string;gaps:string[];sha256:string;scan:string;lock_version:number;revision?:string;version:number;revision_of?:string;document_number?:string;category?:string;category_status?:string}[];page:{id:string;document_id:string;index:number;text:string;source_kind?:string}[];fact:Fact[];evaluation:Run[];jobs:{id:string;state:string;stage:string;error:string|null;attempt:number}[];adjudication:{id:string;actor:string;reason:string;evidence:string;disposition:string}[];review:{id:string;reason:string;actor:string}[];audit:{id:string;action:string;created_at:string}[]};
let csrf='';
export function setCsrf(value:string){csrf=value}
export async function api<T>(path:string,method='GET',body?:unknown):Promise<T>{
 const headers:Record<string,string>={'X-CSRF-Token':csrf};
 if(body instanceof FormData) headers['Idempotency-Key']=crypto.randomUUID();
 else if(body!==undefined)headers['Content-Type']='application/json';
 const res=await fetch('/api/v1'+path,{method,headers,body:body instanceof FormData?body:body!==undefined?JSON.stringify(body):undefined});
 if(!res.ok){const e=await res.json().catch(()=>({detail:'Request failed'}));throw new Error(typeof e.detail==='string'?e.detail:JSON.stringify(e.detail))}
 return res.json();
}
export async function login(name:string):Promise<Identity>{
 const r=await fetch('/api/v1/auth/demo/'+name,{method:'POST',headers:{'X-BidFit-Demo':'local'}});
 if(!r.ok)throw new Error('Demo login is available only in local synthetic mode');
 return r.json();
}
export type Classification={product_category:string;market_area:string;application:string;customer_profile:string;customer:string;end_user:string;contractor:string;location:string;country:string;rfq_reference:string;submission_deadline:string|null;assigned_engineer:string};
export type Equipment={tag:string;product_category:string;description:string;quantity:number|null};
export type Master={id:string;lock_version:number;version:number;product_categories:string[];markets:Record<string,string[]>;customers:string[];document_categories:string[];required_fields:Record<string,string[]>;field_contract:Record<string,{numeric:boolean;unit:string}>};
export type Summary={classification:Classification|null;equipment:(Equipment&{fields:Record<string,Fact[]>})[];documents:Project['document'];missing:{tag:string;field:string;reason:string}[];conflicts:{tag:string;field:string;fact_ids:string[];reason:string}[];coverage_gaps:{document_id:string;filename:string;gaps:string[]}[];unreviewed_count:number;notes:string;summary_hash:string;reviewed:boolean;method:string};
export type Reference={tag:string;code:string;edition:string|null;explicit:boolean;source?:Fact['source'];fact_id?:string;reason?:string;availability:string;review?:{disposition:string;reason:string};approved_rule_ids?:string[]};
export type Standards={suggested:Reference[];explicit:Reference[];notice:string};
export type Family={id:string;name:string;product_category:string;source_reference:string;source_revision:string;approval_status:string};
export type Candidate={id:string;tag:string;model_reference:string;family_snapshot:Family;status:string;engineering_review:string;evidence_reference:string;inputs_stale?:boolean;reference_reviews?:{id:string;disposition:string;actor:string;reason:string}[]};
export type Price={id:string;tag:string;price_kind:string;amount:number|null;currency:string;valid_until:string;source_reference:string;approval_status:string};
export type Quote={id:string;snapshot:{project_name:string;status:string;version:number;content_hash:string}};
export type Studios={inputs:Summary['equipment'];candidates:Candidate[];prices:Price[];quotations:Quote[];templates:{id:string;name:string;version:number}[];selection_status:string;icap_status:string;easyselect_status:string};
export type RuleRecord={id:string;criterion_id:string;name:string;field:string;operator:string;product_category:string;minimum:number|null;maximum:number|null;allowed_values:string[];units:string;severity:string;approval_status:string;version:number;source_reference:string;content_hash:string;approved_by:string|null;namespace:string};
