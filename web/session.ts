/** Public visitors get a unique server session; owner/member sessions are preserved. */
import { api, ApiError } from './api.ts';
import type { Member } from './contracts';

export interface AccessSession { readonly publicAccess:boolean; readonly member:Member|null }
export type SessionRequest=(path:string,body?:unknown)=>Promise<unknown>;

export function checkedMember(value:unknown):Member {
  if(!value||typeof value!=='object'||!('id' in value)||typeof value.id!=='string'||!value.id||value.id.length>128||
    !('name' in value)||typeof value.name!=='string'||!value.name.trim()||value.name.length>60||
    !('owner' in value)||typeof value.owner!=='boolean'||
    ('guest' in value&&typeof value.guest!=='boolean')||('guest' in value&&value.guest&&value.owner)) {
    throw new Error('Inside returned an invalid browser session. Please try opening it again.');
  }
  return {id:value.id,name:value.name,owner:value.owner,guest:'guest' in value&&value.guest===true};
}

/** No write/chat is retried here. Only authentication is opened or renewed. */
export async function openSession(request:SessionRequest=api,revokePending=false):Promise<AccessSession> {
  const health=await request('/health');
  if(!health||typeof health!=='object'||('public_access' in health&&typeof health.public_access!=='boolean')) {
    throw new Error('Inside could not confirm access. Please try opening it again.');
  }
  const publicAccess='public_access' in health&&health.public_access===true;
  if(revokePending) {
    try {await request('/auth/logout',{});}
    catch(error){if(!(error instanceof ApiError&&error.status===401))throw error;}
  }
  try {
    const member=checkedMember(await request(publicAccess?'/auth/guest':'/auth/me',publicAccess?{}:undefined));
    return {publicAccess,member};
  } catch(error) {
    if(!publicAccess&&error instanceof ApiError&&error.status===401)return {publicAccess:false,member:null};
    throw error;
  }
}

export type EntryPage='opening'|'owner-login'|'owner'|'join'|'unavailable'|'offline'|'content';
export function entryPage(path:string,member:Member|null,publicAccess:boolean|null,loading:boolean,online:boolean,failed=false):EntryPage {
  if(loading)return 'opening';
  if(path==='owner/login')return member?.owner&&online?'owner':online?'owner-login':'offline';
  if(!member)return !online?'offline':failed?'unavailable':publicAccess===false?'join':'unavailable';
  if(path==='owner')return !online?'offline':member.owner?'owner':'owner-login';
  return 'content';
}
