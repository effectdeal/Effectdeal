let csrf='';let user=null;let cacheEpoch=0;const cache=new Map();
export const auth={get user(){return user},set user(value){clearCache();user=value},mode:'demo'};
export function clearCache(){cache.clear();cacheEpoch++}
export async function request(path,{method='GET',data,signal,fresh=false}={}){
 const epoch=cacheEpoch,key=path;const hit=cache.get(key);if(method==='GET'&&!fresh&&hit&&Date.now()-hit.at<30000)return structuredClone(hit.data);
 const multipart=data instanceof FormData;
 const response=await fetch('/api'+path,{method,signal,credentials:'same-origin',headers:{...(data&&!multipart?{'Content-Type':'application/json'}:{}),...(method!=='GET'?{'X-CSRF-Token':csrf}:{})},body:data?(multipart?data:JSON.stringify(data)):undefined});
 const result=await response.json().catch(()=>({error:'Server nevrátil platnou odpověď.'}));
 if(!response.ok){if(response.status===401&&path!=='/login')window.dispatchEvent(new Event('session-expired'));throw new Error(result.error||'Požadavek se nezdařil.')}
 if(result.csrf)csrf=result.csrf;
 if(method==='GET'&&path!=='/session'&&epoch===cacheEpoch)cache.set(key,{at:Date.now(),data:result});else if(method!=='GET')clearCache();
 return result;
}
export async function session(){const s=await request('/session',{fresh:true});user=s.user;auth.mode=s.mode;return s}
export const list=(kind,signal,params='')=>request('/'+kind+'?limit=100'+params,{signal});
