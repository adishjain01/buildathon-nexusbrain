const $=id=>document.getElementById(id), esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']; let state,pending,busy=false,clarification="";
async function api(path,data){const r=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data||{})});const x=await r.json();if(!r.ok){const error=new Error(x.error||'Request failed.');error.needsClarification=!!x.needs_clarification;throw error;}return x}
function message(kind,html){const div=document.createElement('div');div.className='message '+kind;div.innerHTML=html;$('chat').append(div);div.scrollIntoView({behavior:'smooth',block:'nearest'});return div}
function updateScenario(){
  const s=document.querySelector('input[name="scenario"]:checked')?.value||'normal';
  const banner=$('scenario-banner');
  if(!banner)return;
  banner.className='scenario-banner '+s;
  if(s==='injection'){
    $('scenario-title').textContent='Prompt Injection Active';
    $('scenario-desc').innerHTML='⚠️ <b>Simulated malicious note:</b> asks the agent to cancel a different meeting. The gateway checks any attempted action.';
  }else if(s==='conflict'){
    $('scenario-title').textContent='Calendar Conflict Active';
    $('scenario-desc').innerHTML='⚠️ <b>Simulated slot collision:</b> The requested slot will temporarily report occupied. Gateway blocks collision before retry.';
  }else{
    $('scenario-title').textContent='Normal Task Active';
    $('scenario-desc').innerHTML='Standard mode: agent operates strictly within user-approved permission.';
  }
}
function renderTrace(result,scenario,mode){
  const entries=Array.isArray(result)?result:(result.results||[]);
  let allowed=entries.filter(x=>x.allowed).length;
  let blocked=entries.filter(x=>!x.allowed).length;
  let sTitle=scenario==='injection'?'PROMPT INJECTION DEFENSE':scenario==='conflict'?'CONFLICT DEFENSE':'NORMAL EXECUTION';
  let html=`<div class="trace-card"><div class="trace-header"><div class="trace-title"><span class="shield-icon">🛡️</span><div><b>Intent Lock Gateway Report</b><small>${esc(mode.toUpperCase())} AGENT · ${sTitle}</small></div></div><div class="trace-counts">${blocked>0?`<span class="badge-blocked">${blocked} BLOCKED</span>`:''}${allowed>0?`<span class="badge-allowed">${allowed} ALLOWED</span>`:''}</div></div>`;
  if(scenario==='injection'){
    const cancelled=entries.find(e=>!e.allowed&&e.action?.type==='cancel');
    html+=`<div class="trace-alert injection"><b>⚠️ Simulated prompt injection</b><small>${cancelled?'The agent attempted an unauthorized cancellation; the gateway blocked it.':'The scenario included a malicious instruction. No blocked cancellation was recorded in this run.'}</small></div>`;
  }else if(scenario==='conflict'){
    const collision=entries.some(e=>!e.allowed&&String(e.reason||'').includes('Simulated conflict'));
    html+=`<div class="trace-alert conflict"><b>⚠️ Simulated calendar conflict</b><small>${collision?(allowed?'A simulated conflict was blocked, and a later action was allowed.':'A simulated conflict was blocked; no later action succeeded.'):'No simulated conflict was recorded in this run.'}</small></div>`;
  }
  html+=`<div class="trace-steps">`;
  entries.forEach((e,i)=>{
    let a=e.action||{};
    let actType=esc(a.type||'unknown').replaceAll('_',' ');
    let details=[];
    if(a.meeting_id)details.push(`meeting: ${esc(a.meeting_id)}`);
    if(a.attendee)details.push(`attendee: ${esc(a.attendee)}`);
    if(a.date||a.time)details.push(`slot: ${esc(a.date||'')} ${esc(a.time||'')}`);
    html+=`<div class="trace-step ${e.allowed?'allowed':'blocked'}"><span class="step-icon">${e.allowed?'✓':'✕'}</span><div class="step-body"><div class="step-head"><b>Attempt ${i+1}: ${actType.toUpperCase()}</b><span class="step-status">${e.allowed?'ALLOWED':'BLOCKED'}</span></div><div class="step-meta">${esc(details.join(' · ')||'action')}</div><div class="step-reason">${esc(e.reason)}</div></div></div>`;
  });
  html+=`</div>`;
  let outcome=entries.length===0?'No gateway actions were recorded in this run.':allowed>0?'The gateway allowed an action. Review the decisions above.':'No action was allowed. Review the decisions above.';
  html+=`<div class="trace-footer">${outcome}</div></div>`;
  return html;
}
async function refresh(){const response=await fetch('/api/state');if(!response.ok)throw Error('Could not read calendar state.');state=await response.json();
 $('meetings').innerHTML=state.meetings.map(m=>`<div class="meeting"><span class="dot"></span><div><b>${esc(m.title)}</b><small>${esc(m.date)} · ${esc(m.time)} · ${esc(m.duration)} min</small><small>WITH ${esc(m.attendees.filter(x=>x!=='you').join(', '))}</small></div></div>`).join('');
 const p=state.policy;$('lock-status').textContent=!p?'NO LOCK':p.used?'USED':new Date(p.expires_at)<=new Date()?'EXPIRED':'ACTIVE';
 $('audit').className=state.audit.length?'audit':'audit-empty';$('audit').innerHTML=state.audit.length?state.audit.map(a=>`<div class="audit-item"><span class="${a.allowed?'allow':'deny'}">${a.allowed?'✓':'×'}</span><div><b>${a.allowed?'ALLOWED':'BLOCKED'} · ${esc(a.action.type||'unknown').replaceAll('_',' ')}</b><small>${esc(a.reason)}</small><small>${esc(a.action.meeting_id||'')} ${esc(a.action.attendee||'')} ${esc(a.action.date||'')} ${esc(a.action.time||'')}</small></div></div>`).join(''):'Action decisions will appear here.';
 $('agent-config').textContent=state.hosted_demo?'Hosted scripted demo. Each browser has a temporary session; it may reset on a cold start.':'Scripted mode is ready.';$('agent-mode').options[1].disabled=!state.openrouter_configured;if(!state.openrouter_configured)$('agent-mode').value='scripted';updateScenario();}
