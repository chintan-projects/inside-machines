import type { Conversation } from './contracts';

export class ApiError extends Error {
  constructor(message: string, readonly status: number) { super(message); }
}

export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method: body === undefined ? 'GET' : 'POST', credentials: 'same-origin',
    headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const data: unknown = await response.json().catch(() => null);
    const detail = data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string'
      ? data.detail : 'We couldn’t complete that request. Please try again.';
    if (response.status === 401 && path !== '/auth/login') window.dispatchEvent(new Event('inside:unauthorized'));
    throw new ApiError(detail, response.status);
  }
  return response.json() as Promise<T>;
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.';
}

export async function askChat(id: string, question: string, onStatus: (status: string) => void): Promise<Conversation> {
  const response = await fetch(`/api/v1/chats/${encodeURIComponent(id)}/messages`, {
    method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, operation: crypto.randomUUID() }),
  });
  if (!response.ok || !response.body) throw new ApiError('Couldn’t open this conversation. Sign in again if your session expired.', response.status);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '', answer: Conversation | null = null;
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let boundary: number;
      while ((boundary = buffer.indexOf('\n\n')) !== -1) {
        const event = buffer.slice(0, boundary); buffer = buffer.slice(boundary + 2);
        const kind = event.match(/^event: (.+)$/m)?.[1];
        const raw = event.match(/^data: (.+)$/m)?.[1];
        if (!raw) continue;
        if (kind === 'answer') answer = JSON.parse(raw) as Conversation;
        else if (kind === 'error') throw new Error((JSON.parse(raw) as { message: string }).message);
        else if (kind === 'status') onStatus((JSON.parse(raw) as { message: string }).message);
      }
      if (done) break;
    }
  } finally { reader.releaseLock(); }
  if (!answer) throw new Error('The reply was interrupted. Reopen your chat to check before sending again.');
  return answer;
}
