const s=LS.get('scan',null);let list;
if(s){$('#t1').textContent='Picked for you';list=recommend(s).slice(0,4).map(x=>card(x.p,x.m))}
else list=[...PRODUCTS].sort((a,b)=>b.rating-a.rating).slice(0,4).map(p=>card(p));
$('#g1').innerHTML=list.join('');
