const s=user();if(!s)location.href='login.html?next=profile.html';
const me=()=>LS.get('users',[]).find(x=>x.email==s.email);
const put=u=>LS.set('users',LS.get('users',[]).map(x=>x.email==s.email?u:x));
let edit=null;
function fill(){const u=me();$('#n').value=u.name;$('#e').value=u.email;$('#ph').value=u.phone||''}
$('#fd').onsubmit=e=>{e.preventDefault();const u=me(),em=$('#e').value.trim().toLowerCase();
if(em!=u.email&&LS.get('users',[]).some(x=>x.email==em)){$('#e1').textContent='That email is already used by another account.';return}
const old=u.email;u.name=$('#n').value.trim();u.email=em;u.phone=$('#ph').value;put(u);
LS.set('orders',LS.get('orders',[]).map(o=>o.email==old?{...o,email:em}:o));
LS.set('session',{name:u.name,email:em});s.email=em;s.name=u.name;$('#e1').textContent='';nav();toast('Details saved')};
$('#fp').onsubmit=async e=>{e.preventDefault();const u=me();
if(u.hash!=await sha($('#cp').value)){$('#e2').textContent='Current password is incorrect.';return}
if($('#np').value!=$('#rp').value){$('#e2').textContent='New passwords do not match.';return}
u.hash=await sha($('#np').value);put(u);$('#fp').reset();$('#e2').textContent='';toast('Password updated')};
function list(){const a=me().addresses||[];
$('#al').innerHTML=a.length?a.map(x=>`<article class="card ad"><div><b>${esc(x.label)}</b> ${x.def?'<span class="def">Default</span>':''}</div><div>${esc(x.name)} · ${esc(x.phone)}</div><div class="mut">${esc(x.addr)}, ${esc(x.city)} ${esc(x.pin)}</div><div class="bd2"><button class="chip" data-ed="${x.id}">Edit</button>${x.def?'':`<button class="chip" data-df="${x.id}">Make default</button>`}<button class="chip" data-rm="${x.id}">Delete</button></div></article>`).join(''):'<p class="mut">No saved addresses yet. Add one below and pick it at checkout.</p>'}
function reset(){edit=null;$('#fa').reset();$('#at').textContent='Add a new address';$('#cx').hidden=true}
$('#cx').onclick=reset;
$('#fa').onsubmit=e=>{e.preventDefault();const u=me();let a=u.addresses||[];
const x={id:edit||'a'+Date.now(),label:$('#lb').value,name:$('#an').value.trim(),phone:$('#ap').value,pin:$('#az').value,addr:$('#aa').value.trim(),city:$('#ac').value.trim()};
if(edit)a=a.map(y=>y.id==edit?{...x,def:y.def}:y);else a.push({...x,def:!a.length});
u.addresses=a;put(u);list();reset();toast('Address saved')};
document.addEventListener('click',e=>{const g=k=>e.target.closest(`[data-${k}]`)?.dataset[k],u=me();let a=u.addresses||[];
if(g('ed')){const x=a.find(y=>y.id==g('ed'));edit=x.id;$('#lb').value=x.label;$('#an').value=x.name;$('#ap').value=x.phone;$('#az').value=x.pin;$('#aa').value=x.addr;$('#ac').value=x.city;$('#at').textContent='Edit address';$('#cx').hidden=false;$('#fa').scrollIntoView({behavior:'smooth'});return}
if(g('df'))a=a.map(y=>({...y,def:y.id==g('df')}));else if(g('rm')){a=a.filter(y=>y.id!=g('rm'));if(a.length&&!a.some(y=>y.def))a[0].def=true}else return;
u.addresses=a;put(u);list()});
fill();list();
