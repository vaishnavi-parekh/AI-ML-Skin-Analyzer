$('#f').onsubmit=async e=>{e.preventDefault();const em=$('#e').value.trim().toLowerCase(),us=LS.get('users',[]);
if(us.some(x=>x.email==em)){$('#er').textContent='An account with this email already exists. Log in instead.';return}
us.push({name:$('#n').value.trim(),email:em,hash:await sha($('#p').value)});LS.set('users',us);LS.set('session',{name:$('#n').value.trim(),email:em});location.href='index.html'};
