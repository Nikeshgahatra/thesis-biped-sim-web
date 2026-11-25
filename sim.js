(function(){
const $=id=>document.getElementById(id), clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
let D,env='Moon',gait='tuned',t=0,playing=true,last=null,T=12;
const G={Earth:9.80665,Moon:1.62,Mars:3.73};
const panels=['Fixed','Adaptive'].map(c=>({c,cv:$('cv'+c),ctx:$('cv'+c).getContext('2d')}));
// ---------- data helpers
function at(run,tt){const n=run.length;if(tt<=run[0][0])return run[0];if(tt>=run[n-1][0])return run[n-1];
  let i=0;while(run[i+1][0]<tt)i++;const p0=run[Math.max(0,i-1)],p1=run[i],p2=run[i+1],p3=run[Math.min(n-1,i+2)],u=(tt-p1[0])/(p2[0]-p1[0]),u2=u*u,u3=u2*u;
  return p1.map((v,k)=>{if(k===0)return tt;if(k===5)return v;
    return 0.5*((2*p1[k])+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u2+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u3)})}
function freqOf(c){const f0=D.params[gait][c].freq;return c==='Fixed'?f0:f0*Math.sqrt(G[env]/9.80665)}
function targets(prm,freq,tt,pitch,rate){
  let r=clamp(tt/prm.startup,0,1);r=r*r*(3-2*r);const lw=Math.sin(2*Math.PI*freq*tt),rw=-lw;
  const ac=clamp(prm.ankle_kp*pitch+prm.ankle_kd*rate,-prm.max_corr,prm.max_corr),hc=clamp(prm.hip_kp*pitch+prm.hip_kd*rate,-prm.max_corr,prm.max_corr);
  const ab=r*prm.ankle_bias,hb=r*prm.hip_bias;
  return{L:{hip:r*prm.hip_amp*lw+hb+hc,knee:r*prm.knee_amp*Math.max(0,lw),ank:-r*prm.ankle_amp*lw+ab+ac},R:{hip:r*prm.hip_amp*rw+hb+hc,knee:r*prm.knee_amp*Math.max(0,rw),ank:-r*prm.ankle_amp*rw+ab+ac}}}
// ---------- drawing one robot panel
const S=285,GY=262,X0=0.70; // px per metre, ground line, x (m) at the left edge
function drawPanel(p){
  const key=gait+'|'+p.c+'|'+env,run=D.runs[key],sm=D.summary[key],ctx=p.ctx,W=p.cv.width,H=p.cv.height;
  const endT=run[run.length-1][0],fell=sm.fall!==null,tt=Math.min(t,endT),done=t>=endT;
  const s=at(run,tt),pitch=s[3]*Math.PI/180,rate=(at(run,tt+0.05)[3]-at(run,Math.max(0,tt-0.05))[3])*Math.PI/180/0.1;
  const X=m=>(m+X0)*S+30; // fixed camera: the start flag stays put
  ctx.clearRect(0,0,W,H);
  const g=ctx.createLinearGradient(0,0,0,GY);g.addColorStop(0,'#070c24');g.addColorStop(1,'#1a2552');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#ffffff40';for(let i=0;i<26;i++)ctx.fillRect((i*89)%W,(i*47)%150,1.5,1.5);
  ctx.fillStyle=env==='Moon'?'#6b6f7c':env==='Mars'?'#8a4a33':'#3d5e3a';ctx.fillRect(0,GY,W,H-GY);
  // ruler with 10 cm ticks (clear sense of distance)
  ctx.strokeStyle='#ffffff77';ctx.fillStyle='#ffffffcc';ctx.font='11px system-ui';ctx.textAlign='center';
  for(let m=-0.5;m<=0.8001;m+=0.1){const x=X(m);ctx.beginPath();ctx.moveTo(x,GY);ctx.lineTo(x,GY+(Math.abs(Math.round(m*10)%2)?6:12));ctx.stroke();if(Math.round(m*10)%2===0)ctx.fillText(Math.round(m*100)+' cm',x,GY+26)}
  // start flag
  ctx.strokeStyle='#ffd166';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(X(0),GY);ctx.lineTo(X(0),GY-150);ctx.stroke();ctx.fillStyle='#ffd166';ctx.fillRect(X(0),GY-150,34,12);ctx.fillStyle='#1a1a1a';ctx.textAlign='left';ctx.fillText('START',X(0)+3,GY-140);
  // trail of the body position
  ctx.fillStyle='#38e0b488';for(const r of run){if(r[0]>tt)break;ctx.beginPath();ctx.arc(X(r[1]),GY+40,2,0,6.3);ctx.fill()}
  // robot
  const bx=X(s[1]),by=GY-s[2]*S;const rot=(px,py)=>[bx+(px*Math.cos(pitch)+py*Math.sin(pitch))*S,by-(py*Math.cos(pitch)-px*Math.sin(pitch))*S];
  const tg=targets(D.params[gait][p.c],freqOf(p.c),tt,pitch,rate),hipP=rot(0,-0.11),K=parseFloat($('amp').value);['L','R'].forEach(k=>{tg[k].hip*=K;tg[k].knee*=K;tg[k].ank*=K});
  function leg(q,al,col){const a1=pitch+q.hip,a2=a1-q.knee,a3=a2+q.ank,d=a=>[Math.sin(a),Math.cos(a)];
    const k=[hipP[0]+d(a1)[0]*.2*S,hipP[1]+d(a1)[1]*.2*S],f=[k[0]+d(a2)[0]*.2*S,k[1]+d(a2)[1]*.2*S];
    ctx.globalAlpha=al;ctx.lineCap='round';ctx.strokeStyle=col;ctx.lineWidth=11;ctx.beginPath();ctx.moveTo(hipP[0],hipP[1]);ctx.lineTo(k[0],k[1]);ctx.stroke();
    ctx.lineWidth=9;ctx.beginPath();ctx.moveTo(k[0],k[1]);ctx.lineTo(f[0],f[1]);ctx.stroke();
    const fd=[Math.cos(a3),-Math.sin(a3)];ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(f[0]-fd[0]*.04*S,f[1]-fd[1]*.04*S);ctx.lineTo(f[0]+fd[0]*.10*S,f[1]+fd[1]*.10*S);ctx.stroke();
    ctx.fillStyle='#fff';[hipP,k,f].forEach(q=>{ctx.beginPath();ctx.arc(q[0],q[1],3,0,6.3);ctx.fill()});ctx.globalAlpha=1}
  const fallen=fell&&done,legc=p.c==='Fixed'?['#7a8fe8','#a9b8ff']:['#2fbf95','#6fe0b9'];
  leg(tg.R,.45,legc[0]);leg(tg.L,1,legc[1]);
  const c=[[-.08,.11],[.08,.11],[.08,-.11],[-.08,-.11]].map(q=>rot(q[0],q[1]));
  ctx.fillStyle=fallen?'#b8402f':(p.c==='Fixed'?'#3d5bd6':'#14996f');ctx.strokeStyle='#e8eeff';ctx.lineWidth=2;ctx.beginPath();c.forEach((q,i)=>i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();ctx.fill();ctx.stroke();
  // state overlays
  if(fallen){const flash=clamp(1-(t-endT)/0.8,0,1);ctx.fillStyle='rgba(214,64,47,'+(0.06+0.28*flash)+')';ctx.fillRect(0,0,W,H);
    ctx.fillStyle='#fff';ctx.font='bold 30px system-ui';ctx.textAlign='center';ctx.fillText('FALLEN at '+endT.toFixed(2)+' s',W/2,44)}
  else if(done){ctx.fillStyle='#6fe0a1';ctx.font='bold 22px system-ui';ctx.textAlign='center';ctx.fillText('STAYED UPRIGHT 12 s',W/2,60)}
  // numbers
  const x1=at(run,Math.max(0,tt-1))[1],inst=(s[1]-x1)/Math.min(1,Math.max(tt,0.1))*100,avg=tt>0?s[1]/tt*100:0;
  const hud=$('h'+p.c);
  hud.innerHTML='<div><span>Distance</span><b>'+(s[1]*100).toFixed(1)+' cm</b></div><div><span>Speed (last 1 s)</span><b class="'+(inst>=0.05?'up':inst<=-0.05?'fall':'')+'">'+(inst>=0?'+':'')+inst.toFixed(1)+' cm/s</b></div><div><span>Average speed</span><b>'+(avg>=0?'+':'')+avg.toFixed(1)+' cm/s</b></div><div><span>Pitch</span><b>'+s[3].toFixed(1)+'°</b></div>';
  $('t'+p.c).textContent=p.c==='Fixed'?'Fixed frequency · '+freqOf(p.c).toFixed(4)+' Hz':'Gravity-adaptive · '+freqOf(p.c).toFixed(4)+' Hz (period '+(1/freqOf(p.c)).toFixed(1)+' s)';
  const dir=$('d'+p.c);dir.textContent=fallen?'Fell backwards':done?'Finished':(inst>0.3?'Moving forward ➜':inst<-0.3?'⬅ Moving backwards':'Almost still');dir.className='dir '+(fallen||inst<-0.3?'fall':inst>0.3?'up':'');
}
// ---------- charts
function drawDist(){
  const cv=$('dist'),c=cv.getContext('2d'),W=cv.width,H=cv.height,pl=44,pr=10,pt=18,pb=26;c.clearRect(0,0,W,H);c.fillStyle='#0a1028';c.fillRect(0,0,W,H);
  const runs=['Fixed','Adaptive'].map(k=>D.runs[gait+'|'+k+'|'+env]);let lo=0,hi=0;runs.forEach(r=>r.forEach(p=>{lo=Math.min(lo,p[1]*100);hi=Math.max(hi,p[1]*100)}));hi+=3;lo-=3;
  const X=tt=>pl+tt/T*(W-pl-pr),Y=v=>pt+(hi-v)/(hi-lo)*(H-pt-pb);
  c.strokeStyle='#232e57';c.fillStyle='#9aa8cf';c.font='11px system-ui';c.textAlign='right';
  const st=(hi-lo)>40?10:5;for(let v=Math.ceil(lo/st)*st;v<=hi;v+=st){c.beginPath();c.moveTo(pl,Y(v));c.lineTo(W-pr,Y(v));c.stroke();c.fillText(v,pl-5,Y(v)+4)}
  c.textAlign='center';for(let s=0;s<=T;s+=2)c.fillText(s+' s',X(s),H-8);
  c.save();c.translate(11,H/2);c.rotate(-Math.PI/2);c.fillText('distance (cm)',0,0);c.restore();
  runs.forEach((r,i)=>{const col=i?'#38e0b4':'#7c9cff';c.strokeStyle=col;c.lineWidth=2.5;c.beginPath();r.forEach((p,k)=>k?c.lineTo(X(p[0]),Y(p[1]*100)):c.moveTo(X(p[0]),Y(p[1]*100)));c.stroke();
    const e=r[r.length-1];if(D.summary[gait+'|'+(i?'Adaptive':'Fixed')+'|'+env].fall!==null){c.fillStyle='#ff7a6b';c.font='bold 13px system-ui';c.textAlign='right';c.fillText('✕ fell',X(e[0])-4,Y(e[1]*100)-8)}});
  c.strokeStyle='#fff';c.lineWidth=1;c.beginPath();c.moveTo(X(Math.min(t,T)),pt-6);c.lineTo(X(Math.min(t,T)),H-pb);c.stroke();
}
function drawLaw(){
  const cv=$('law'),c=cv.getContext('2d'),W=cv.width,H=cv.height,pl=44,pr=14,pt=16,pb=34;c.clearRect(0,0,W,H);c.fillStyle='#0a1028';c.fillRect(0,0,W,H);
  const f0=D.params[gait].Adaptive.freq,fx=D.params[gait].Fixed.freq,gmax=11,fmax=Math.max(f0,fx)*1.15;
  const X=g=>pl+g/gmax*(W-pl-pr),Y=f=>pt+(1-f/fmax)*(H-pt-pb);
  c.strokeStyle='#232e57';c.fillStyle='#9aa8cf';c.font='11px system-ui';c.textAlign='right';
  for(let i=0;i<=4;i++){const f=fmax*i/4;c.beginPath();c.moveTo(pl,Y(f));c.lineTo(W-pr,Y(f));c.stroke();c.fillText(f.toFixed(2),pl-5,Y(f)+4)}
  c.textAlign='center';[0,2,4,6,8,10].forEach(g=>c.fillText(g,X(g),H-16));c.fillText('gravity (m/s²)',W/2,H-1);
  c.setLineDash([6,5]);c.strokeStyle='#7c9cff';c.lineWidth=2;c.beginPath();c.moveTo(X(0),Y(fx));c.lineTo(X(gmax),Y(fx));c.stroke();c.setLineDash([]);
  c.fillStyle='#7c9cff';c.textAlign='left';c.fillText('Fixed '+fx.toFixed(3)+' Hz',pl+8,Y(fx)-6);
  c.strokeStyle='#38e0b4';c.lineWidth=2.5;c.beginPath();for(let g=0;g<=gmax;g+=0.1){const f=f0*Math.sqrt(g/9.80665);g?c.lineTo(X(g),Y(f)):c.moveTo(X(g),Y(f))}c.stroke();
  [['Earth','#4aa3ff'],['Mars','#ff7a59'],['Moon','#cfd6ea']].forEach(([e,col])=>{const f=f0*Math.sqrt(G[e]/9.80665);c.fillStyle=col;c.beginPath();c.arc(X(G[e]),Y(f),e===env?7:4.5,0,6.3);c.fill();c.fillStyle='#eaf0ff';c.textAlign='center';c.fillText(e,X(G[e]),Y(f)+(e==='Earth'?-12:18))});
  c.strokeStyle='#ffffff99';c.setLineDash([4,4]);c.beginPath();c.moveTo(X(G[env]),pt);c.lineTo(X(G[env]),H-pb);c.stroke();c.setLineDash([]);
}
// ---------- run table and cards
function cards(){
  $('cmp').innerHTML=['Fixed','Adaptive'].map(c=>{const m=D.summary[gait+'|'+c+'|'+env],f=m.fall!==null,sp=f?m.dx/m.fall*100:m.dx/12*100;
    return '<div><span>'+c+'</span>'+(f?'<b class="fall">Fell at '+m.fall.toFixed(2)+' s</b>':'<b class="up">Upright for 12 s</b>')+'<small>'+(m.dx>=0?'+':'')+(m.dx*100).toFixed(1)+' cm · average '+(sp>=0?'+':'')+sp.toFixed(1)+' cm/s · max pitch '+m.pitch.toFixed(1)+'°</small></div>'}).join('');
}
function table(){
  const rows=['first','tuned'].flatMap(g=>['Fixed','Adaptive'].flatMap(c=>['Earth','Moon','Mars'].map(e=>[g,c,e])));
  $('tbl').innerHTML='<tr><th>Gait</th><th>Controller</th><th>Gravity</th><th>Result</th><th>Distance (cm)</th><th>Avg speed (cm/s)</th><th>Max pitch</th></tr>'+rows.map(r=>{const m=D.summary[r.join('|')],f=m.fall!==null,sp=m.dx/(f?m.fall:12)*100;
    return '<tr data-g="'+r[0]+'" data-c="'+r[1]+'" data-e="'+r[2]+'" class="'+(r[0]===gait&&r[2]===env?'sel':'')+'"><td>'+(r[0]==='first'?'First':'Tuned')+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td class="'+(f?'fall':'up')+'">'+(f?'Fell '+m.fall.toFixed(2)+' s':'12 s up')+'</td><td>'+(m.dx*100).toFixed(1)+'</td><td>'+sp.toFixed(1)+'</td><td>'+m.pitch.toFixed(1)+'°</td></tr>'}).join('');
  [...$('tbl').querySelectorAll('tr[data-g]')].forEach(tr=>tr.onclick=()=>{set(tr.dataset.e,tr.dataset.g);window.scrollTo({top:0,behavior:'smooth'})});
}
function set(e,g){env=e||env;gait=g||gait;$('gait').value=gait;
  T=Math.max(...['Fixed','Adaptive'].map(c=>{const r=D.runs[gait+'|'+c+'|'+env];return r[r.length-1][0]}));
  [...document.querySelectorAll('.gb')].forEach(b=>b.classList.toggle('on',b.dataset.e===env));
  $('gv').textContent=G[env].toFixed(2)+' m/s²';t=0;cards();table();}
function frame(ts){
  if(last===null)last=ts;const dt=(ts-last)/1000;last=ts;
  t+=dt*parseFloat($('spd').value);if(t>=T+1.8)t=0;
  panels.forEach(drawPanel);drawDist();drawLaw();$('clock').textContent=Math.min(t,T).toFixed(1)+' s';
  requestAnimationFrame(frame);
}
[...document.querySelectorAll('.gb')].forEach(b=>b.onclick=()=>set(b.dataset.e));
$('gait').onchange=e=>set(null,e.target.value);
Promise.all(['timeseries.json','params.json','runs.json'].map(u=>fetch(u).then(r=>r.json()))).then(([ts,pr,runs])=>{
  const P=n=>{const o={};pr.filter(r=>r.controller===n).forEach(r=>o[r.name]=r.value);return o};const first=P('first (both)');
  D={runs:ts,params:{first:{Fixed:first,Adaptive:first},tuned:{Fixed:P('tuned Fixed'),Adaptive:P('tuned Adaptive')}},summary:{}};
  runs.forEach(r=>{D.summary[r.gait+'|'+r.controller+'|'+r.environment]={fall:r.fell?r.fall_time_s:null,dx:r.x_displacement_m,pitch:r.max_pitch_deg}});
  set('Moon','tuned');requestAnimationFrame(frame);
}).catch(e=>{$('cmp').innerHTML='<p class="fall">Could not load the data files ('+e+').</p>'});
})();
