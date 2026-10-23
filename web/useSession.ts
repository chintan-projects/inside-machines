import { useCallback, useEffect, useRef, useState } from 'react';
import { api, errorMessage } from './api';
import type { Member } from './contracts';
import { clearOffline, offlineMember, rememberMember } from './offline';
import { checkedMember, openSession } from './session';

function savedPublicAccess():boolean|null {
  try {const saved=localStorage.getItem('inside.public-access');return saved==='true'?true:saved==='false'?false:null;}
  catch{return null;}
}

export function useSession(online:boolean):{
  member:Member|null;publicAccess:boolean|null;loading:boolean;error:string;notice:string;
  retry:()=>void;adopt:(member:Member)=>Promise<void>;logout:()=>Promise<void>;
} {
  const [member,setMember]=useState<Member|null>(null),[publicAccess,setPublicAccess]=useState(()=>online?null:savedPublicAccess());
  const [loading,setLoading]=useState(true),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const [attempt,setAttempt]=useState(0),renewing=useRef(false);
  const retry=useCallback(()=>{setLoading(true);setAttempt(value=>value+1);},[]);
  const adopt=useCallback(async(value:Member):Promise<void>=>{
    const next=checkedMember(value),previous=offlineMember();
    if(previous&&previous.id!==next.id)await clearOffline();
    try {rememberMember(next);}
    catch{setNotice('This browser could not keep your place or offline profile. Online explanations still work.');}
    setMember(next);setError('');setLoading(false);
  },[]);

  useEffect(()=>{
    const expired=():void=>{
      if(renewing.current)return;
      setNotice('Your browser session ended. Inside is reopening; your last action was not automatically retried.');
      setMember(null);retry();
    };
    window.addEventListener('inside:unauthorized',expired);
    return()=>window.removeEventListener('inside:unauthorized',expired);
  },[retry]);

  useEffect(()=>{
    let cancelled=false;renewing.current=true;
    async function restore():Promise<void> {
      try {
        if(!online) {
          if(!cancelled){setMember(offlineMember());setError('');}
          return;
        }
        let pending=false;
        try{pending=localStorage.getItem('inside.revoke-pending')==='1';}
        catch{setNotice('Offline access is unavailable in this browser. Online explanations still work.');}
        const session=await openSession(undefined,pending);
        if(cancelled)return;
        if(pending)localStorage.removeItem('inside.revoke-pending');
        setPublicAccess(session.publicAccess);
        try{localStorage.setItem('inside.public-access',String(session.publicAccess));}
        catch{setNotice('Offline access is unavailable in this browser. Online explanations still work.');}
        if(session.member)await adopt(session.member);
        else {
          if(offlineMember())await clearOffline();
          localStorage.removeItem('inside.member');setMember(null);setError('');
        }
      } catch(failure) {
        if(!cancelled)setError(errorMessage(failure));
      } finally {if(!cancelled){setLoading(false);renewing.current=false;}}
    }
    void restore();
    return()=>{cancelled=true;};
  },[online,attempt,adopt]);

  const logout=useCallback(async():Promise<void>=>{
    localStorage.setItem('inside.revoke-pending','1');
    if(online){await api('/auth/logout',{});localStorage.removeItem('inside.revoke-pending');}
    await clearOffline();localStorage.removeItem('inside.member');
    setMember(null);setNotice('');setError('');retry();
  },[online,retry]);
  return {member,publicAccess,loading,error,notice,retry,adopt,logout};
}
