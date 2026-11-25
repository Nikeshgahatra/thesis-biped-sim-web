// tiny grouped bar chart. groups: labels[]; series: [{name,color,values[]}]
window.barChart=function(canvas,o){
  const c=canvas.getContext('2d'),W=canvas.width,H=canvas.height,pl=54,pr=12,pt=14,pb=34;
  c.clearRect(0,0,W,H);c.fillStyle='#0a1028';c.fillRect(0,0,W,H);
  let hi=0,lo=0;o.series.forEach(s=>s.values.forEach(v=>{hi=Math.max(hi,v);lo=Math.min(lo,v)}));
  hi=hi*1.12||1;if(lo<0)lo=lo*1.12;
  const Y=v=>pt+(hi-v)/(hi-lo)*(H-pt-pb),n=o.labels.length,gw=(W-pl-pr)/n,bw=Math.min(46,gw*0.8/o.series.length);
  c.font='12px system-ui';c.fillStyle='#9aa8cf';c.strokeStyle='#232e57';
  const step=niceStep((hi-lo)/5);for(let v=Math.ceil(lo/step)*step;v<=hi;v+=step){c.beginPath();c.moveTo(pl,Y(v));c.lineTo(W-pr,Y(v));c.stroke();c.textAlign='right';c.fillText((+v.toFixed(3)).toString(),pl-6,Y(v)+4)}
  o.labels.forEach((lb,i)=>{const x0=pl+i*gw+gw/2-o.series.length*bw/2;
    o.series.forEach((s,k)=>{const v=s.values[i];c.fillStyle=s.color;const y=Y(Math.max(v,0)),y0=Y(Math.min(v,0));c.fillRect(x0+k*bw+2,y,bw-4,Math.max(1,y0-y));
      c.fillStyle='#eaf0ff';c.textAlign='center';c.fillText(o.fmt?o.fmt(v):v,x0+k*bw+bw/2,(v>=0?y-4:y0+13))});
    c.fillStyle='#9aa8cf';c.textAlign='center';c.fillText(lb,pl+i*gw+gw/2,H-12)});
  c.save();c.translate(13,(H-pb)/2);c.rotate(-Math.PI/2);c.textAlign='center';c.fillStyle='#9aa8cf';c.fillText(o.ylabel||'',0,0);c.restore();
  const lg=canvas.parentElement.querySelector('.legend');if(lg)lg.innerHTML=o.series.map(s=>'<span><i style="background:'+s.color+'"></i>'+s.name+'</span>').join('');
  function niceStep(r){const p=Math.pow(10,Math.floor(Math.log10(r||1))),m=r/p;return (m<1.5?1:m<3?2:m<7?5:10)*p}
};
