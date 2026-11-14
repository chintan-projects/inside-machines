import {context,KEPT,CLEARED,traceAt,RULES,format} from './mechanism.mjs';
const n=x=>String(Number(format(x))),pct=x=>(100*x).toFixed(1),name=x=>`the word ${x}`;
/** Compile numerical narration from the same trace used by the renderer. */
export function voice(b){
 const {t,pass,s}=context(b),w=t.word,src=s===undefined?null:t.sources[s];
 switch(b.narration_template){
  case 'same_prepare':return `The same input, ${n(t.input)}, gives the same query, ${n(t.query)}.`;
  case 'same_blend':return `The same query and allowed source keys and values repeat the same reading calculation. The combined reading is still ${n(t.blend)}.`;
  case 'same_mix':return `The unchanged input and reading give the same mixed working number, ${n(t.mixed)}.`;
  case 'same_adjust':return `The positive part is unchanged. Half gives the same local adjustment, ${n(t.adjustment)}.`;
  case 'same_done':return `The same mixed number plus the same adjustment leaves the finished result at ${n(t.output)}.`;
  case 'rebuild_step':{const a=traceAt(CLEARED,1,0,0),z=traceAt(CLEARED,1,0,1);return b.part==='lookup'?`The text remains. Look up The’s original input, ${n(a.input)}.`:b.part==='first'?`The quarter and 0.8 rules rebuild The’s first-layer key, ${n(a.key)}, and value, ${n(a.value)}.`:`From The’s second-layer input, ${n(z.input)}, rebuild its key, ${n(z.key)}, and value, ${n(z.value)}.`;}
  case 'single_read':return b.plain_read?`The only allowed source is The itself. Take its whole prepared reading number, ${n(t.value)}. The reading is ${n(t.blend)}.`:`The still reads only itself. Take its whole rebuilt value, ${n(t.value)}, to reconstruct the reading, ${n(t.blend)}.`;
  case 'prepare':{
   const a=b.part==='query'?t:context({...b,position:s??t.position,source_index:undefined}).t;
   if(b.part==='query')return b.first_definition?`To start the multiplication for The’s share, halve sky’s input, ${n(a.input)}. That gives ${n(a.query)}, the first number we will multiply.`:`Half of ${w}’s input, ${n(a.input)}, gives its query, ${n(a.query)}.`;
   if(b.part==='key')return b.revisit?`Revisit ${a.word}’s existing first-layer key, ${n(a.key)}. It came from a quarter of that source’s own input, ${n(a.input)}. This is the same preparation used while processing sky.`:b.use_plain_names&&!b.first_definition?`A quarter of ${a.word}’s input, ${n(a.input)}, gives its prepared source number, ${n(a.key)}.`:b.first_definition?`A quarter of The’s original input, ${n(a.input)}, gives ${n(a.key)}. Keep this prepared number beside The.`:`A quarter of ${a.word}’s input, ${n(a.input)}, gives its key, ${n(a.key)}.`;
   return b.revisit?`Use ${a.word}’s existing first-layer value, ${n(a.value)}. The same source value can be read again with a different share.`:b.show_creation_first?`${n(a.input)} times 0.8 gives ${n(a.value)}. This is The’s prepared reading number, ready to be taken into a reading.`:b.use_plain_names?`Prepare The’s reading number: ${n(a.input)} times 0.8 gives ${n(a.value)}.`:`${a.word}’s input, ${n(a.input)}, times 0.8 prepares its reading value, ${n(a.value)}.`;
  }
  case 'sources':return `This layer prepares each source’s ${b.part} from that source’s own input. ${t.sources.map((v,i)=>{const q=context({...b,position:i,source_index:undefined}).t;return `${v.word}: ${n(q.input)} times ${RULES[b.part]} gives ${n(v[b.part])}`;}).join('. ')}.`;
  case 'match':return b.use_plain_names&&!b.name_equal_product?`${w}’s prepared reader number ${n(t.query)} times ${src.word}’s prepared source number ${n(src.key)} gives the match ${n(t.matches[s])}.`:b.name_equal_product?`Sky’s prepared ${n(t.query)} times The’s prepared ${n(src.key)} gives ${n(t.matches[s])}. The product is called the match.`:b.plain_match?`Multiply sky’s prepared ${n(t.query)} by The’s prepared ${n(src.key)}. The product, ${n(t.matches[s])}, is called their match.`:`${w}’s query, ${n(t.query)}, times ${src.word}’s key, ${n(src.key)}, gives the match ${n(t.matches[s])}.`;
  case 'amount_rule_demo':{
   const x=traceAt(KEPT,0,1,0),m=x.matches[0],pos=x.positiveMatches[0],parts=x.parts[0];
   return b.part==='input'?`Try a small calculation that will help decide how much source value to use. Start with ${n(m)}.`:b.part==='positive'?`The actual match is ${n(m)}. It is positive, so its positive part stays ${n(pos)}.`:`Add one to that ${n(pos)}. The result is ${n(parts)}.`;
  }
  case 'sources_summary':return `Apply the ${b.part==='key'?'quarter':'times 0.8'} rule to each source’s second-layer input. The second-layer ${b.part}s are ${t.sources.map(v=>`${v.word}: ${n(v[b.part])}`).join('; ')}. These stay at layer two.`;
  case 'match_all':return `For ${w}’s reading, the matches are ${t.sources.map((v,i)=>`${v.word}: ${n(t.matches[i])}`).join('; ')}.`;
  case 'self_negative_match':return `Blue’s query ${n(t.query)} times its own key ${n(t.key)} gives ${n(t.matches[s])}. Multiplying two negatives gives a positive result.`;
  case 'positive_after_negative':return `The’s negative match gave a positive part of ${n(t.positiveMatches[s])}. Adding one makes its sharing amount ${n(t.parts[s])}, a positive number.`;
  case 'parts_all':return `For each match, keep its positive part and add one. Each row now gives that source’s sharing amount, using the rule we already built.`;
  case 'shares_all':return `Divide each source’s sharing amount by the total, ${n(t.total)}. The fractions to take of source values are ${t.sources.map((v,i)=>`${v.word}: ${pct(t.shares[i])} percent`).join('; ')}.`;
  case 'contribute_all':return `Take each source’s fraction of its own value. Each row gives one contribution; combine these contributions next.`;
  case 'parts_clip':return `${src.word}’s match is ${n(t.matches[s])}. Replace that negative match with zero to get its positive part: ${n(t.positiveMatches[s])}.`;
  case 'parts_add':return b.first_parts?`The’s match is ${n(t.matches[s])}. The rule we tried keeps its positive part and adds one. That gives The a sharing amount of ${n(t.parts[s])} for sky’s reading.`:`${src.word}’s match ${n(t.matches[s])} has positive part ${n(t.positiveMatches[s])}. Add one, giving ${src.word} an amount of ${n(t.parts[s])}.`;
  case 'parts_total':return `Add the source amounts. Their total is about ${n(t.total)}.`;
  case 'shared_fraction':{
   if(!b.shared_sources.every(i=>Math.abs(t.parts[i]-t.parts[s])<1e-12))throw new Error('Grouped fractions must have equal source amounts.');
   return `${b.shared_sources.map(i=>t.sources[i].word).join(', ')} each have amount ${n(t.parts[s])}. Divide ${n(t.parts[s])} by the total ${n(t.total)}: each uses ${pct(t.shares[s])} percent of its own value.`;
  }
  case 'share':return `For ${src.word}, divide its amount ${n(t.parts[s])} by the total ${n(t.total)}. This gives about ${pct(t.shares[s])} percent, the fraction to take of ${src.word}’s source value.`;
  case 'contribute':return `Read ${pct(t.shares[s])} percent of ${src.word}’s value, ${n(src.value)}, giving about ${n(t.contributions[s])}.`;
  case 'blend':return `The contributions add to a combined reading of about ${n(t.blend)}.`;
  case 'mix':return `Input ${n(t.input)} plus reading ${n(t.blend)} makes the mixed working number ${n(t.mixed)}.`;
  case 'positive':return b.first_definition?`In the copy, replace a negative number with zero; otherwise keep it. Here ${n(t.mixed)} stays at ${n(t.positive)}.`:`The mixed number ${n(t.mixed)} has positive part ${n(t.positive)}.`;
  case 'adjust':return `Half of ${n(t.positive)} makes the local adjustment, ${n(t.adjustment)}.`;
  case 'done':return `Working number ${n(t.mixed)} plus adjustment ${n(t.adjustment)} finishes this ${b.before_layer_name?'stage':'layer'} at ${n(t.output)}.`;
  case 'boundary':return `The finished first-layer number, ${n(context({...b,layer:0}).t.output)}, becomes this same piece’s second-layer input. Its first-layer key and value stay at their own layer.`;
  case 'first_result':return `The’s prepared reading number, ${n(t.value)}, is called its value. Keep that separate from its finished first-layer result, ${n(t.output)}.`;
  case 'second_inputs':return `The first-layer results are ready: ${KEPT.passes[0].traces.map(v=>`${v.word} at ${n(v.layers[0].output)}`).join(', ')}. Each result becomes that piece’s own second-layer input.`;
  case 'scores':{
   const p=KEPT.passes[pass],cand=p.selection.candidates.filter(c=>!['blue','and'].includes(b.part)||c.word===b.part);
   if(b.first_score){const c=cand[0];return `Multiply is’s finished number, ${n(p.result)}, by the assigned factor ${c.weight}. This gives ${n(c.score)}, blue’s score for choosing the next piece. The factor belongs to the choosing rule.`;}
   return `Use ${p.text.at(-1)}’s finished number, ${n(p.result)}, at the chooser. ${cand.map(c=>`Candidate ${c.word}: multiply by ${c.weight} to score ${n(c.score)}`).join('. ')}.`;
  }
  case 'prior_result':return `Appending later blue leaves the earlier is result at ${n(KEPT.passes[0].result)}. It did not acquire information from blue.`;
  case 'prior_choice':return `Scoring that unchanged earlier number again still selects ${KEPT.passes[0].selection.word}. That does not account for the newly appended blue.`;
  case 'rebuild':return `Rebuilding from the retained text uses the same fixed arithmetic and reproduces the same earlier layer inputs, keys and values.`;
  case 'compare':{
   if(b.part==='input')return `Both replay routes give blue the same starting input, ${n(KEPT.passes[1].traces[0].layers[0].input)}. Its processing still needs to happen.`;
   if(b.part==='choice')return `Only after blue finishes both layers, score its finished result. Both routes select ${KEPT.passes[1].selection.word}; the cache saved preparation work.`;
   const q=b.part==='layer1'?0:1;return `Both routes compute the same ${q?'second':'first'}-layer result for blue, about ${n(KEPT.passes[1].traces[0].layers[q].output)}. They used the same current input and the same allowed reading data.`;
  }
  default:throw new Error('Unknown numerical narration template: '+b.narration_template);
 }
}
export function compileNarration(raw){return {...raw,scenes:raw.scenes.map(s=>({...s,beats:s.beats.map(b=>b.narration_template?{...b,narration:voice(b)}:b)}))};}
