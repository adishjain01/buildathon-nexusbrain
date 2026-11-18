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
 const p=state.policy, active=p&&!p.used&&new Date(p.expires_at)>new Date(); $('policy-status').textContent=active?'● LOCK ACTIVE':p&&p.used?'LOCK USED':'NO ACTIVE LOCK'; $('policy-status').className='tag '+(active?'active':'muted'); $('run').disabled=!active;
 $('audit').innerHTML=state.audit.length?state.audit.map(a=>`<div class="entry"><div class="decision ${a.allowed?'allow':'deny'}">${a.allowed?'✓':'×'}</div><div><b>${a.allowed?'ALLOWED':'BLOCKED'} <span>${esc(a.action.type||'unknown').replaceAll('_',' ')}</span></b><p>${esc(a.reason)}</p><small>${esc(a.action.meeting_id||'')} ${esc(a.action.date||'')} ${esc(a.action.time||'')} · ${esc(a.at)}</small></div></div>`).join(''):'<div class="empty">No actions yet.<br><small>Gateway decisions will appear here.</small></div>';
}
function form(){return {meeting_id:$('meeting').value,start_date:$('start').value,end_date:$('end').value,earliest:$('earliest').value,latest:$('latest').value,days:[...document.querySelectorAll('#days input:checked')].map(x=>Number(x.value))}}
$('review').onclick=()=>{const p=form(), m=state.meetings.find(x=>x.id===p.meeting_id); if(!m||!p.start_date||!p.end_date||p.end_date<p.start_date||!p.earliest||!p.latest||p.earliest>p.latest||!p.days.length){toast('Complete a valid permission first.');return} pending=p; $('summary').innerHTML=`<b>${esc(m.title)} · ${esc(m.attendees.join(', '))}</b><p>Move once from ${esc(p.start_date)} through ${esc(p.end_date)}, on ${p.days.map(d=>names[d]).join(', ')}, with a start time between ${esc(p.earliest)} and ${esc(p.latest)}. Preserve all other details.</p>`; $('preview').hidden=false; $('preview').scrollIntoView({behavior:'smooth',block:'nearest'});};
document.querySelector('.permission').addEventListener('change',e=>{if(e.target.matches('input,select')){$('preview').hidden=true; pending=null}});
$('approve').onclick=async()=>{try{await api('approve',pending); $('preview').hidden=true; pending=null; await refresh();toast('Permission activated for 15 minutes.')}catch(e){toast(e.message)}};
$('run').onclick=async()=>{try{await api('agent');await refresh();toast('Demo agent finished. Inspect the decision trail.')}catch(e){toast(e.message)}};
$('test').onclick=async()=>{try{let type=$('action').value, a={type,meeting_id:$('target').value};if(type==='reschedule')Object.assign(a,{date:$('action-date').value,time:$('action-time').value});if(type==='add_attendee')a.attendee='Mallory';let result=await api('action',a);await refresh();toast((result.allowed?'Allowed: ':'Blocked: ')+result.reason)}catch(e){toast(e.message)}};
$('reset').onclick=async()=>{await api('reset');$('preview').hidden=true;pending=null;await refresh();toast('Demo reset. All permissions revoked.')};
refresh().catch(e=>toast(e.message));
