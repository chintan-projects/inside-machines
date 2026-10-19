import { useState } from 'react';
import type { ReactElement } from 'react';

interface Check {
  readonly question: string;
  readonly options: readonly string[];
  readonly correct: number;
  readonly explanation: string;
  readonly chapter: number;
}
const checks: readonly Check[] = [
  { question:'What travels between the two units?', options:['Room air', 'Refrigerant in sealed tubing'], correct:1, explanation:'The two air streams stay separate. Refrigerant carries heat through the connecting tubes.', chapter:0 },
  { question:'Why can heat leave the outdoor coil on a hot day?', options:['The compressor makes the refrigerant hotter than outdoor air', 'The outdoor fan manufactures cold'], correct:0, explanation:'The compressor adds work. Heat can then flow from hotter refrigerant into the outdoor air.', chapter:2 },
  { question:'What happens inside the indoor coil?', options:['Refrigerant absorbs heat and boils into vapor', 'Refrigerant is used up as a fuel'], correct:0, explanation:'Boiling absorbs energy from room air. The refrigerant keeps circulating through its sealed loop.', chapter:1 },
];

export function AcLearningCheck({ onShow }: { readonly onShow: (chapter: number) => void }): ReactElement {
  const [answers, setAnswers] = useState<Record<number,number>>({});
  return <section className="learning-check" aria-label="Check your understanding"><p className="eyebrow">Make sure it makes sense</p><h2>Can you explain the cycle?</h2><p>Try these without replaying. Your choices stay in this page.</p>{checks.map((check,index) => <div className="check-question" key={check.question}><h3>{check.question}</h3><div>{check.options.map((option,choice) => <button key={option} aria-pressed={answers[index] === choice} onClick={() => setAnswers({...answers,[index]:choice})}>{option}</button>)}</div>{answers[index] !== undefined && <div className="check-result" aria-live="polite"><strong>{answers[index] === check.correct ? 'Yes.' : 'Revisit this part of the cycle.'}</strong><p>{check.explanation}</p><button onClick={() => onShow(check.chapter)}>Show this in the machine</button></div>}</div>)}</section>;
}
