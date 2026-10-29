const nx=new URLSearchParams(location.search).get('next')||'index.html';
$('#f').onsubmit=async e=>{e.preventDefault();const em=$('#e').value.trim().toLowerCase(),u=LS.get('users',[]).find(x=>x.email==em);
if(!u||u.hash!=await sha($('#p').value)){$('#er').textContent='Email or password is incorrect.';return}
LS.set('session',{name:u.name,email:u.email});location.href=nx};
