/** Owner exposure permission is bound to exact artifacts, independently of release. */
export interface PreviewBinding {
  spec_sha256:string;video_sha256:string;bundle_sha256:string;
  bindings:readonly {lesson_id:string;spec_sha256:string;video_sha256:string;proof_sha256:string;artifact_sha256:string}[];
}
export interface PublicPreviewState {
  lesson_id:string;candidate:PreviewBinding|null;
  preview:{binding:PreviewBinding;enabled:boolean;by:string;at:number}|null;
  enabled:boolean;issue:string;notice:string;
}
export interface PreviewChange {enabled:boolean;spec_sha256:string;video_sha256:string;bundle_sha256:string}
export function previewChange(state:PublicPreviewState,enabled:boolean):PreviewChange|undefined {
  const binding=enabled?state.candidate:state.preview?.enabled?state.preview.binding:undefined;
  return binding?{enabled,spec_sha256:binding.spec_sha256,video_sha256:binding.video_sha256,bundle_sha256:binding.bundle_sha256}:undefined;
}
