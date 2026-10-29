let cat='All';const cats=['All','Skincare','Makeup','Haircare','Fragrance','Wishlist'];
$('#cats').innerHTML=cats.map(c=>`<button class="chip ${c==cat?'on':''}" data-c="${c}">${c}</button>`).join('');
function draw(){const q=$('#q').value.toLowerCase(),w=LS.get('wish',[]);let l=PRODUCTS.filter(p=>(cat=='All'||(cat=='Wishlist'?w.includes(p.id):p.cat==cat))&&(p.name+p.desc).toLowerCase().includes(q));
const so=$('#so').value;if(so=='pa')l.sort((a,b)=>a.price-b.price);if(so=='pd')l.sort((a,b)=>b.price-a.price);if(so=='r')l.sort((a,b)=>b.rating-a.rating);
$('#g').innerHTML=l.map(p=>card(p)).join('');$('#none').hidden=l.length>0}
$('#cats').onclick=e=>{const b=e.target.closest('[data-c]');if(!b)return;cat=b.dataset.c;$$('#cats .chip').forEach(c=>c.classList.toggle('on',c==b));draw()};
$('#q').oninput=draw;$('#so').onchange=draw;draw();
