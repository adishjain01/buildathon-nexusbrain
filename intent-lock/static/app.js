const $ = id => document.getElementById(id);
let state, pending;
const names = ['MON','TUE','WED','THU','FRI','SAT','SUN'];
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, data) { const r=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data||{})}); const x=await r.json(); if(!r.ok) throw Error(x.error); return x; }
function toast(s){$('toast').textContent=s; $('toast').classList.add('show'); setTimeout(()=>$('toast').classList.remove('show'),3500)}
function localDate(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
const today=new Date(), startDate=new Date(today); startDate.setDate(today.getDate()+1); const endDate=new Date(startDate); endDate.setDate(startDate.getDate()+6); $('start').value=localDate(startDate); $('end').value=localDate(endDate); $('action-date').value=localDate(startDate);
$('days').innerHTML=names.map((n,i)=>`<label class="day"><input type="checkbox" value="${i}" ${i<4?'checked':''}><span>${n}</span></label>`).join('');
async function refresh(){
 state=await (await fetch('/api/state')).json();
 for(const id of ['meeting','target']){const el=$(id), old=el.value; el.innerHTML=state.meetings.map(m=>`<option value="${esc(m.id)}">${esc(m.title)} · ${esc(m.attendees.filter(x=>x!=='you').join(', '))}</option>`).join(''); if(old) el.value=old;}
 $('meetings').innerHTML=state.meetings.map(m=>`<div class="meeting"><div class="meeting-dot"></div><div><b>${esc(m.title)}</b><p>${esc(m.date)} &nbsp;·&nbsp; ${esc(m.time)} &nbsp;·&nbsp; ${m.duration} min</p><small>WITH ${esc(m.attendees.filter(x=>x!=='you').join(', ').toUpperCase())}</small></div></div>`).join('');
 $('agent-config').textContent=state.openrouter_configured?'OpenRouter key detected. Selecting OpenRouter sends the mock calendar and permission to its provider.':'No OpenRouter key detected. Enter one below to enable model mode, or use scripted mode.'; $('agent-mode').options[1].disabled=!state.openrouter_configured; if(!state.openrouter_configured) $('agent-mode').value='scripted';
 const p=state.policy, active=p&&!p.used&&new Date(p.expires_at)>new Date(); $('policy-status').textContent=active?'● LOCK ACTIVE':p&&p.used?'LOCK USED':'NO ACTIVE LOCK'; $('policy-status').className='tag '+(active?'active':'muted'); $('run').disabled=!active;
 $('audit').innerHTML=state.audit.length?state.audit.map(a=>`<div class="entry"><div class="decision ${a.allowed?'allow':'deny'}">${a.allowed?'✓':'×'}</div><div><b>${a.allowed?'ALLOWED':'BLOCKED'} <span>${esc(a.action.type||'unknown').replaceAll('_',' ')}</span></b><p>${esc(a.reason)}</p><small>${esc(a.action.meeting_id||'')} ${esc(a.action.attendee||'')} ${esc(a.action.date||'')} ${esc(a.action.time||'')} · ${esc(a.at)}</small></div></div>`).join(''):'<div class="empty">No actions yet.<br><small>Gateway decisions will appear here.</small></div>';
}
function form(){if($('permission-type').value==='add_attendee')return {type:'add_attendee',meeting_id:$('meeting').value,attendee:$('permission-attendee').value.trim()};return {type:'reschedule',meeting_id:$('meeting').value,start_date:$('start').value,end_date:$('end').value,earliest:$('earliest').value,latest:$('latest').value,days:[...document.querySelectorAll('#days input:checked')].map(x=>Number(x.value))}}
// Parse the entire supported expression; unrecognized text never changes the form.
$('apply-constraint').onclick=()=>{
 const raw=$('constraint').value.trim().toLowerCase();
 const parts=raw.split(/\s+and\s+/); let earliest=$('earliest').value, latest=$('latest').value;
 const days=[...document.querySelectorAll('#days input')].map(x=>x.checked);
 const weekdays=['monday','tuesday','wednesday','thursday','friday','saturday','sunday'];
 try {
  if(!raw) throw Error('Enter a constraint first.');
  for(let part of parts){
   part=part.replace(/^only allow rescheduling\s+/, '').replace(/^only\s+/, '').trim();
   let m=part.match(/^never (?:on )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?$/);
   if(m){days[weekdays.indexOf(m[1])]=false;continue;}
   m=part.match(/^(after|before) (\d{1,2})(?::(\d{2}))?\s*(am|pm)$/);
   if(!m) throw Error('Unsupported constraint. Use “after 2 PM” or “never Friday”, joined with “and”.');
   let hour=Number(m[2]), min=Number(m[3]||0); if(hour<1||hour>12||min>59) throw Error('Enter a valid 12-hour time.');
   let value=(hour%12+(m[4]==='pm'?12:0))*60+min+(m[1]==='after'?1:-1);
   if(value<0||value>1439) throw Error('That time leaves no valid start time.');
   let time=String(Math.floor(value/60)).padStart(2,'0')+':'+String(value%60).padStart(2,'0');
   if(m[1]==='after') earliest=earliest>time?earliest:time; else latest=latest<time?latest:time;
  }
  if(!days.some(Boolean)||earliest>latest) throw Error('Those constraints leave no allowed days or times.');
  $('earliest').value=earliest; $('latest').value=latest; document.querySelectorAll('#days input').forEach((x,i)=>x.checked=days[i]);
  $('preview').hidden=true; pending=null; toast('Constraint applied. Review the exact permission below.');
 } catch(e){toast(e.message)}
};
$('permission-type').onchange=()=>{let add=$('permission-type').value==='add_attendee';$('schedule-controls').hidden=add;$('permission-attendee-wrap').hidden=!add;};
$('action').onchange=()=>{let kind=$('action').value;$('action-schedule').hidden=kind!=='reschedule';$('action-attendee-wrap').hidden=kind!=='add_attendee';};
$('review').onclick=()=>{const p=form(), m=state.meetings.find(x=>x.id===p.meeting_id); if(!m || (p.type==='add_attendee' ? !p.attendee : !p.start_date||!p.end_date||p.end_date<p.start_date||!p.earliest||!p.latest||p.earliest>p.latest||!p.days.length)){toast('Complete a valid permission first.');return} pending=p; const detail=p.type==='add_attendee'?`Add ${esc(p.attendee)} once. Keep the meeting time and all other details unchanged.`:`Move once from ${esc(p.start_date)} through ${esc(p.end_date)}, on ${p.days.map(d=>names[d]).join(', ')}, with a start time between ${esc(p.earliest)} and ${esc(p.latest)}. Preserve all other details.`; $('summary').innerHTML=`<b>${esc(m.title)} · ${esc(m.attendees.join(', '))}</b><p>${detail}</p>`; $('effect').textContent=p.type==='add_attendee'?'Known effect: add the named attendee to this mock meeting. No invitation is sent.':'Known effect: change the time of this mock meeting. No notifications are sent.'; $('preview').hidden=false; $('preview').scrollIntoView({behavior:'smooth',block:'nearest'});};
document.querySelector('.permission').addEventListener('input',e=>{if(e.target.matches('input,select')){$('preview').hidden=true; pending=null}});
$('approve').onclick=async()=>{try{await api('approve',pending); $('preview').hidden=true; pending=null; await refresh();toast('Permission activated for 15 minutes.')}catch(e){toast(e.message)}};
$('save-key').onclick=async()=>{const key=$('api-key').value.trim();if(!key){toast('Enter an OpenRouter key first.');return}try{await api('key',{key});$('api-key').value='';await refresh();$('agent-mode').value='openrouter';$('agent-mode').onchange();toast('Key stored for this server session.')}catch(e){$('api-key').value='';toast(e.message)}};
$('clear-key').onclick=async()=>{try{await api('key',{key:''});$('api-key').value='';await refresh();toast('Session key cleared.')}catch(e){toast(e.message)}};
$('agent-mode').onchange=()=>{$('agent-description').textContent=$('agent-mode').value==='openrouter'?'A free model proposes tool calls; the gateway checks every action. Mock calendar data is sent to OpenRouter.':'Scripted mode runs locally and produces a repeatable demonstration.'};
$('run').onclick=async()=>{const mode=$('agent-mode').value; $('run').disabled=true; $('agent-result').textContent=mode==='openrouter'?'Waiting for the model…':'Running scripted agent…'; try{const result=await api('agent',{mode});await refresh();$('agent-result').textContent=mode==='openrouter'?(result.message||'Model run finished.'):'Scripted run finished. Inspect the decision trail.';toast('Agent finished. Inspect the decision trail.')}catch(e){await refresh();$('agent-result').textContent='Run stopped: '+e.message+' Check the decision trail before retrying.';toast(e.message)}};
$('test').onclick=async()=>{try{let type=$('action').value, a={type,meeting_id:$('target').value};if(type==='reschedule')Object.assign(a,{date:$('action-date').value,time:$('action-time').value});if(type==='add_attendee')a.attendee=$('action-attendee').value.trim();let result=await api('action',a);await refresh();toast((result.allowed?'Allowed: ':'Blocked: ')+result.reason)}catch(e){toast(e.message)}};
$('reset').onclick=async()=>{await api('reset');$('preview').hidden=true;pending=null;await refresh();toast('Demo reset. All permissions revoked.')};
refresh().catch(e=>toast(e.message));
