import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactElement } from "react";
import { MessageCircle, Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { api, askChat, errorMessage } from "./api";
import type { Answer, Conversation, Feedback, Lesson, Member } from "./contracts";
interface Props {
  readonly lesson: Lesson;
  readonly member: Member;
  readonly online: boolean;
}

export function FeedbackPanel({
  lesson,
  online,
  stage,
}: {
  readonly lesson: Lesson;
  readonly online: boolean;
  readonly stage: number;
}): ReactElement {
  const [feedback, setFeedback] = useState<Feedback | null>(lesson.feedback),
    [reason, setReason] = useState(lesson.feedback?.reason || "");
  const [busy, setBusy] = useState(false),
    [status, setStatus] = useState(""),
    [error, setError] = useState("");
  async function vote(value: "up" | "down", text = reason): Promise<void> {
    setBusy(true);
    setError("");
    try {
      await api(`/lessons/${encodeURIComponent(lesson.id)}/feedback`, { value, reason: text, stage });
      setFeedback({ value, reason: text });
      setStatus("Thanks. Your feedback is saved.");
    } catch (error) {
      setError(errorMessage(error));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="feedback">
      <h3>Did this help you understand?</h3>
      <div className="vote-buttons">
        <button
          disabled={!online || busy}
          aria-pressed={feedback?.value === "up"}
          onClick={() => void vote("up")}
        >
          <ThumbsUp size={18} />
          Yes, it helped
        </button>
        <button
          disabled={!online || busy}
          aria-pressed={feedback?.value === "down"}
          onClick={() => void vote("down")}
        >
          <ThumbsDown size={18} />
          Not quite
        </button>
      </div>
      {feedback && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void vote(feedback.value);
          }}
        >
          <label>
            What worked, or what was confusing? <span className="muted">Optional</span>
            <textarea maxLength={600} rows={2} value={reason} onChange={(e) => setReason(e.target.value)} />
          </label>
          <button disabled={!online || busy}>Save a note</button>
        </form>
      )}
      {status && (
        <p role="status" className="muted">
          {status}
        </p>
      )}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
    </section>
  );
}

interface ChatProps extends Props {
  readonly onShow: (answer: Answer) => void;
}
export function ChatPanel({ lesson, member, online, onShow }: ChatProps): ReactElement {
  const [chat, setChat] = useState<Conversation | null>(null),
    [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false),
    [status, setStatus] = useState(""),
    [error, setError] = useState("");
  const [suggestion, setSuggestion] = useState<number | null>(null);
  const key = `inside.chat.${member.id}.${lesson.id}`;
  const historyEnd = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const id = sessionStorage.getItem(key);
    if (!id || !online) return;
    let cancelled = false;
    void api<Conversation>(`/chats/${encodeURIComponent(id)}`)
      .then((result) => {
        if (!cancelled) setChat(result);
      })
      .catch((error) => {
        if (!cancelled) setError(errorMessage(error));
      });
    return () => {
      cancelled = true;
    };
  }, [key, online]);
  useEffect(() => {
    if (chat?.messages.length) historyEnd.current?.scrollIntoView({ block: "nearest" });
  }, [chat]);
  async function send(event: FormEvent): Promise<void> {
    event.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    setStatus("Opening your private conversation…");
    try {
      const current = chat || (await api<Conversation>("/chats", { lesson_id: lesson.id }));
      sessionStorage.setItem(key, current.id);
      setChat(current);
      const result = await askChat(current.id, question.trim(), setStatus);
      setChat(result);
      setQuestion("");
    } catch (error) {
      setError(errorMessage(error));
    } finally {
      setBusy(false);
      setStatus("");
    }
  }
  return (
    <section className="chat-panel" aria-label="Lesson questions">
      <div className="chat-heading">
        <MessageCircle size={21} />
        <div>
          <h2>Keep asking</h2>
          <p>Start with a question, or follow your curiosity.</p>
        </div>
      </div>
      <div className="suggested-questions">
        {lesson.spec.questions.map((q, i) => (
          <button
            key={q.question}
            aria-expanded={suggestion === i}
            onClick={() => setSuggestion(suggestion === i ? null : i)}
          >
            {q.question}
          </button>
        ))}
      </div>
      {suggestion !== null && (
        <div className="suggested-answer">
          <p>{lesson.spec.questions[suggestion].answer}</p>
          <button
            onClick={() => {
              const q = lesson.spec.questions[suggestion];
              onShow({
                answer: q.answer,
                stage: q.stage,
                part: q.part || null,
                source_indices: [],
                uncertain: false,
              });
            }}
          >
            Show me in the explanation
          </button>
          <small>Included with this lesson · works offline</small>
        </div>
      )}
      <div className="chat-messages" aria-live="polite">
        {chat?.messages.map((message, i) => (
          <div key={`${message.at}-${i}`} className={`chat-message ${message.role}`}>
            <strong>{message.role === "user" ? "You" : "Inside"}</strong>
            <p>{message.text}</p>
            {message.answer?.uncertain && (
              <small>This answer has uncertainty. Check the lesson’s sources.</small>
            )}
            {message.answer && (message.answer.stage !== null || message.answer.part) && (
              <button onClick={() => onShow(message.answer!)}>Show me</button>
            )}
            {message.answer && message.answer.source_indices.length > 0 && (
              <div className="answer-sources">
                {message.answer.source_indices.map((index) => (
                  <a key={index} href={lesson.spec.sources[index]?.url} target="_blank" rel="noreferrer">
                    Source {index + 1}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={historyEnd} />
      </div>
      <form className="chat-form" onSubmit={(event) => void send(event)}>
        <label htmlFor="followup">
          Ask a follow-up
          <textarea
            id="followup"
            required
            minLength={3}
            maxLength={700}
            rows={2}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What would happen if…"
            disabled={!online || busy}
          />
        </label>
        <button className="primary" disabled={!online || busy || question.trim().length < 3}>
          <Send size={17} />
          {busy ? "Preparing reply…" : "Ask Inside"}
        </button>
      </form>
      {status && (
        <p role="status" className="muted">
          {status}
        </p>
      )}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      <small className="chat-privacy">
        Your chat is private. Live replies use the alpha’s AI budget and don’t change the shared lesson.
      </small>
    </section>
  );
}
