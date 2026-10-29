import csv, io, json, html

def render(snapshot, fmt):
    if fmt=='json': return json.dumps(snapshot,sort_keys=True,indent=2), 'application/json'
    if fmt=='html':
        def esc(value): return html.escape(str(value))
        sections=[]
        for tag in snapshot['tags']:
            rows=''.join('<tr><td>'+esc(r['criterion_id'])+'</td><td>'+esc(r.get('compliance_status',r['result']))+'</td><td>'+esc(r['reason'])+'<br><small>'+esc(r.get('clarification') or '')+'</small></td><td>'+esc(r.get('authority',''))+'<br>'+esc(r.get('capability_evidence',''))+'</td></tr>' for r in tag['results'])
            sections.append('<h2>'+esc(tag['tag'])+' · '+esc(tag['outcome'])+'</h2><p>'+esc(tag['hydraulic_selection'])+'</p><table><tr><th>Criterion</th><th>Result</th><th>Reason / action</th><th>Rule / capability authority</th></tr>'+rows+'</table>')
        context=''
        if snapshot.get('classification'):
            context='<h2>RFQ classification</h2><p>'+esc(json.dumps(snapshot['classification'],sort_keys=True))+'</p><p>Summary review: '+('reviewed' if snapshot.get('summary',{}).get('reviewed') else 'not reviewed')+'</p>'
        if snapshot.get('customer_approvals'):
            approvals=snapshot['customer_approvals']
            context+='<h2>Saudi Aramco approval evidence</h2><p>'+esc(approvals['notice'])+'</p>'
            context+='<table><tr><th>Equipment / candidate</th><th>Required / matched 9COM</th><th>Historical vendor / plant</th><th>Historical evidence / current verification</th></tr>'
            for a in approvals['assessments']:
                product=a.get('product_series') or {}
                context+='<tr><td>'+esc(a['equipment_tag_id'])+' / '+esc(product.get('name','Not selected'))+'</td><td>'+esc(a['required_9com'] or 'Not specified')+' / '+esc(a['matched_9com'] or 'Unknown')+'</td><td>'+esc(a['vendor_code'])+' / '+esc(a['relevant_plant_id'])+'</td><td>'+esc(a['historical_listing'])+'<br>'+esc(a['current_approval_verification']['status'])+'<br>'+esc(a['current_approval_verification']['reason'])+'</td></tr>'
            context+='</table><p>Technical compliance is evaluated separately. Registry hash: '+esc(snapshot['approval_registry_hash'])+'</p>'
        fact_rows=''.join('<tr><td>'+esc(f['tag'])+'<br>'+esc(f['field'])+'</td><td>'+esc(f['raw_value'])+' '+esc(f['raw_unit'])+'</td><td>'+esc(f['normalized_value'])+' '+esc(f['normalized_unit'])+'<br>'+esc(f['status'])+'</td><td>'+esc(f['source']['document_version_id'])+'<br>Source '+esc(f['source'].get('worksheet') or f['source'].get('paragraph') or f['source']['page'] or 'TXT')+' / line '+esc(f['source']['line_start'])+'<br>'+esc(f['source']['quote'])+'</td></tr>' for f in snapshot['facts'])
        report='<!doctype html><html><head><meta charset="utf-8"><title>BidFit preliminary report</title><style>body{font:14px system-ui;max-width:1100px;margin:40px auto;color:#18323d}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:11px}h1,h2{color:#0f4c5c}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border:1px solid #dae4e9;padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#eef4f6}small{color:#687b85}@media print{body{margin:0}details{display:block}}</style></head><body><h1>BidFit · Preliminary synthetic screening</h1><p>DEMONSTRATION ONLY — not validated engineering conclusions; no KSB capability data.</p><h2>'+esc(snapshot['project_name'])+' · '+esc(snapshot['outcome'])+'</h2><p>Complete-package scope · Evidence revision '+esc(snapshot['project_version'])+'</p><p>Run hash: '+esc(snapshot['run_hash'])+'</p>'+context+''.join(sections)+'<h2>Requirement evidence</h2><table><tr><th>Tag / field</th><th>Original</th><th>Reviewed SI / status</th><th>Source</th></tr>'+fact_rows+'</table><h2>Frozen audit payload</h2><p>Includes document hashes, human fact reviews, assumptions, versions and rule content. Later dispositions are in project History and cannot change this report.</p><pre>'+esc(json.dumps(snapshot,sort_keys=True,indent=2))+'</pre></body></html>'
        return report,'text/html'
    if fmt=='csv':
        out=io.StringIO(); writer=csv.writer(out)
        writer.writerow(['run_hash','outcome','tag','criterion','result','reason','frozen_snapshot_json'])
        def safe(v):
            v=str(v)
            return "'"+v if v.lstrip().startswith(('=','+','-','@','\t','\r')) else v
        for tag in snapshot['tags']:
            for result in tag['results']:
                writer.writerow([safe(v) for v in [snapshot['run_hash'],snapshot['outcome'],tag['tag'],result['criterion_id'],result['result'],result['reason'],json.dumps(snapshot,sort_keys=True)]])
        return out.getvalue(),'text/csv'
    raise ValueError('Unsupported export format')
