import { useCallback, useEffect, useRef, useState } from "react";
import type { RefObject } from "react";
import type { Lesson, Member } from "../contracts";
import { offlineMember } from "../offline";
import { duration, stageAt } from "../lessonTimeline";
import { progressKey, readProgress } from "../progress";

export function useMedia(query: string): boolean {
  const [matches, setMatches] = useState(() => matchMedia(query).matches);
  useEffect(() => {
    const media = matchMedia(query);
    const change = (): void => setMatches(media.matches);
    media.addEventListener("change", change);
    return () => media.removeEventListener("change", change);
  }, [query]);
  return matches;
}
interface Guide {
  step: number;
  seconds: number;
  listening: boolean;
  loading: boolean;
  motion: boolean;
  error: string;
  jump: (step: number) => void;
  listen: () => Promise<void>;
  time: (seconds: number) => void;
  pause: () => void;
  stopped: () => void;
  toggleMotion: () => void;
  initialTime: () => number;
}
export function useGuide(
  lesson: Lesson,
  member: Member,
  audioRef: RefObject<HTMLAudioElement | null>,
): Guide {
  const key = progressKey(member.id, lesson.id),
    total = duration(lesson.spec);
  const [initial] = useState(() =>
    readProgress(
      key,
      total,
      lesson.spec.parts.map((p) => p.id),
    ),
  );
  const [seconds, setSeconds] = useState(initial.seconds),
    [listening, setListening] = useState(false),
    [motion, setMotion] = useState(false),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false);
  const clock = useRef(initial.seconds),
    attemptRef = useRef(0);
  useEffect(() => {
    const player = audioRef.current;
    return () => {
      attemptRef.current += 1;
      player?.pause();
    };
  }, [audioRef]);
  const [step] = stageAt(lesson.spec, seconds);
  const persist = useCallback(() => {
    if (offlineMember()?.id !== member.id) return;
    try {
      localStorage.setItem(
        key,
        JSON.stringify({
          seconds: clock.current,
          selected: lesson.spec.stages[stageAt(lesson.spec, clock.current)[0]].focus,
          mode: "explore",
          speed: 1,
        }),
      );
    } catch {
      setError("Your browser could not save your place. The explanation still works.");
    }
  }, [key, member.id, lesson.spec]);
  useEffect(() => {
    const interval = window.setInterval(persist, 1000);
    window.addEventListener("pagehide", persist);
    return () => {
      window.clearInterval(interval);
      window.removeEventListener("pagehide", persist);
      persist();
    };
  }, [persist]);
  function time(value: number): void {
    clock.current = value;
    setSeconds(value);
  }
  function stopped(): void {
    setListening(false);
  }
  function pause(): void {
    attemptRef.current += 1;
    audioRef.current?.pause();
    setListening(false);
    setLoading(false);
  }
  function jump(index: number): void {
    pause();
    const at = lesson.spec.stages.slice(0, index).reduce((n, s) => n + s.duration, 0);
    time(at);
    const player = audioRef.current;
    if (player) player.currentTime = at;
    setMotion(index !== 0);
    setError("");
  }
  async function listen(): Promise<void> {
    if (listening) {
      pause();
      return;
    }
    if (!audioRef.current) return;
    if (clock.current >= total - 0.1) jump(0);
    setError("");
    setLoading(true);
    const attempt = ++attemptRef.current;
    try {
      await audioRef.current.play();
      if (attempt === attemptRef.current) {
        setListening(true);
        setMotion(true);
      }
    } catch {
      if (attempt === attemptRef.current)
        setError(
          "Narration could not play. You can still step through the machine, or reconnect and try again.",
        );
    } finally {
      if (attempt === attemptRef.current) setLoading(false);
    }
  }
  return {
    step,
    seconds,
    listening,
    loading,
    motion,
    error,
    jump,
    listen,
    time,
    pause,
    stopped,
    toggleMotion: () => setMotion(!motion),
    initialTime: () => clock.current,
  };
}
