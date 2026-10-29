import {list,request,auth} from '../core/api.js';
import {heading,esc,money,roles,btn,table,badge,field,modal,toast,bindActions,documents,filePanel,bindUpload} from '../core/ui.js';

let uploadNotice='';
const managers=['owner','manager'];
const canEdit=(user,employee)=>managers.includes(user.role)&&(user.role==='owner'||employee?.role!=='owner');
const privateAccess=(user,employee)=>user.id===employee.id||canEdit(user,employee);

export async function render({route,id,signal,refresh,user}){
 if(route==='profile')id=user.id;
 if(id){
  const employee=await request('/employees/'+encodeURIComponent(id),{signal});
  const own=employee.id===user.id,privateFiles=privateAccess(user,employee);
  const files=privateFiles?await documents('employees',id,signal):[];
  return {html:heading(own?'Můj profil':employee.name,employee.position||roles[employee.role],canEdit(user,employee)?btn('edit','Upravit profil',id,true):'')+
   (route==='employees'?'<a class="back" href="#employees">← Zaměstnanci</a>':'')+
   (uploadNotice?`<p class="notice" role="status">${esc(uploadNotice)}</p>`:'')+
   `<div class="detail-grid"><section class="card"><h2>Osobní údaje</h2><dl>${[
    ['Jméno',employee.firstName],['Příjmení',employee.lastName],['Kontakt',employee.phone],['E-mail',employee.email],
    ['Uživatelské jméno',employee.username],['Pozice',employee.position||roles[employee.role]],['Přístupová role',roles[employee.role]],
    ['Hodinová sazba',money(employee.hourlyRate)+' / h'],['Dostupnost',employee.available?'Dostupný':'Nedostupný']
   ].map(([label,value])=>`<div><dt>${label}</dt><dd>${esc(value||'—')}</dd></div>`).join('')}</dl>
   <p class="note">Heslo se z bezpečnostních důvodů nezobrazuje.</p>${own?'<a class="button" href="#reports">Moje výkazy a pracovní historie →</a>':''}</section>
   <div>${privateFiles?filePanel(files,'employees',id,true):'<section class="card"><h2>Osobní dokumenty</h2><p>Dokumenty jsou přístupné zaměstnanci a oprávněné správě účtů.</p></section>'}
   <p class="note">Dokumenty jsou nepovinné. Můžete přiložit například řidičský průkaz. Doklady se nezobrazují ostatním zaměstnancům ani dispečerovi.</p></div></div>`,
   bind(root){uploadNotice='';bindUpload(root,refresh);bindActions(root,{edit:()=>editor(employee,user,refresh)})}};
 }
 const page=new URLSearchParams(location.hash.split('?')[1]).get('page')||'1';
 const offset=Math.max(0,(Number(page)||1)-1)*50;
 const result=await request('/employees?limit=50&offset='+offset,{signal});
 const rows=result.items.map(employee=>`<tr><td><a href="#employees/${employee.id}"><b>${esc(employee.name)}</b></a><small>${esc(employee.username)}</small></td><td>${esc(employee.phone||'—')}<small>${esc(employee.email)}</small></td><td>${esc(employee.position||roles[employee.role])}</td><td>${money(employee.hourlyRate)} / h</td><td>${employee.available?'Dostupný':'Nedostupný'}</td><td><a href="#employees/${employee.id}">Profil ↗</a></td></tr>`);
 return {html:heading('Zaměstnanci','Profily, přihlašovací údaje, osobní dokumenty a hodinové sazby.',canEdit(user)?btn('new','＋ Vytvořit profil','',true):'')+
 `<section class="card">${table(['Zaměstnanec','Kontakt','Pozice','Sazba','Dostupnost',''],rows)}</section><div class="actions">${offset?`<a class="button" href="#employees?page=${Math.floor(offset/50)}">← Předchozí</a>`:''}<span>${result.total} zaměstnanců</span>${offset+50<result.total?`<a class="button" href="#employees?page=${Math.floor(offset/50)+2}">Další →</a>`:''}</div>`,
 bind(root){bindActions(root,{new:()=>editor(null,user,refresh)})}};
}

function editor(employee,user,refresh){
 const title=employee?'Upravit profil':'Vytvořit profil';
 const fields=[['Jméno','firstName'],['Příjmení','lastName'],['Kontakt / telefon','phone','tel'],['E-mail','email','email'],['Uživatelské jméno pro přihlášení','username'],['Heslo (nejméně 12 znaků)','password','password'],['Název pozice (např. řidič, technik)','position']];
 const body=`<div class="form-grid">${fields.map(([label,key,type])=>field(label,key,key==='password'?'':employee?.[key]||'',type)).join('')}${field('Přístupová role','role',employee?.role||'employee','select',Object.entries(roles).filter(([key])=>user.role==='owner'||key!=='owner'))}${field('Hodinová sazba (Kč/h)','hourlyRate',employee?.hourlyRate||0,'number')}${field('Dostupnost','available',employee?.available??true,'select',[['true','Dostupný'],['false','Nedostupný']])}${field('Potvrzená GPS šířka','latitude',employee?.latitude??'')}${field('Potvrzená GPS délka','longitude',employee?.longitude??'')}${field('Poloha potvrzena','locationConfirmedAt',employee?.locationConfirmedAt||'','datetime-local')}</div>
  <p class="note">Role Zaměstnanec / řidič má pouze vlastní úkoly, výkazy a historii. Název pozice tato oprávnění nerozšiřuje.${employee?' Prázdné heslo ponechá stávající heslo.':''}</p>
  <label class="upload">Osobní dokumenty (nepovinné)<input name="profileDocuments" type="file" multiple accept="image/jpeg,image/png,image/webp,application/pdf"></label><p class="note">JPG, PNG, WebP nebo PDF; nejvýše 10 MB za soubor, 10 dokumentů u profilu. Profil lze vytvořit bez dokumentů.</p>`;
 const dialog=modal(title,body,async form=>{
  const files=form.getAll('profileDocuments').filter(f=>f.size>0);
  if(files.length>10||files.some(f=>f.size>10*1024*1024))throw Error('Nejvýše 10 dokumentů, každý do 10 MB.');
  const data=Object.fromEntries([...form].filter(([key])=>key!=='profileDocuments'));
  data.hourlyRate=Number(data.hourlyRate||0);if(employee)data.version=employee.version;
  const saved=await request('/employees'+(employee?'/'+employee.id:''),{method:employee?'PUT':'POST',data});
  if(saved.id===auth.user.id)auth.user=saved;
  let count=0;uploadNotice='';
  try{for(const file of files){const data=new FormData();data.append('file',file);data.append('parentKind','employees');data.append('parentId',saved.id);await request('/documents/upload',{method:'POST',data});count++}}
  catch(error){uploadNotice=`Profil byl uložen. Přidáno ${count} z ${files.length} dokumentů. ${error.message} Zbývající dokumenty přidejte zde v profilu.`}
  toast(uploadNotice?'Profil uložen; zkontrolujte zprávu u dokumentů.':'Profil uložen.');
  const destination='employees/'+saved.id;
  if(location.hash==='#'+destination||location.hash==='#profile')refresh();else location.hash=destination;
 });
 for(const key of ['firstName','lastName','phone','email','username'])dialog.querySelector(`[name="${key}"]`).required=true;
 const password=dialog.querySelector('[name="password"]');password.required=!employee;password.minLength=12;password.autocomplete='new-password';
 dialog.querySelector('[name="username"]').autocomplete='off';
}
