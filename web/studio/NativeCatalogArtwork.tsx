import type { ReactElement } from 'react';
import type { NativeSpec } from './native-contracts';
import { nativeLesson } from './native-registry';

/** Trusted source only; unknown artwork keeps its text rather than a substitute drawing. */
export function NativeCatalogArtwork({spec}:{readonly spec:NativeSpec}):ReactElement {
  const lesson=nativeLesson(spec,'',false);
  if(!lesson)return <span>{spec.title}</span>;
  const scene=lesson.render(lesson.stateAt(0,lesson.defaultControls));
  const vp=scene.viewport??{x:0,y:0,width:720,height:620};
  return <svg viewBox={`${vp.x} ${vp.y} ${vp.width} ${vp.height}`} aria-hidden="true"
    dangerouslySetInnerHTML={{__html:scene.svg}}/>;
}
