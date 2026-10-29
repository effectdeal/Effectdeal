import {request} from './api.js';
export const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const money=n=>new Intl.NumberFormat('cs-CZ',{style:'currency',currency:'CZK',maximumFractionDigits:2}).format(Number(n)||0);
export const roles={owner:'Majitel',manager:'Manager',dispatcher:'Dispečer',employee:'Zaměstnanec / řidič'};
export const statuses={unverified:'K doplnění',draft:'Koncept',submitted:'Čeká na schválení',approved:'Schváleno',rejected:'Zamítnuto',returned:'Vráceno k opravě',assigned:'Přiděleno',progress:'Probíhá',completed:'Dokončeno',available:'K dispozici',rented:'Zapůjčeno',service:'V servisu',reserved:'Rezervováno',active:'Aktivní',ended:'Ukončeno',issued:'Vystavena',paid:'Uhrazeno'};
export const badge=s=>`<span class="badge ${esc(s)}">${esc(statuses[s]||s)}</span>`;
export const heading=(title,sub,action='')=>`<header class="page-heading"><div><span class="eyebrow">EFFECT DEAL / PRACOVNÍ PROSTOR</span><h1>${esc(title)}</h1><p>${esc(sub)}</p></div>${action}</header>`;
export const btn=(action,label,id='',primary=false)=>`<button data-action="${action}" data-id="${esc(id)}" class="${primary?'primary':''}">${label}</button>`;
export function toast(message){const el=document.querySelector('#toast');el.textContent=message;el.classList.add('visible');setTimeout(()=>el.classList.remove('visible'),3500)}
export function field(label,name,value='',type='text',options=[]){return `<label>${esc(label)}${type==='textarea'?`<textarea name="${name}" maxlength="3000">${esc(value)}</textarea>`:type==='select'?`<select name="${name}">${options.map(o=>{const [v,l]=Array.isArray(o)?o:[o,o];return `<option value="${esc(v)}" ${String(value)===String(v)?'selected':''}>${esc(l)}</option>`}).join('')}</select>`:`<input name="${name}" type="${type}" value="${esc(value)}" ${type==='number'?'min="0" max="1000000" step="0.01"':''} ${['text','email','password'].includes(type)?'maxlength="200"':''}>`}</label>`}
export function modal(title,body,save){const dialog=document.querySelector('#dialog');dialog.innerHTML=`<form><div class="dialog-head"><h2>${esc(title)}</h2><button type="button" data-close aria-label="Zavřít">✕</button></div>${body}<p class="error" role="alert"></p><div class="form-actions"><button type="button" data-close>Zrušit</button>${save?'<button class="primary" type="submit">Uložit</button>':''}</div></form>`;dialog.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>dialog.close());dialog.querySelector('form').onsubmit=async e=>{e.preventDefault();if(!save)return;const button=e.submitter;button.disabled=true;try{await save(new FormData(e.target));dialog.close()}catch(error){dialog.querySelector('.error').textContent=error.message}finally{button.disabled=false}};if(!dialog.open)dialog.showModal();return dialog}
export function objectFrom(form,numbers=[]){const o=Object.fromEntries(form);for(const n of numbers)if(n in o)o[n]=Number(o[n]||0);return o}
export function simpleEditor(kind,title,row,fields,refresh){modal(title,`<div class="form-grid">${fields.map(f=>field(f.label,f.name,row?.[f.name]??f.default??'',f.type||'text',f.options||[])).join('')}</div>`,async form=>{const data=objectFrom(form,fields.filter(f=>f.type==='number').map(f=>f.name));if(row)data.version=row.version;await request('/'+kind+(row?'/'+row.id:''),{method:row?'PUT':'POST',data});toast('Uloženo');refresh()})}
export function table(headers,rows){return `<div class="table-scroll"><table><thead><tr>${headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.join(''):`<tr><td colspan="${headers.length}" class="empty">Zatím zde nejsou žádné záznamy.</td></tr>`}</tbody></table></div>`}
export function bindActions(root,handlers){root.addEventListener('click',async e=>{const b=e.target.closest('[data-action]');if(!b||!handlers[b.dataset.action])return;try{await handlers[b.dataset.action](b.dataset.id,b)}catch(error){toast(error.message)}})}
export function lookup(items,key='name'){return new Map(items.map(i=>[i.id,i[key]||i.plate||i.id]))}
export async function documents(kind,id,signal){const result=await request('/documents?limit=100&parentKind='+encodeURIComponent(kind)+'&parentId='+encodeURIComponent(id),{signal});return result.items}
export const isPhoto=file=>['image/jpeg','image/png','image/webp'].includes(file.mime);
export const photoUrl=id=>'/api/documents/'+encodeURIComponent(id)+'/file';
export function filePanel(files,kind,id,editable=true,options={}){
 const images=files.filter(isPhoto),other=files.filter(f=>!isPhoto(f));
 return `<section class="card photo-panel"><div class="section-head"><h2>${kind==='vehicles'?'Fotografie vozidla':'Fotografie a doklady'}</h2><small>${images.length} fotografií</small></div>
 <div class="photo-gallery">${images.map(f=>`<figure class="photo-tile ${options.profileId===f.id?'is-profile':''}"><button type="button" class="photo-open" data-photo="${esc(f.id)}" data-photo-name="${esc(f.name)}" aria-label="Zvětšit fotografii ${esc(f.name)}"><img src="${photoUrl(f.id)}" alt="${esc(f.name)}" loading="lazy" decoding="async"></button><figcaption><span>${esc(f.name)}</span>${kind==='vehicles'?(options.profileId===f.id?'<b class="profile-badge">✓ Profilová fotografie</b>':editable?`<button type="button" class="choose-profile" data-profile="${esc(f.id)}">Nastavit jako profilovou</button>`:''):''}</figcaption></figure>`).join('')}</div>
 ${other.length?`<div class="document-list">${other.map(f=>`<a href="${photoUrl(f.id)}?download=1">▤ ${esc(f.name)} · ${Math.round(f.size/1024)} kB</a>`).join('')}</div>`:''}
 ${!files.length?'<p class="empty">Zatím nebyly přidány žádné fotografie ani doklady.</p>':''}
 ${editable?`<label class="upload">${kind==='vehicles'?'Přidat fotografie vozu':'Přidat fotografie nebo doklady'} (do 10 MB za soubor)<input type="file" multiple data-upload data-kind="${kind}" data-parent="${esc(id)}" accept="${kind==='vehicles'?'image/jpeg,image/png,image/webp':'image/jpeg,image/png,image/webp,application/pdf'}"></label>`:''}</section>`
}
export function openPhotoViewer(photos,index=0){
 if(!photos.length)return;
 const opener=document.activeElement;
 const dialog=document.createElement('dialog');dialog.className='photo-viewer';dialog.setAttribute('aria-label','Prohlížeč fotografií');
 dialog.innerHTML=`<div class="photo-viewer-toolbar"><span data-caption></span><button type="button" data-close-photo aria-label="Zavřít fotografii">Zavřít ✕</button></div><div class="photo-viewer-stage"><button type="button" data-prev aria-label="Předchozí fotografie">‹</button><div class="photo-viewer-image"><img alt=""><p hidden>Fotografii nelze načíst. Zavřete náhled a obnovte stránku.</p></div><button type="button" data-next aria-label="Další fotografie">›</button></div><div class="photo-viewer-footer"><span data-counter aria-live="polite"></span><a data-download>Stáhnout originál ↓</a></div>`;
 const img=dialog.querySelector('img'),error=dialog.querySelector('.photo-viewer-image p');
 const paint=()=>{index=(index+photos.length)%photos.length;const photo=photos[index];img.hidden=false;error.hidden=true;img.alt=photo.name;img.src=photoUrl(photo.id);dialog.querySelector('[data-caption]').textContent=photo.name;dialog.querySelector('[data-counter]').textContent=(index+1)+' / '+photos.length;dialog.querySelector('[data-download]').href=photoUrl(photo.id)+'?download=1';dialog.querySelectorAll('[data-prev],[data-next]').forEach(b=>b.disabled=photos.length===1)};
 img.onerror=()=>{img.hidden=true;error.hidden=false};
 dialog.querySelector('[data-prev]').onclick=()=>{index--;paint()};dialog.querySelector('[data-next]').onclick=()=>{index++;paint()};dialog.querySelector('[data-close-photo]').onclick=()=>dialog.close();
 dialog.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();index+=e.key==='ArrowRight'?1:-1;paint()}});
 dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
 dialog.addEventListener('close',()=>{dialog.remove();opener?.focus()},{once:true});document.body.append(dialog);paint();dialog.showModal();
}
export function bindPhotos(root,onProfile){
 root.addEventListener('click',async e=>{
  const photo=e.target.closest('[data-photo]');
  if(photo){const all=[...new Map(Array.from(root.querySelectorAll('[data-photo]')).map(b=>[b.dataset.photo,{id:b.dataset.photo,name:b.dataset.photoName||'Fotografie vozidla'}])).values()];openPhotoViewer(all,all.findIndex(p=>p.id===photo.dataset.photo));return}
  const button=e.target.closest('[data-profile]');if(!button||!onProfile)return;
  button.disabled=true;try{await onProfile(button.dataset.profile)}catch(error){toast(error.message);button.disabled=false}
 });
}
export function bindUpload(root,refresh,options={}){
 bindPhotos(root,options.onProfile);
 root.querySelectorAll('[data-upload]').forEach(input=>input.onchange=async()=>{
  const files=Array.from(input.files||[]);if(!files.length)return;
  if(files.some(f=>f.size>10*1024*1024)){toast('Soubor může mít nejvýše 10 MB.');input.value='';return}
  input.disabled=true;let uploaded=0;
  try{for(const file of files){const data=new FormData();data.append('file',file);data.append('parentKind',input.dataset.kind);data.append('parentId',input.dataset.parent);await request('/documents/upload',{method:'POST',data});uploaded++}toast('Uloženo '+uploaded+' fotografií / příloh.');refresh()}
  catch(error){toast((uploaded?'Uloženo '+uploaded+' příloh. ':'')+error.message);if(uploaded)refresh();else{input.disabled=false;input.value=''}}
 })
}
