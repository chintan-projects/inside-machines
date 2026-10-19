import { useEffect, useState } from "react";
import type { ReactElement } from "react";
import { Check, Download } from "lucide-react";
import type { Lesson, Member } from "./contracts";
import { errorMessage } from "./api";
import { savedLesson, saveLesson } from "./offline";

export function useLessonAssets(
  lesson: Lesson,
  member: Member,
  online: boolean,
): {
  saved: boolean;
  saving: boolean;
  saveError: string;
  setSaveError: (message: string) => void;
  videoUrl: string;
  captionUrl: string;
  save: () => Promise<void>;
} {
  const [saved, setSaved] = useState(false),
    [saving, setSaving] = useState(false),
    [saveError, setSaveError] = useState("");
  const [videoUrl, setVideoUrl] = useState(`/api/v1/lessons/${encodeURIComponent(lesson.id)}/video`);
  const [captionUrl, setCaptionUrl] = useState(`/api/v1/lessons/${encodeURIComponent(lesson.id)}/captions`);
  useEffect(() => {
    let cancelled = false;
    const urls: string[] = [];
    void savedLesson(member.id, lesson.id)
      .then((record) => {
        if (cancelled || !record) return;
        setSaved(true);
        if (!online && record.video) {
          const video = URL.createObjectURL(record.video);
          urls.push(video);
          setVideoUrl(video);
          const caption = URL.createObjectURL(
            new Blob([record.captions || "WEBVTT\n"], { type: "text/vtt" }),
          );
          urls.push(caption);
          setCaptionUrl(caption);
        }
      })
      .catch((error) => {
        if (!cancelled) setSaveError(errorMessage(error));
      });
    return () => {
      cancelled = true;
      urls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [member.id, lesson.id, online]);
  async function save(): Promise<void> {
    setSaving(true);
    setSaveError("");
    try {
      await saveLesson(member.id, lesson);
      setSaved(true);
    } catch (error) {
      setSaveError(errorMessage(error));
    } finally {
      setSaving(false);
    }
  }
  return {
    saved,
    saving,
    saveError,
    setSaveError,
    videoUrl: online ? `/api/v1/lessons/${encodeURIComponent(lesson.id)}/video` : videoUrl,
    captionUrl: online ? `/api/v1/lessons/${encodeURIComponent(lesson.id)}/captions` : captionUrl,
    save,
  };
}
export function LessonSaveButton({
  online,
  saved,
  saving,
  save,
}: {
  readonly online: boolean;
  readonly saved: boolean;
  readonly saving: boolean;
  readonly save: () => Promise<void>;
}): ReactElement {
  return (
    <button
      aria-label={saving ? "Saving lesson" : saved ? "Saved offline" : "Save offline"}
      className="save-button"
      disabled={!online || saving}
      onClick={() => void save()}
    >
      {saved ? <Check size={17} /> : <Download size={17} />}
      <span>{saving ? "Saving…" : saved ? "Saved offline" : "Save offline"}</span>
    </button>
  );
}
