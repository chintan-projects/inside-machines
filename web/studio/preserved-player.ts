import type { Lesson } from '../contracts';
import type { StudioAPI } from './contracts';

/** Keep historical media readable when its exact trusted renderer is unavailable. */
export function mountPreservedLesson(root: HTMLElement, lesson: Lesson, source: string, captions?: string): StudioAPI {
  const notice = document.createElement('p');
  notice.textContent = 'This earlier revision is preserved in its original video and text. Its drawing is not recreated with a different renderer.';
  root.append(notice);
  const video = lesson.video_ready ? document.createElement('video') : undefined;
  if (video) {
    video.src = source; video.controls = true; video.playsInline = true; video.preload = 'metadata';
    if (captions) {
      const track = document.createElement('track'); track.kind = 'captions'; track.src = captions;
      track.srclang = 'en'; track.label = 'English captions'; video.append(track);
    }
    video.style.width = '100%'; root.append(video);
  }
  lesson.spec.stages.forEach(stage => {
    const section = document.createElement('section'), heading = document.createElement('h2'), text = document.createElement('p');
    heading.textContent = stage.title; text.textContent = stage.narration; section.append(heading, text); root.append(section);
  });
  const total = lesson.spec.stages.reduce((sum, stage) => sum + stage.duration, 0);
  let seconds = 0, disposed = false;
  const visibility = (): void => { if (document.hidden) video?.pause(); };
  document.addEventListener('visibilitychange', visibility);
  const api: StudioAPI = {
    dispose() {
      if (disposed) return;
      disposed = true; video?.pause(); video?.removeAttribute('src'); video?.load();
      document.removeEventListener('visibilitychange', visibility); root.replaceChildren();
      if (window.lessonStudio === api) { Reflect.deleteProperty(window, 'lessonStudio'); Reflect.deleteProperty(window, 'seek'); }
    },
    seek(time) { if (!disposed) { seconds = Number.isFinite(time) ? Math.max(0, Math.min(total, time)) : 0;
      if (video) { video.pause(); video.currentTime = seconds; } } },
    // Playback is deliberately started through the visible native video controls.
    play() { /* No implicit play when a historical node is selected. */ },
    pause() { if (!disposed) video?.pause(); },
    reset() { api.seek(0); },
    setControl() { throw new Error('This historical revision supports its preserved video and text only.'); },
    setMuted(muted) { if (video && !disposed) video.muted = muted; },
    getState() { return { time: video?.currentTime ?? seconds, beatId: 'preserved', description: notice.textContent ?? '',
      playing: !!video && !video.paused, controls: {}, narrated: !!video, audioStatus: video ? 'preserved' : 'unavailable', muted: video?.muted ?? false }; },
  };
  return api;
}
