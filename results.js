fetch('api/runs.json').then(r=>r.json()).then(runs=>{
  const E=['Earth','Moon','Mars'],g=(gait,c,e)=>runs.find(r=>r.gait===gait&&r.controller===c&&r.environment===e);
  const F='#7c9cff',A='#38e0b4',F2='#ffb454',A2='#ff7a6b';
  barChart(document.getElementById('c1'),{labels:E,ylabel:'time before fall (s)',fmt:v=>v.toFixed(2),series:[
    {name:'Fixed',color:F,values:E.map(e=>g('first','Fixed',e).fall_time_s)},{name:'Adaptive',color:A,values:E.map(e=>g('first','Adaptive',e).fall_time_s)}]});
  barChart(document.getElementById('c2'),{labels:E,ylabel:'time survived (s)',fmt:v=>v.toFixed(1),series:[
    {name:'First gait, fixed',color:F2,values:E.map(e=>g('first','Fixed',e).observed_s)},{name:'First gait, adaptive',color:A2,values:E.map(e=>g('first','Adaptive',e).observed_s)},
    {name:'Tuned, fixed',color:F,values:E.map(e=>g('tuned','Fixed',e).observed_s)},{name:'Tuned, adaptive',color:A,values:E.map(e=>g('tuned','Adaptive',e).observed_s)}]});
  barChart(document.getElementById('c3'),{labels:E,ylabel:'distance in 12 s (cm)',fmt:v=>v.toFixed(1),series:[
    {name:'Fixed',color:F,values:E.map(e=>g('tuned','Fixed',e).x_displacement_m*100)},{name:'Adaptive',color:A,values:E.map(e=>g('tuned','Adaptive',e).x_displacement_m*100)}]});
  barChart(document.getElementById('c4'),{labels:E,ylabel:'largest pitch (°)',fmt:v=>v.toFixed(1),series:[
    {name:'Fixed',color:F,values:E.map(e=>g('tuned','Fixed',e).max_pitch_deg)},{name:'Adaptive',color:A,values:E.map(e=>g('tuned','Adaptive',e).max_pitch_deg)}]});
  barChart(document.getElementById('c5'),{labels:E,ylabel:'distance before fall (cm)',fmt:v=>v.toFixed(1),series:[
    {name:'Fixed',color:F,values:E.map(e=>g('first','Fixed',e).x_displacement_m*100)},{name:'Adaptive',color:A,values:E.map(e=>g('first','Adaptive',e).x_displacement_m*100)}]});
  const fix=g('first','Fixed','Moon').fall_time_s;
  const rows=E.map(e=>{const a=g('first','Fixed',e).fall_time_s,b=g('first','Adaptive',e).fall_time_s;return '<tr><td>'+e+'</td><td>'+a.toFixed(4)+'</td><td>'+b.toFixed(4)+'</td><td>'+((b-a)/a*100>=0?'+':'')+((b-a)/a*100).toFixed(1)+'%</td></tr>'}).join('');
  document.getElementById('t1').innerHTML='<tr><th>Gravity</th><th>Fixed (s)</th><th>Adaptive (s)</th><th>Change</th></tr>'+rows;
});
Promise.all([fetch('api/standing.json').then(r=>r.json()),fetch('api/foot_width.json').then(r=>r.json())]).then(([s,f])=>{
  document.getElementById('t2').innerHTML='<tr><th>Gravity</th><th>g (m/s²)</th><th>Both-foot contact (%)</th><th>Max roll (°)</th><th>Max pitch (°)</th></tr>'+s.map(r=>'<tr><td>'+r.environment+'</td><td>'+r.gravity+'</td><td>'+r.both_contact_pct+'</td><td>'+r.max_roll_deg+'</td><td>'+r.max_pitch_deg+'</td></tr>').join('');
  const w=[7,9,11];document.getElementById('t3').innerHTML='<tr><th>Foot width</th><th>Earth roll (°)</th><th>Moon roll (°)</th><th>Mars roll (°)</th><th>Contact (%)</th></tr>'+w.map(x=>{const q=e=>f.find(r=>r.foot_width_cm===x&&r.environment===e);return '<tr><td>'+x+' cm</td><td>'+q('Earth').max_roll_deg+'</td><td>'+q('Moon').max_roll_deg+'</td><td>'+q('Mars').max_roll_deg+'</td><td>'+q('Earth').both_contact_pct+'</td></tr>'}).join('');
});
