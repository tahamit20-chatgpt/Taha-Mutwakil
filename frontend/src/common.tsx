import React,{useEffect,useState} from 'react';
import {Fact} from './api';
export function Badge({value}:{value:string}){return <span className={'badge '+value.toLowerCase().replaceAll(' ','-')}>{value}</span>}
export function sourceLabel(s:Fact['source']){return `${s.worksheet?`Worksheet ${s.worksheet} · ${s.cell}`:s.paragraph?`Paragraph ${s.paragraph}`:s.page?`Physical page ${s.page}`:'TXT'} · line ${s.line_start}`}
export function Brand(){
 const [available,setAvailable]=useState(false),[revision,setRevision]=useState(0);
 useEffect(()=>{const load=()=>fetch('/api/v1/branding/status').then(r=>r.json()).then(s=>{setAvailable(s.configured);setRevision(Date.now())}).catch(()=>setAvailable(false));void load();window.addEventListener('bidfit-brand-updated',load);return()=>window.removeEventListener('bidfit-brand-updated',load)},[]);
 return <div className="branding">{available?<img className="official-logo" src={'/api/v1/branding/logo?v='+revision} alt="KSB Pumps Arabia official supplied logo"/>:<div className="company-name">KSB Arabia<small>Original logo file pending configuration</small></div>}<div className="product-brand">BidFit <span>2.0</span></div></div>
}
export function FactCard({fact,save}:{fact:Fact;save:(f:Fact,status:string,value:string,unit:string,reason:string)=>void}){
 const [value,setValue]=useState(fact.reviewed_value??fact.raw_value),[unit,setUnit]=useState(fact.reviewed_unit??fact.raw_unit),[reason,setReason]=useState('Verified against synthetic source');
 return <article className="fact"><div className="row"><strong>{fact.tag} · {fact.field.replaceAll('_',' ')}</strong><Badge value={fact.status}/></div><blockquote>{fact.source.quote}</blockquote><small>Document {fact.source.document_version_id.slice(0,8)} · {sourceLabel(fact.source)} · {fact.method}</small><div className="row inputs"><label>Value<input aria-label={fact.field+' value'} value={value} onChange={e=>setValue(e.target.value)}/></label><label>Unit<input aria-label={fact.field+' unit'} value={unit} onChange={e=>setUnit(e.target.value)}/></label></div><small>Normalized: {fact.normalized_value??'UNKNOWN'} {fact.normalized_unit} · revision {fact.lock_version}</small>{fact.warnings.map(w=><p className="warning" key={w}>{w}</p>)}<label>Review rationale<input value={reason} onChange={e=>setReason(e.target.value)}/></label><div className="row"><button onClick={()=>save(fact,'ACCEPTED',value,unit,reason)}>Accept / correct</button><button className="secondary" onClick={()=>save(fact,'REJECTED',value,unit,reason)}>Reject evidence</button></div></article>
}
export type Action=(fn:()=>Promise<void>)=>Promise<void>;
