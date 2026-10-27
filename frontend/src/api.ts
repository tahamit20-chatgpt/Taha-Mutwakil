export type Identity={user:string;tenant:string;role:string;csrf:string;demo:boolean};
export type Fact={id:string;tag:string;field:string;raw_value:string;raw_unit:string;reviewed_value?:string;reviewed_unit?:string;normalized_value:string|number|null;normalized_unit:string;status:string;lock_version:number;warnings:string[];method:string;source:{document_version_id:string;page:number|null;line_start:number;quote:string}};
export type Finding={criterion_id:string;field?:string;result:string;reason:string;decision_impact:string;clarification?:string;fact_ids?:string[];authority?:string;capability_evidence?:string;rule_hash?:string};
export type Snapshot={outcome:string;project_version:number;run_hash:string;tags:{tag:string;outcome:string;results:Finding[];hydraulic_selection:string}[]};
export type Run={id:string;created_at:string;snapshot:Snapshot};
export type Project={id:string;name:string;tags:string[];lock_version:number;commercial:string;document:{id:string;filename:string;state:string;gaps:string[];sha256:string;scan:string}[];page:{id:string;document_id:string;index:number;text:string}[];fact:Fact[];evaluation:Run[];jobs:{id:string;state:string;stage:string;error:string|null;attempt:number}[];adjudication:{id:string;actor:string;reason:string;evidence:string;disposition:string}[];review:{id:string;reason:string;actor:string}[];audit:{id:string;action:string;created_at:string}[]};
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
