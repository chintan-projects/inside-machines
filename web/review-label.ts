/** A public demonstration permission is separate from human lesson approval. */
export function reviewLabel(value:{readonly public_preview?:boolean;readonly review_needed?:boolean}):string {
  return value.public_preview?'Review draft · public preview':value.review_needed?'Teaching draft · review pending':'';
}