function description(p){const m=state.meetings.find(x=>x.id===p.meeting_id);if(!m)return 'Unknown meeting';let who=esc(m.title)+' with '+esc(m.attendees.filter(x=>x!=='you').join(', '));if(p.type==='add_attendee')return `Add <b>${esc(p.attendee)}</b> to <b>${who}</b>. Keep the meeting time unchanged.`;return `Reschedule <b>${who}</b> once to <b>${esc(p.start_date)} at ${esc(p.earliest)}</b>. Keep attendees and other details unchanged.`}
$('task-form').onsubmit=async e=>{e.preventDefault();if(busy)return;let input=$('task').value.trim();if(!input)return;let text=input;if(clarification&&!/\b(reschedule|move|add)\b/i.test(input)){text=/^(?:please )?add\s+to\s/i.test(clarification)?clarification.replace(/\badd\s+to\s/i,()=>`add ${input} to `):clarification+' '+input;}message('user',esc(input));$('task').value='';pending=null;busy=true;$('send').disabled=true;let thinking=message('assistant',`<span class="avatar">◈</span><div class="bubble">Interpreting your task…</div>`);try{await refresh();pending=await api('interpret',{text,mode:$('agent-mode').value});clarification='';thinking.remove();const card=message('assistant',`<span class="avatar">◈</span><div class="bubble"><b>Review this permission</b><p>${description(pending)}</p><div class="review-note">${pending._source==='local_fallback'?'OpenRouter was unavailable or returned an invalid response. The local interpreter understood this request; the scripted agent will run. ':''}Check the entire request against this permission. Unsupported or omitted actions are not authorized. One action · 15-minute expiry · mock calendar only</div><div class="review-actions"><button class="approve">Approve & run agent →</button><button class="dismiss">Cancel</button></div></div>`);const candidate=pending;card.querySelector('.dismiss').onclick=()=>{if(pending===candidate)pending=null;card.remove()};card.querySelector('.approve').onclick=async()=>{if(pending!==candidate){message('assistant','<span class="avatar">◈</span><div class="bubble">This review is no longer current. Submit your task again.</div>');return}busy=true;card.querySelector('.approve').disabled=true;card.querySelector('.dismiss').disabled=true;try{await api('approve',candidate);pending=null;await refresh();let scenario=document.querySelector('input[name="scenario"]:checked').value,mode=candidate._source==='local_fallback'?'scripted':$('agent-mode').value;let progress=message('assistant',`<span class="avatar">◈</span><div class="bubble">Running ${esc(mode)} agent · ${esc(scenario)} scenario…</div>`);let result=await api('agent',{mode,scenario});await refresh();progress.querySelector('.bubble').innerHTML=renderTrace(result,scenario,mode)}catch(err){await refresh();message('assistant',`<span class="avatar">◈</span><div class="bubble">${esc(err.message)} Check gateway activity before retrying.</div>`)}finally{busy=false}}}catch(err){thinking.remove();clarification=err.needsClarification?text:'';message('assistant',`<span class="avatar">◈</span><div class="bubble">${esc(err.message)}</div>`)}finally{busy=false;$('send').disabled=false}};
document.querySelectorAll('.example').forEach(b=>b.onclick=()=>{
  $('task').value=b.dataset.text;
  if(b.dataset.scenario){
    let r=document.querySelector(`input[name="scenario"][value="${b.dataset.scenario}"]`);
    if(r){r.checked=true;updateScenario();}
  }
  $('task').focus();
});
document.querySelectorAll('input[name="scenario"]').forEach(r=>r.onchange=updateScenario);
$('settings-toggle').onclick=()=>{$('settings-panel').hidden=!$('settings-panel').hidden};$('settings-close').onclick=()=>{$('settings-panel').hidden=true};
$('save-key').onclick=async()=>{const key=$('api-key').value.trim();if(!key)return;try{await api('key',{key});$('api-key').value='';await refresh();$('agent-mode').value='openrouter';$('agent-config').textContent='Key saved for this session. Model mode sends mock data to OpenRouter.'}catch(e){$('api-key').value='';$('agent-config').textContent=e.message}};
$('clear-key').onclick=async()=>{await api('key',{key:''});$('api-key').value='';await refresh()};
$('reset').onclick=async()=>{if(busy)return;await api('reset');pending=null;clarification='';$('chat').innerHTML='';$('task').value='';await refresh()};
refresh().catch(e=>message('assistant',`<span class="avatar">◈</span><div class="bubble">${esc(e.message)}</div>`));
