import { useState } from 'react';
import type { FormEvent, ReactElement } from 'react';
import { Box, ChevronRight } from 'lucide-react';
import { api, errorMessage } from './api';
import type { Member } from './contracts';
import { checkedMember } from './session';

export function Login({onLogin,owner=false}:{readonly onLogin:(member:Member)=>Promise<void>;readonly owner?:boolean}):ReactElement {
  const [name,setName]=useState(''),[code,setCode]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState('');
  async function login(event:FormEvent):Promise<void> {
    event.preventDefault();setBusy(true);setError('');
    try {
      const member=checkedMember(await api<unknown>('/auth/login',{name:name.trim(),code}));
      await onLogin(member);
      if(owner&&!member.owner)setError('That code does not open the owner workspace. You can still return to the library.');
    } catch(failure){setError(errorMessage(failure));}
    finally{setBusy(false);}
  }
  return <main id="main" tabIndex={-1} className="welcome"><div className="welcome-mark"><Box size={34} strokeWidth={1.5}/></div>
    <h1>{owner?'Owner workspace':<>Look inside.<br/>Understand what happens.</>}</h1>
    <p>{owner?'Manage requests, review explanations and control the library.':'Explore how things work, from everyday machines to computing.'}</p>
    <form onSubmit={event=>void login(event)} className="invite-form">
      <h2>{owner?'Owner sign-in':'Join the family alpha'}</h2><p className="muted">{owner?'Use your private owner code.':'Use the invite code shared with you.'}</p>
      <label>Your name<input autoComplete="given-name" required maxLength={60} value={name} onChange={e=>setName(e.target.value)} placeholder="What should we call you?"/></label>
      <label>{owner?'Owner code':'Invite code'}<input autoComplete="off" type="password" required maxLength={180} value={code} onChange={e=>setCode(e.target.value)}/></label>
      {error&&<p role="alert" className="error">{error}</p>}
      <button className="primary" disabled={busy||!name.trim()}>{busy?'Opening…':owner?'Open owner workspace':'Explore Inside'}<ChevronRight size={18}/></button>
      <small>{owner?'Owner actions remain protected.':'No customer API key needed. Your conversations stay private.'}</small>
    </form>{owner&&<p><a href="#/">Return to the library</a></p>}
  </main>;
}
