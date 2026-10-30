import {heading,btn,bindActions} from '../core/ui.js';

export async function render(context){
 if(!['owner','manager'].includes(context.user.role))throw Error('Nemáte přístup k nastavení.');
 const query=new URLSearchParams(location.hash.split('?')[1]);
 const tab=context.route==='catalog'?'import':query.get('tab')==='new-vehicle'?'new-vehicle':'import';
 const tabs=`<nav class="settings-tabs" aria-label="Nastavení"><a class="button ${tab==='import'?'primary':''}" href="#settings?tab=import" ${tab==='import'?'aria-current="page"':''}>Import</a><a class="button ${tab==='new-vehicle'?'primary':''}" href="#settings?tab=new-vehicle" ${tab==='new-vehicle'?'aria-current="page"':''}>Nový vůz</a></nav>`;
 const title=heading('Nastavení','Nabídka vozidel a import dat.');
 if(tab==='import'){
  const module=await import('./catalog.js');
  const content=await module.render(context);
  return {html:title+tabs+content.html,bind:content.bind};
 }
 return {html:title+tabs+`<section class="card"><h2>Vytvořit novou nabídku vozidla</h2><p>Přidejte vůz, měsíční cenu a technické údaje. Fotografie nahrajete v detailu uloženého vozidla.</p><p class="notice">Nová nabídka může zůstat ve stavu K doplnění bez SPZ. Před přiřazením k pronájmu nebo převozu doplňte skutečné údaje.</p><div class="actions">${btn('new-vehicle','＋ Vytvořit nabídku','',true)}</div></section>`,bind(root){bindActions(root,{'new-vehicle':async()=>{
   const module=await import('./vehicles.js');
   module.createVehicleOffer(context.user,()=>{location.hash='vehicles'});
 }})}};
}
