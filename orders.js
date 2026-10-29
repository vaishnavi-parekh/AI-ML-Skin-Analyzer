const u=user();if(!u)location.href='login.html?next=orders.html';
const S=['Placed','Packed','Shipped','Delivered'];
function draw(){const o=LS.get('orders',[]).filter(x=>x.email==u.email);
$('#w').innerHTML=o.length?o.map(x=>{const st=Math.min(3,Math.floor((Date.now()-x.ts)/30000));
return `<div class="panel o"><div class="oh"><b>#${x.id}</b><span class="mut">${new Date(x.ts).toLocaleString('en-IN')} · ${inr(x.total)} · ${x.pay}</span></div><div class="tl">${S.map((s,i)=>`<div class="${i<=st?'d':''}">${s}</div>`).join('')}</div>${x.items.map(i=>{const p=PRODUCTS.find(y=>y.id==i.id);return `<p>${p.e} ${p.name} × ${i.q}</p>`}).join('')}<p class="mut"><small>Ship to: ${esc(x.addr)}</small></p><button class="btn sm ghost" data-re="${x.id}">Reorder</button></div>`}).join(''):'<p class="mut" style="margin:16px 0">No orders yet.</p><a class="btn" href="shop.html">Shop now</a>'}
document.addEventListener('click',e=>{const b=e.target.closest('[data-re]');if(!b)return;const x=LS.get('orders',[]).find(o=>o.id==b.dataset.re);x.items.forEach(i=>addCart(i.id,i.q));location.href='cart.html'});
draw();setInterval(draw,15000);
