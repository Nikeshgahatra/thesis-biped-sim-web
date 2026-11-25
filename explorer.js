const $=id=>document.getElementById(id);
const SRC={runs:'api/runs.json',params:'api/params.json',standing:'api/standing.json',foot_width:'api/foot_width.json',timeseries:'api/timeseries.json'};
const SCHEMA={runs:'gait, controller, environment, gravity, frequency_hz, fell, fall_time_s, observed_s, x_displacement_m, max_pitch_deg, max_roll_deg',
 params:'controller, name, value',standing:'environment, gravity, both_contact_pct, max_roll_deg, max_pitch_deg',foot_width:'foot_width_cm, environment, both_contact_pct, max_roll_deg',
 timeseries:'gait, controller, environment, time_s, x_m, height_m, pitch_deg, roll_deg, fall_flag'};
const cache={};let rows=[],cols=[],sortCol=null,sortDir=1;
async function load(t){
  if(cache[t])return cache[t];const d=await (await fetch(SRC[t])).json();
  if(t==='timeseries'){const out=[];Object.keys(d).forEach(k=>{const [g,c,e]=k.split('|');d[k].forEach(r=>out.push({gait:g,controller:c,environment:e,time_s:r[0],x_m:r[1],height_m:r[2],pitch_deg:r[3],roll_deg:r[4],fall_flag:r[5]}))});cache[t]=out}else cache[t]=d;
  return cache[t];
}
async function setTable(){
  const t=$('tbl').value;rows=await load(t);cols=Object.keys(rows[0]);sortCol=null;
  $('filters').innerHTML=cols.filter(c=>typeof rows[0][c]==='string'||c==='fell'||c==='fall_flag').map(c=>{const vals=[...new Set(rows.map(r=>r[c]))];return '<label>'+c+'<select data-c="'+c+'"><option value="">all</option>'+vals.map(v=>'<option>'+v+'</option>').join('')+'</select></label>'}).join('');
  [...$('filters').querySelectorAll('select')].forEach(s=>s.onchange=draw);
  $('schema').textContent='CREATE TABLE '+t+'('+SCHEMA[t]+');';draw();
}
function filtered(){
  const f={};[...$('filters').querySelectorAll('select')].forEach(s=>{if(s.value)f[s.dataset.c]=s.value});
  let r=rows.filter(x=>Object.keys(f).every(c=>String(x[c])===f[c]));
  const q=$('q').value.trim().toLowerCase();if(q)r=r.filter(x=>cols.some(c=>String(x[c]).toLowerCase().includes(q)));
  if(sortCol)r=[...r].sort((a,b)=>(a[sortCol]>b[sortCol]?1:a[sortCol]<b[sortCol]?-1:0)*sortDir);return r;
}
function draw(){
  const r=filtered(),t=$('tbl').value;
  const f=[...$('filters').querySelectorAll('select')].filter(s=>s.value).map(s=>s.dataset.c+" = '"+s.value+"'");
  $('sql').textContent='SELECT * FROM '+t+(f.length?'\nWHERE '+f.join('\n  AND '):'')+(sortCol?'\nORDER BY '+sortCol+(sortDir>0?' ASC':' DESC'):'')+';';
  $('count').textContent=r.length+' rows';
  const shown=r.slice(0,300);
  $('grid').innerHTML='<tr>'+cols.map(c=>'<th class="sort" data-c="'+c+'">'+c+(sortCol===c?(sortDir>0?' ▲':' ▼'):'')+'</th>').join('')+'</tr>'+shown.map(x=>'<tr>'+cols.map(c=>'<td>'+(x[c]===null?'<i>null</i>':typeof x[c]==='number'?+x[c].toPrecision(6):x[c])+'</td>').join('')+'</tr>').join('')+(r.length>300?'<tr><td colspan="'+cols.length+'">Showing the first 300 rows. Use the filters or download the CSV.</td></tr>':'');
  [...$('grid').querySelectorAll('th')].forEach(h=>h.onclick=()=>{const c=h.dataset.c;sortDir=sortCol===c?-sortDir:1;sortCol=c;draw()});
}
$('tbl').onchange=setTable;$('q').oninput=draw;
$('csv').onclick=()=>{const r=filtered(),lines=[cols.join(',')].concat(r.map(x=>cols.map(c=>x[c]===null?'':x[c]).join(',')));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/csv'}));a.download=$('tbl').value+'.csv';a.click()};
setTable();
