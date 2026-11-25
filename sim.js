(function(){
let D; const $=id=>document.getElementById(id);
const cv=$('cv'),ctx=cv.getContext('2d'),ch=$('chart'),cc=ch.getContext('2d');
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
let run,key,t=0,playing=true,last=null,prm,freq,env,ctl,gait,ended=false;
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();

function pick(){
  env=$('env').value;ctl=$('ctl').value;gait=$('gait').value;
  key=gait+'|'+ctl+'|'+env;run=D.runs[key];prm=D.params[gait][ctl];
  const f0=prm.freq;freq=ctl==='Fixed'?f0:f0*Math.sqrt(D.gravity[env]/9.80665);
  t=0;ended=false;$('badge').hidden=true;playing=true;$('play').textContent='Pause';
  summary();table();
}
function at(tt){ // interpolate [t,x,h,pitch,roll,fall]
  const n=run.length;
  if(tt<=run[0][0])return run[0];
  if(tt>=run[n-1][0])return run[n-1];
  let i=0;while(run[i+1][0]<tt)i++;
  const a=run[i],b=run[i+1],u=(tt-a[0])/(b[0]-a[0]);
  return a.map((v,k)=>k===0?tt:v+(b[k]-v)*u);
}
function targets(tt,pitch,rate){
  const p=prm;let r=clamp(tt/p.startup,0,1);r=r*r*(3-2*r);
  const lw=Math.sin(2*Math.PI*freq*tt),rw=-lw;
  const ac=clamp(p.ankle_kp*pitch+p.ankle_kd*rate,-p.max_corr,p.max_corr);
  const hc=clamp(p.hip_kp*pitch+p.hip_kd*rate,-p.max_corr,p.max_corr);
  const ab=r*p.ankle_bias,hb=r*p.hip_bias;
  return{L:{hip:r*p.hip_amp*lw+hb+hc,knee:r*p.knee_amp*Math.max(0,lw),ank:-r*p.ankle_amp*lw+ab+ac},
         R:{hip:r*p.hip_amp*rw+hb+hc,knee:r*p.knee_amp*Math.max(0,rw),ank:-r*p.ankle_amp*rw+ab+ac}};
}
const S=470,GY=360; // px per metre, ground y
function draw(){
  const s=at(t),pitch=s[3]*Math.PI/180,rate=(at(t+0.05)[3]-at(Math.max(0,t-0.05))[3])*Math.PI/180/0.1;
  const W=cv.width,H=cv.height;ctx.clearRect(0,0,W,H);
  const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#0a1230');g.addColorStop(1,'#1a2550');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  // stars
  ctx.fillStyle='#ffffff55';for(let i=0;i<40;i++){ctx.fillRect((i*137)%W,(i*53)%200,1.5,1.5)}
  const camX=s[1],cx=W/2;const X=m=>cx+(m-camX)*S;
  // ground with 0.1 m ticks
  ctx.fillStyle=env==='Moon'?'#6b6f7c':env==='Mars'?'#8a4a33':'#3d5e3a';ctx.fillRect(0,GY,W,H-GY);
  ctx.strokeStyle='#ffffff55';ctx.fillStyle='#ffffffaa';ctx.font='11px system-ui';
  for(let m=Math.floor((camX-cx/S)*10)/10;m<camX+cx/S;m+=0.1){const x=X(m);ctx.beginPath();ctx.moveTo(x,GY);ctx.lineTo(x,GY+8);ctx.stroke();if(Math.abs(Math.round(m*10)%5)===0)ctx.fillText((Math.abs(m)<0.005?0:m).toFixed(1)+' m',x-14,GY+22)}
  const tg=targets(t,pitch,rate);
  // body centre and hips
  const bx=X(s[1]),by=GY-s[2]*S;
  const rot=(px,py)=>[bx+(px*Math.cos(pitch)+py*Math.sin(pitch))*S,by-(py*Math.cos(pitch)-px*Math.sin(pitch))*S];
  // body box 0.16 deep x 0.22 tall (pitch>0: top leans forward)
  const c=[[-.08,.11],[.08,.11],[.08,-.11],[-.08,-.11]].map(p=>rot(p[0],p[1]));
  const hipP=rot(0,-0.11);
  function leg(q,alpha,col){
    const a1=pitch+q.hip,a2=a1-q.knee,a3=a2+q.ank;
    const d=(a)=>[Math.sin(a),Math.cos(a)];
    const k=[hipP[0]+d(a1)[0]*.2*S,hipP[1]+d(a1)[1]*.2*S];
    const f=[k[0]+d(a2)[0]*.2*S,k[1]+d(a2)[1]*.2*S];
    ctx.globalAlpha=alpha;ctx.lineCap='round';ctx.strokeStyle=col;ctx.lineWidth=13;
    ctx.beginPath();ctx.moveTo(hipP[0],hipP[1]);ctx.lineTo(k[0],k[1]);ctx.stroke();
    ctx.lineWidth=10;ctx.beginPath();ctx.moveTo(k[0],k[1]);ctx.lineTo(f[0],f[1]);ctx.stroke();
    // foot 0.14 long
    const fd=[Math.cos(a3),-Math.sin(a3)];
    ctx.lineWidth=7;ctx.beginPath();ctx.moveTo(f[0]-fd[0]*.04*S,f[1]-fd[1]*.04*S);ctx.lineTo(f[0]+fd[0]*.10*S,f[1]+fd[1]*.10*S);ctx.stroke();
    ctx.fillStyle='#fff';[hipP,k,f].forEach(p=>{ctx.beginPath();ctx.arc(p[0],p[1],3.5,0,6.3);ctx.fill()});
    ctx.globalAlpha=1;
  }
  leg(tg.R,.45,'#7aa7e8');leg(tg.L,1,'#9fd0ff');
  ctx.fillStyle='#2f6fe0';ctx.strokeStyle='#cfe3ff';ctx.lineWidth=2;ctx.beginPath();c.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fill();ctx.stroke();
  // HUD
  $('hg').textContent=D.gravity[env].toFixed(2)+' m/s²';$('hf').textContent=freq.toFixed(3)+' Hz';
  $('ht').textContent=t.toFixed(1)+' s';$('hx').textContent=(s[1]*100).toFixed(1)+' cm';$('hp').textContent=s[3].toFixed(1)+'°';
  chart(s);
  const T=run[run.length-1][0];$('seek').value=Math.round(t/T*1000);
}
function chart(s){
  const W=ch.width,H=ch.height,T=run[run.length-1][0],T12=gait==='tuned'?12:Math.max(T,1);
  cc.clearRect(0,0,W,H);cc.fillStyle='#0b1020';cc.fillRect(0,0,W,H);
  const series=[['Pitch (°)',3,'#ff9b6b'],['Distance (×10 cm)',1,'#6fe0a1',10],['Roll (°)',4,'#5ab0ff']];
  let lo=-1,hi=1;run.forEach(r=>{[r[3],r[4],r[1]*10].forEach(v=>{lo=Math.min(lo,v);hi=Math.max(hi,v)})});
  const pad=28,X=tt=>pad+tt/T12*(W-pad-10),Y=v=>H-22-(v-lo)/(hi-lo)*(H-40);
  cc.strokeStyle='#243055';cc.beginPath();cc.moveTo(pad,Y(0));cc.lineTo(W-10,Y(0));cc.stroke();
  cc.fillStyle='#9aa6c4';cc.font='11px system-ui';cc.fillText('0',8,Y(0)+4);cc.fillText('0',X(0),H-6);cc.fillText(T12.toFixed(0)+' s',W-34,H-6);
  series.forEach((sr,i)=>{cc.strokeStyle=sr[2];cc.lineWidth=2;cc.beginPath();run.forEach((r,k)=>{const v=r[sr[1]]*(sr[3]||1);k?cc.lineTo(X(r[0]),Y(v)):cc.moveTo(X(r[0]),Y(v))});cc.stroke();cc.fillStyle=sr[2];cc.fillText(sr[0],pad+8+i*130,14)});
  cc.strokeStyle='#fff';cc.beginPath();cc.moveTo(X(t),6);cc.lineTo(X(t),H-20);cc.stroke();
}
function summary(){
  const m=D.summary[key];
  const fell=m.fall!==null&&m.fall!==undefined&&!isNaN(m.fall);
  $('sum').innerHTML=[['Result',fell?'<b class="fall">Fell at '+m.fall.toFixed(2)+' s</b>':'<b class="up">Upright for 12 s</b>'],['Frequency','<b>'+m.freq.toFixed(3)+' Hz</b>'],['Distance','<b>'+(m.dx>=0?'+':'')+(m.dx*100).toFixed(1)+' cm</b>'],['Max pitch','<b>'+m.pitch.toFixed(1)+'°</b>'],['Max roll','<b>'+m.roll.toFixed(1)+'°</b>']].map(a=>'<div><span>'+a[0]+'</span>'+a[1]+'</div>').join('');
}
function table(){
  const rows=['first','tuned'].flatMap(g=>['Fixed','Adaptive'].flatMap(c=>['Earth','Moon','Mars'].map(e=>[g,c,e])));
  $('tbl').innerHTML='<tr><th>Gait</th><th>Controller</th><th>Gravity</th><th>Result</th><th>Δx (cm)</th><th>Max pitch</th></tr>'+rows.map(r=>{const k=r.join('|'),m=D.summary[k],f=m.fall!==null&&m.fall!==undefined&&!isNaN(m.fall);
    return '<tr data-k="'+k+'" class="'+(k===key?'sel':'')+'"><td>'+(r[0]==='first'?'First':'Tuned')+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td class="'+(f?'fall':'up')+'">'+(f?'Fell '+m.fall.toFixed(2)+' s':'12 s up')+'</td><td>'+(m.dx*100).toFixed(1)+'</td><td>'+m.pitch.toFixed(1)+'°</td></tr>'}).join('');
  [...$('tbl').querySelectorAll('tr[data-k]')].forEach(tr=>tr.onclick=()=>{const [g,c,e]=tr.dataset.k.split('|');$('gait').value=g;$('ctl').value=c;$('env').value=e;pick();window.scrollTo({top:0,behavior:'smooth'})});
}
function frame(ts){
  if(last===null)last=ts;const dt=(ts-last)/1000;last=ts;
  const T=run[run.length-1][0];
  if(playing){t+=dt*parseFloat($('spd').value);if(t>=T){t=T;playing=false;ended=true;$('play').textContent='Replay';
    const m=D.summary[key],f=m.fall!==null&&m.fall!==undefined&&!isNaN(m.fall);const b=$('badge');b.hidden=false;b.className='badge '+(f?'fall':'ok');b.textContent=f?'FALL':'Stayed upright'}}
  draw();requestAnimationFrame(frame);
}
['env','ctl','gait'].forEach(i=>$(i).onchange=pick);
$('play').onclick=()=>{if(ended){t=0;ended=false;$('badge').hidden=true;playing=true;$('play').textContent='Pause'}else{playing=!playing;$('play').textContent=playing?'Pause':'Play'}};
$('seek').oninput=e=>{const T=run[run.length-1][0];t=e.target.value/1000*T;playing=false;ended=false;$('badge').hidden=true;$('play').textContent='Play'};
Promise.all(['timeseries.json','params.json','runs.json'].map(u=>fetch(u).then(r=>r.json()))).then(([ts,pr,runs])=>{
  const P=n=>{const o={};pr.filter(r=>r.controller===n).forEach(r=>o[r.name]=r.value);return o};
  const first=P('first (both)');
  D={gravity:{Earth:9.80665,Moon:1.62,Mars:3.73},runs:ts,params:{first:{Fixed:first,Adaptive:first},tuned:{Fixed:P('tuned Fixed'),Adaptive:P('tuned Adaptive')}},summary:{}};
  runs.forEach(r=>{D.summary[r.gait+'|'+r.controller+'|'+r.environment]={freq:r.frequency_hz,fall:r.fell?r.fall_time_s:null,dx:r.x_displacement_m,pitch:r.max_pitch_deg,roll:r.max_roll_deg}});
  pick();requestAnimationFrame(frame);
}).catch(e=>{$('sum').innerHTML='<p class="fall">Could not load the data files ('+e+'). Open the site through a web server or GitHub Pages, not by double-clicking the file.</p>'});
})();
