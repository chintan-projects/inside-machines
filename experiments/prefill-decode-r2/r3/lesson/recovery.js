// Topic-independent, deterministic help navigation. It chooses authored help;
// it never pretends to generate an answer. Learner input stays in memory.
export function resolveHelp({ text, concept, repairs, aliases }) {
  const query = String(text).toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
  const matches = Object.entries(aliases).filter(([, words]) => words.some(word => query.includes(word)));
  if (matches.length === 1) return { kind: 'repair', id: matches[0][0], reason: 'named_concept' };
  const current = repairs.find(item => item.concept === concept);
  if (/\b(lost|confused|dont understand|do not understand|simpler|simply|again)\b/.test(query) && current) {
    return { kind: 'repair', id: current.id, reason: 'current_context' };
  }
  return { kind: 'clarify', ids: [...new Set([current?.id, ...repairs.map(item => item.id)].filter(Boolean))], reason: query ? 'clarification_needed' : 'choose_help' };
}

export function createJourney(frameIds) {
  if (!frameIds.length || new Set(frameIds).size !== frameIds.length) throw new RangeError('Use unique chapter IDs.');
  let core = { frame: frameIds[0], beat: 0, cache: true };
  let repair = null;
  return {
    state: () => ({ ...core, repair }),
    move(frame, beat = 0) {
      if (!frameIds.includes(frame) || !Number.isSafeInteger(beat) || beat < 0) throw new RangeError('Unknown chapter or beat.');
      core = { ...core, frame, beat }; repair = null;
    },
    compare(cache) { core = { ...core, cache: Boolean(cache) }; },
    help(id) { repair = id; },
    back() { repair = null; },
    reset() { core = { frame: frameIds[0], beat: 0, cache: true }; repair = null; },
  };
}
