const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const LS={get:(k,d)=>{try{return JSON.parse(localStorage.getItem('glowra_'+k))??d}catch{return d}},set:(k,v)=>localStorage.setItem('glowra_'+k,JSON.stringify(v))};
const inr=n=>'₹'+n.toLocaleString('en-IN');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const user=()=>LS.get('session',null);
async function sha(t){if(!crypto.subtle)return btoa(t);const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
document.documentElement.dataset.theme=LS.get('theme','light');
function toast(m){let t=$('#toast');if(!t){t=document.createElement('div');t.id='toast';document.body.append(t)}t.textContent=m;t.classList.add('show');clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove('show'),2200)}
function totals(){const c=LS.get('cart',{}),pr=LS.get('promo',null);let sub=0;for(const id in c){const p=PRODUCTS.find(x=>x.id==id);if(p)sub+=p.price*c[id]}const disc=pr?Math.round(sub*PROMOS[pr]/100):0;const ship=!sub||sub-disc>=999?0:49;return{sub,disc,ship,total:sub-disc+ship,count:Object.values(c).reduce((a,b)=>a+b,0)}}
function addCart(id,q=1){const c=LS.get('cart',{});c[id]=(c[id]||0)+q;LS.set('cart',c);$('#cb').textContent=totals().count;toast('Added to cart')}
function toggleWish(id){let w=LS.get('wish',[]);w=w.includes(id)?w.filter(x=>x!=id):[...w,id];LS.set('wish',w);return w.includes(id)}
function card(p,m){const w=LS.get('wish',[]).includes(p.id);return `<article class="card"><div class="art" style="background:linear-gradient(135deg,hsl(${p.h} 75% 88%),hsl(${p.h} 65% 72%))">${p.e}<button class="wish" data-wish="${p.id}" aria-label="Wishlist">${w?'♥':'♡'}</button>${m?`<span class="match">${m}% match</span>`:''}</div><div class="bd"><small>${p.cat} · ★ ${p.rating}</small><h3>${p.name}</h3><small>${p.desc}</small><div class="row"><b>${inr(p.price)}</b><button class="btn sm" data-add="${p.id}">Add to cart</button></div></div></article>`}
function rnd(seed){let a=Math.floor((seed||0)*4294967296)||1;return()=>{a=(a*1664525+1013904223)%4294967296;return a/4294967296}}
function recommend(s){const R=rnd(s.seed),has=(a,v)=>a.includes('all')||a.includes(v);return PRODUCTS.map(p=>{let m=50;m+=has(p.skin,s.skin)?15:-10;m+=has(p.tones,s.tone)?12:-25;m+=has(p.under,s.under)?8:-8;m+=p.concerns.filter(c=>s.concerns.includes(c)).length*12;return{p,m:Math.round(Math.max(40,Math.min(99,m+R()*18-9)))}}).sort((a,b)=>b.m-a.m)}
function nav(){const u=user(),t=totals(),pg=location.pathname.split('/').pop()||'index.html';
const l=[['shop.html','Shop'],['scan.html','AI Scan'],['orders.html','My orders'],['profile.html','Profile']].map(([h,n])=>`<a href="${h}" class="${pg==h?'on':''}">${n}</a>`).join('');
$('#nav').innerHTML=`<div class="bar"><a class="logo" href="index.html">glowra<i>✦</i></a><nav>${l}</nav><div class="acts"><button id="th" class="ic" aria-label="Toggle dark mode">◐</button><a class="ic" href="cart.html" aria-label="Cart">🛍<b id="cb">${t.count}</b></a>${u?`<a class="hi" href="profile.html">Hi, ${esc(u.name.split(' ')[0])}</a><button class="btn sm ghost" id="lo">Log out</button>`:`<a class="btn sm ghost" href="login.html">Log in</a><a class="btn sm" href="signup.html">Sign up</a>`}</div></div>`;
$('#foot').innerHTML='© Glowra. All rights reserved.';
$('#th').onclick=()=>{const t=document.documentElement.dataset.theme=='dark'?'light':'dark';document.documentElement.dataset.theme=t;LS.set('theme',t)};
if(u)$('#lo').onclick=()=>{localStorage.removeItem('glowra_session');location.href='index.html'}}
document.addEventListener('click',e=>{const a=e.target.closest('[data-add]');if(a)addCart(+a.dataset.add);const w=e.target.closest('[data-wish]');if(w)w.textContent=toggleWish(+w.dataset.wish)?'♥':'♡'});
nav();
