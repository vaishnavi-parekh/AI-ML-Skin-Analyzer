function draw(){const c=LS.get('cart',{}),ids=Object.keys(c).filter(i=>PRODUCTS.some(p=>p.id==i));const w=$('#w');
if(!ids.length){w.innerHTML='<p class="mut" style="margin:16px 0">Your cart is empty.</p><a class="btn" href="shop.html">Start shopping</a>';return}
const t=totals(),pr=LS.get('promo',null);
w.innerHTML=`<div class="lay"><div class="panel">${ids.map(i=>{const p=PRODUCTS.find(x=>x.id==i);return `<div class="it"><div class="th" style="background:hsl(${p.h} 70% 85%)">${p.e}</div><div><b>${p.name}</b><br><small class="mut">${inr(p.price)}</small></div><div class="q"><button data-d="${i}" aria-label="Less">−</button>${c[i]}<button data-u="${i}" aria-label="More">+</button></div><b>${inr(p.price*c[i])}</b><button class="chip" data-r="${i}">Remove</button></div>`}).join('')}</div>
<div class="panel"><h2 style="margin-top:0">Summary</h2><div class="pr"><input id="pc" placeholder="Promo code" value="${pr||''}"><button class="btn sm" id="ap">Apply</button></div><p class="err" id="pe"></p>
<div class="sm2"><span>Subtotal</span><span>${inr(t.sub)}</span></div>${t.disc?`<div class="sm2"><span>Discount (${pr})</span><span>−${inr(t.disc)}</span></div>`:''}<div class="sm2"><span>Shipping</span><span>${t.ship?inr(t.ship):'Free'}</span></div><div class="sm2"><b>Total</b><b>${inr(t.total)}</b></div><p class="mut"><small>Free shipping over ₹999.</small></p><p><a class="btn rose" href="checkout.html">Checkout</a></p></div></div>`}
document.addEventListener('click',e=>{const c=LS.get('cart',{}),g=a=>e.target.closest(`[data-${a}]`)?.dataset[a];
if(g('u')){c[g('u')]++}else if(g('d')){if(--c[g('d')]<1)delete c[g('d')]}else if(g('r')){delete c[g('r')]}
else if(e.target.id=='ap'){const k=$('#pc').value.trim().toUpperCase();if(PROMOS[k]){LS.set('promo',k);toast('Promo applied')}else{$('#pe').textContent='That code is not valid. Try GLOW10.';return}}else return;
LS.set('cart',c);draw();$('#cb').textContent=totals().count});
draw();
