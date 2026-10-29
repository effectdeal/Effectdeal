import {request} from '../core/api.js';
import {heading,table,esc,money,btn,bindActions,toast} from '../core/ui.js';

export async function render({signal,user}){
 const catalog=await request('/catalog/effectdeal',{signal});
 return {html:heading('Nabídka z effectdeal.com','Převod veřejné nabídky do vozového parku.',btn('import','Převést celou nabídku','',true))+
 `<a href="#vehicles" class="back">← Vozový park</a><section class="card"><h2>${catalog.items.length} nabídek · ${catalog.items.reduce((n,r)=>n+r.photoCount,0)} fotografií</h2><p>Stav webu k ${esc(new Date(catalog.fetchedAt).toLocaleString('cs-CZ'))}. Přenesou se popisy, technické údaje, výbava, měsíční ceny a fotografie.</p><p class="notice">Po importu doplňte skutečnou SPZ, VIN a ověřte dostupnost. Nabídka na webu může zahrnovat více kusů stejného modelu. Vytvoří se jedna karta na nabídku se stavem „K doplnění“.</p><p>Opakované spuštění zachová vaše úpravy i vybranou profilovou fotografii a doplní chybějící fotografie z balíčku.</p><p id="import-progress" role="status" aria-live="polite"></p></section>
 <section class="card">${table(['Vozidlo','Rok','Cena / měsíc','Fotografií','Stav'],catalog.items.map(v=>`<tr><td><a href="${esc(v.sourceUrl)}" target="_blank" rel="noopener">${esc(v.brand+' '+v.model)} ↗</a></td><td>${v.year??'—'}</td><td>${v.monthlyPrice==null?'Neuvedena':money(v.monthlyPrice)}</td><td>${v.photoCount}</td><td data-import-id="${esc(v.sourceSlug)}">${v.imported?`<a href="#vehicles/${esc(v.id)}">Ve vozovém parku ↗</a>`:'Připraveno k importu'}</td></tr>`))}</section>`,
 bind(root){bindActions(root,{import:async(_,button)=>{
  button.disabled=true;const progress=root.querySelector('#import-progress');let created=0,photos=0,skipped=0;const failed=[];
  for(let i=0;i<catalog.items.length;i++){
   const item=catalog.items[i];progress.textContent=`Převádím ${i+1} / ${catalog.items.length}: ${item.brand} ${item.model}…`;
   const cell=root.querySelector(`[data-import-id="${CSS.escape(item.sourceSlug)}"]`);
   try{const result=await request('/catalog/effectdeal/'+encodeURIComponent(item.sourceSlug)+'/import',{method:'POST',data:{}});created+=Number(result.created);photos+=result.addedPhotos;skipped+=result.skippedPhotos;cell.innerHTML=`<a href="#vehicles/${esc(result.vehicleId)}">Převedeno ↗</a>`}
   catch(error){failed.push(item.brand+' '+item.model+': '+error.message);cell.textContent='Nepodařilo se převést';}
  }
  progress.textContent=`Přidáno ${created} nabídek a ${photos} fotografií.${skipped?' '+skipped+' fotografií přeskočeno kvůli limitu 10 na vůz.':''}${failed.length?' Některé nabídky se nepodařilo převést: '+failed.join('; ')+'. Spusťte import znovu.':' Nabídka je připravená ve vozovém parku.'}`;
  toast(failed.length?'Import vyžaduje kontrolu.':'Nabídka byla převedena.');button.disabled=false;button.textContent='Zkontrolovat / doplnit import';
 }})}};
}
