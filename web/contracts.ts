/** Versioned provider-independent, non-executable teaching artifact. */
import type { TeachingSpec } from './teaching/contracts';
export interface Motion { stage: number; kind: 'rotate' | 'translate' | 'pulse' | 'flow'; amount: number; axis: 'x' | 'y' }
export interface Part {
  id: string; name: string; description: string;
  shape: 'box' | 'ellipse' | 'ring' | 'path' | 'polygon' | 'text';
  x: number; y: number; w: number; h: number; color: string; stroke: string;
  points: number[][]; label: string; layer: number; motion: Motion[];
}
export interface Stage { title: string; explanation: string; narration: string; duration: number; parts: string[]; cause: string; input_state?: string; output_state?: string; focus?: string; source_indices?: number[] }
export interface LessonSpec {
  version: 1|2; title: string; canonical: string; aliases: string[]; family: string;
  question: string; summary: string; big_idea: string; category: string; accent: string;
  assumptions: string[]; sources: { title: string; url: string; supports: string }[];
  parts: Part[]; stages: Stage[];
  questions: { question: string; answer: string; stage: number; part: string }[];
  prediction: string; prediction_answer: string;
  teaching?: TeachingSpec|null; graphics?:Part[];
}
export interface Member { id: string; name: string; owner: boolean }
export interface Feedback { value: 'up' | 'down'; reason: string }
export interface Lesson { id: string; spec: LessonSpec; quality: string; review_needed?: boolean; superseded_by?: string | null; video_ready: boolean; feedback: Feedback | null }
export interface CatalogEntry {
  id: string; title: string; canonical: string; family: string; question: string;
  summary: string; category: string; accent: string; duration: number; parts: number;
  quality: string; review_needed?: boolean; created_at: number; views: number; video_ready: boolean; preview: LessonSpec;
}
export interface Job { pipeline_version?: 'evidence-first-1' | null; id: string; canonical: string; status: string; phase: string; message: string; error: string | null; lesson_id?: string }
export interface RequestResult { kind: 'lesson' | 'job' | 'unavailable' | 'budget' | 'specific'; lesson_id?: string; job_id?: string; message?: string; reused?: boolean }
export interface Answer { answer: string; stage: number | null; part: string | null; source_indices: number[]; uncertain: boolean }
export interface Conversation { id: string; lesson_id: string; messages: { role: string; text: string; answer?: Answer | null; at: number }[]; pending: string }
export interface OwnerReport {
  generation_reserve_usd:number;
  budget_usd: number; spent_usd: number; reserved_usd: number; remaining_usd: number;
  generation_enabled: boolean; lesson_count: number;
  events: { kind: string; user_id?: string; at: number; question?: string; canonical?: string; lesson_id?: string }[];
  feedback: (Feedback & { user_id: string; lesson_id: string; stage?: number | null })[];
  jobs: Job[];
  ledger: { operation: string; input_tokens: number; output_tokens: number; charged_usd: number; uncertain: boolean; speech_estimated: boolean }[];
  members: { id: string; name: string }[];
}
