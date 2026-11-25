fetch('params.json').then(r=>r.json()).then(p=>{
  const names=[['freq','Frequency f0 (Hz)'],['hip_amp','Hip amplitude (rad)'],['knee_amp','Knee amplitude (rad)'],['ankle_amp','Ankle amplitude (rad)'],['startup','Start-up time (s)'],['ankle_kp','Ankle feedback kp'],['ankle_kd','Ankle feedback kd'],['hip_kp','Hip feedback kp'],['hip_kd','Hip feedback kd'],['ankle_bias','Ankle bias (rad)'],['hip_bias','Hip bias (rad)']];
  const v=(c,n)=>{const r=p.find(x=>x.controller===c&&x.name===n);return r?(+r.value.toPrecision(4)).toString():''};
  document.getElementById('tp').innerHTML='<tr><th>Parameter</th><th>First gait</th><th>Tuned fixed</th><th>Tuned adaptive</th></tr>'+names.map(n=>'<tr><td>'+n[1]+'</td><td>'+v('first (both)',n[0])+'</td><td>'+v('tuned Fixed',n[0])+'</td><td>'+v('tuned Adaptive',n[0])+'</td></tr>').join('');
});
