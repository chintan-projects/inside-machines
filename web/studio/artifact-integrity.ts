/** Verify offline video bytes against the artifact bound by the server's path envelope. */
export async function verifyVideo(blob: Blob, expectedSha256: string | undefined): Promise<void> {
  if (!expectedSha256 || !/^[a-f0-9]{64}$/.test(expectedSha256))
    throw new Error('The explanation is missing its video identity. Nothing new was saved.');
  if (!globalThis.crypto?.subtle) throw new Error('This browser cannot verify offline videos. The previous save is preserved.');
  const digest = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
  const actual = [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
  if (actual !== expectedSha256) throw new Error('The downloaded video does not match this explanation. Nothing new was saved.');
}
