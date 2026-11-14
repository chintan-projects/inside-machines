import { runRequest, PROMPT, round } from './mechanism.js';

export const CACHED = runRequest({cache:true});
export const REBUILT = runRequest({cache:false});
export const FRAME_IDS = ['tasks','first_choice','feed_back','second_choice','whole'];
export const HELP_ALIASES = {
  next_slot: ['slot', 'next token', 'next word'],
  scoring: ['score', 'scoring', 'rank', 'highest'],
  feed_input: ['feed', 'chosen', 'processed', 'feedback'],
  saved_work: ['cache', 'key', 'keys', 'value', 'saved', 'tray'],
  layers: ['layer', 'attention', 'ffn', 'numbers', 'transform'],
  cache_count: ['speed', 'timing', 'count', 'faster'],
};
export const DEFAULT_REPAIR = {
  next_slot_tasks:'next_slot', choice_and_saved_preparation:'saved_work',
  chosen_vs_processed:'feed_input', process_new_input_with_saved_lists:'saved_work', cache_on_off:'cache_count',
  layer_change:'layers', matching_share:'saved_work', taking_values:'saved_work',
  word_scores:'scoring',
};
export const vector = values => '[' + values.map(value=>round(value,2).toFixed(2)).join(', ') + ']';

export function exportStates() {
  return {revision:3,cached:CACHED,rebuilt:REBUILT};
}
