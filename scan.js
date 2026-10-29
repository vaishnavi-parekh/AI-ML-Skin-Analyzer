const TIPS={oval:'Balanced proportions. Most shapes suit you; a soft contour is optional.',round:'Add contour along the cheekbones and jaw to add definition.',square:'Soften the jawline with blush on the apples of the cheeks.',heart:'Balance a wider forehead with blush low on the cheeks.',oblong:'Place blush horizontally to add width, and skip heavy contour.'};
let stream,LM;
$$('[data-t]').forEach(b=>b.onclick=()=>{$$('[data-t]').forEach(x=>x.classList.toggle('on',x==b));$('#pcam').hidden=b.dataset.t!='cam';$('#pup').hidden=b.dataset.t!='up';$('#pq').hidden=b.dataset.t!='quiz'});
$('#start').onclick=async()=>{try{stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user'}});$('#v').srcObject=stream;$('#start').hidden=true;$('#snap').hidden=false}catch{$('#st').textContent='Camera blocked or unavailable. Upload a photo or use the quick quiz instead.'}};
$('#snap').onclick=()=>{const v=$('#v'),c=$('#c');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);run(c)};
$('#f').onchange=e=>{const f=e.target.files[0];if(!f)return;const im=new Image();im.onload=()=>{const c=$('#c'),k=Math.min(1,900/im.width);c.width=im.width*k;c.height=im.height*k;c.getContext('2d').drawImage(im,0,0,c.width,c.height);run(c)};im.src=URL.createObjectURL(f)};
async function loadLM(){if(LM)return LM;const B='https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14';const v=await import(B+'/vision_bundle.mjs');const f=await v.FilesetResolver.forVisionTasks(B+'/wasm');return LM=await v.FaceLandmarker.createFromOptions(f,{baseOptions:{modelAssetPath:'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'},runningMode:'IMAGE',numFaces:1})}
async function run(c){$('#st').textContent='Analyzing on your device…';let lm=null,fb=false;
try{lm=(await(await loadLM()).detect(c)).faceLandmarks[0]}catch{}
if(!lm){fb=true;lm={50:{x:.3,y:.55},280:{x:.7,y:.55},151:{x:.5,y:.22},145:{x:.38,y:.45},374:{x:.62,y:.45}}}
const s=analyze(c,lm,fb);s.seed=Math.random();LS.set('scan',s);$('#st').textContent=fb?'No face detected, so I used a center estimate. For better accuracy, retake in good light facing the camera.':'Done. Your scan is saved to this browser.';show(s)}
function analyze(c,lm,fb){const W=c.width,H=c.height,x=c.getContext('2d');
const patch=(p,dy=0,r=6)=>{const px=p.x*W,py=p.y*H+dy*H;const d=x.getImageData(Math.max(0,px-r),Math.max(0,py-r),2*r,2*r).data;let R=0,G=0,B=0,n=d.length/4;for(let k=0;k<d.length;k+=4){R+=d[k];G+=d[k+1];B+=d[k+2]}return[R/n,G/n,B/n]};
const lum=a=>.299*a[0]+.587*a[1]+.114*a[2],mid=(a,b)=>a.map((v,i)=>(v+b[i])/2);
const ch=mid(patch(lm[50]),patch(lm[280])),fo=patch(lm[151]),ue=mid(patch(lm[145],.03),patch(lm[374],.03));
const L=lum(ch),tone=L>200?'fair':L>170?'light':L>135?'medium':L>100?'tan':'deep';
const[r,g,b]=ch,mx=Math.max(r,g,b),mn=Math.min(r,g,b);let h=0;if(mx!=mn){h=mx==r?60*((g-b)/(mx-mn)):mx==g?60*(2+(b-r)/(mx-mn)):60*(4+(r-g)/(mx-mn));if(h<0)h+=360}
const under=h<16?'cool':h>26?'warm':'neutral',sh=lum(fo)-L,skin=sh>12?'oily':sh>5?'combination':sh<-6?'dry':'normal';
const concerns=[];if(r/g>1.42)concerns.push('redness');if(L-lum(ue)>22)concerns.push('darkcircles');if(skin=='dry')concerns.push('dryness');if(skin=='oily')concerns.push('oil');
let shape='oval';if(!fb){const d=(a,b)=>Math.hypot((lm[a].x-lm[b].x)*W,(lm[a].y-lm[b].y)*H),w=d(234,454),ht=d(10,152),jw=d(172,397),fw=d(103,332),q=ht/w;shape=q>1.45?'oblong':fw/jw>1.15?'heart':jw/w>.86&&q<1.4?'square':q<1.25?'round':'oval'}
return{tone,under,skin,shape,concerns,fb}}
$('#pq').onsubmit=e=>{e.preventDefault();const k=$('#qc').value;const s={skin:$('#qs').value,tone:$('#qt').value,under:$('#qu').value,shape:'oval',concerns:k?[k]:[],seed:Math.random()};LS.set('scan',s);$('#st').textContent='';show(s)};
function show(s){const t=[`Skin tone: ${s.tone}`,`Undertone: ${s.under}`,`Skin type: ${s.skin}`,`Face shape: ${s.shape}`,...s.concerns.map(c=>({redness:'Redness',darkcircles:'Dark circles',dryness:'Dryness',oil:'Excess oil'}[c]))];
$('#res').innerHTML=`<div class="panel"><h2 style="margin-top:0">Your skin profile</h2><div class="tags">${t.map(x=>`<span class="chip">${x}</span>`).join('')}</div><p class="mut">${TIPS[s.shape]||TIPS.oval}</p></div><h2>Picked for you <button class="btn sm ghost" id="sh">Shuffle picks</button></h2><div class="grid">${recommend(s).slice(0,8).map(x=>card(x.p,x.m)).join('')}</div>`;$('#sh').onclick=()=>{s.seed=Math.random();LS.set('scan',s);show(s)};if(!window._f){window._f=1;$('#res').scrollIntoView({behavior:'smooth'})}}
if(LS.get('scan',null))show(LS.get('scan'));
