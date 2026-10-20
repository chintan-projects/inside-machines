/** CE-1 data mirrors the validated versioned API; rendering never executes model code. */
export interface Pose { x:number; y:number; sx:number; sy:number; angle:number; fill:string; opacity:number }
export interface Change { target:string; before:Pose; after:Pose; via?:Pose[] }
export interface Property { name:string; before:string; after:string }
export interface Claim { id:string; statement:string; source:number; locator:string; scope:'generic'|'documented-model'|'inference'; limitation:string }
export interface Assessment { prompt:string; choices:string[]; correct:number; explanation:string; reasoning:string[]; misconception:string }
export interface Beat { id:string; stage:number; short:string; requires:string[]; claims:string[]; bridge:string; visible_change:string; static_explanation:string; action:string; graphics:string[]; changes:Change[]; properties:Property[] }
export interface Scenario { id:string; label:string; beat:string; kind:'qualitative'; context:'outside'|'inside'|'none'; outcome:string; explanation:string; claims:string[]; changes:Change[] }
export interface TeachingSpec { spec_version:'ce-1'; renderer:'ac-cutaway-v2'|'declarative'; renderer_fingerprint?:string; goal:string; misconception:string; core:string[]; operation:'simultaneous'|'sequential'|'controlled'; operation_note:string; invariants:string[]; claims:Claim[]; beats:Beat[]; prediction:Assessment; transfer:Assessment; teach_back:string; teach_back_reasoning:string[]; scenarios:Scenario[] }
