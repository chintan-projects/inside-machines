import { lazy, Suspense, type ReactElement } from 'react';
import type { StoredSpec } from './native-contracts';
import { Graphic } from '../teaching/Graphic';
import { Scene } from '../Scene';
const NativeArtwork=lazy(async()=>({default:(await import('./NativeCatalogArtwork')).NativeCatalogArtwork}));

/** Only compiled trusted artwork can supply SVG, never executable API content. */
export function CatalogArtwork({spec}:{readonly spec:StoredSpec}):ReactElement {
  if(spec.version===3) {
    return <Suspense fallback={<span>{spec.title}</span>}><NativeArtwork spec={spec}/></Suspense>;
  }
  return spec.canonical.endsWith('-studio-1') ? <Graphic spec={spec} seconds={spec.stages[0].duration*.45}/> : <Scene spec={spec} preview/>;
}
