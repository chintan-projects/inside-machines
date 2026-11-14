// Interactive explanation. Runs after lesson/mechanism.js, checkpoints.js and story.js are inlined above it.
// No storage, no network: every state lives in `ui` and is lost on reload by design.
const REVISION = "prefill-decode-r2";
const $ = (id) => document.getElementById(id);
const SVG = "http://www.w3.org/2000/svg";
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Interactive steps = the story's checkpoints in order; captions are the film's narration for those beats.
const STEPS = [];
SCENES.forEach((scene, sceneIndex) => {
  scene.beats.forEach((beat) => {
    if (beat.interactive === "reveal" || beat.checkpoint === "cp_transfer") return; // the transfer answer stays hidden until asked for
    let step = STEPS.find((s) => s.checkpoint === beat.checkpoint);
    if (!step) {
      step = { checkpoint: beat.checkpoint, scene: scene.id, sceneIndex, title: scene.title, lines: [] };
      STEPS.push(step);
    }
    step.lines.push(beat.narration);
  });
});

const ui = { step: 0, cache: true, guess: null, trace: "prefill", score: null, teachbackScore: null, revealed: false };

// ---------- the board ----------
const X0 = 92, DX = 86, CW = 72, CH = 46;
const ROW_Y = [196, 136]; // layer 1 lower, layer 2 upper
const INPUT_Y = 264, PICK_Y = 40;
const colX = (c) => X0 + c * DX;
const CELL_STYLE = {
  empty: { fill: "none", stroke: "#a9a59a", dash: "5 4", text: "" },
  processed: { fill: "#e9e7e0", stroke: "#1b2129", text: "" },
  kv: { fill: "#d7ece9", stroke: "#157067", text: "K V" },
  new: { fill: "#d7ece9", stroke: "#1b2129", width: 3, text: "made" },
  reused: { fill: "#d7ece9", stroke: "#157067", width: 3, text: "read" },
  rebuilt: { fill: "#f8e3df", stroke: "#a73b32", width: 3, text: "rebuilt" },
};
const LEGEND = {
  empty: "not processed yet", kv: "keeps its key and value (K V)", new: "K and V made on this trip",
  reused: "K and V read back from the cache", rebuilt: "K and V rebuilt (cache off)",
};

function el(name, attrs, text) {
  const node = document.createElementNS(SVG, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

function chip(group, x, y, token, role, dashed) {
  const w = Math.max(64, token.length * 13 + 24);
  const color = role === "prompt" ? "#2c5aa0" : "#a8741a";
  group.append(el("rect", { x: x - w / 2, y: y - 18, width: w, height: 36, rx: 8, class: "chip",
    fill: role === "prompt" ? "#e3ebf7" : "#f6ecd8", stroke: color, "stroke-width": 2, "stroke-dasharray": dashed ? "4 3" : "none" }));
  group.append(el("text", { x, y: y + 7, "text-anchor": "middle", "font-size": 20, "font-weight": 600, fill: color }, token));
}

function arc(group, x1, x2, y, color, dashed, below = false) {
  if (x1 === x2) {
    group.append(el("path", { d: `M ${x1 - 10} ${y} c -6 -26 26 -26 20 0`, fill: "none", stroke: color, "stroke-width": 2, class: "arrow" }));
    return;
  }
  const h = 18 + Math.abs(x1 - x2) * 0.18;
  group.append(el("path", { d: `M ${x1} ${y} Q ${(x1 + x2) / 2} ${below ? y + h * 2 : y - h * 2} ${x2} ${y}`, fill: "none", stroke: color,
    "stroke-width": 2, "stroke-dasharray": dashed ? "5 4" : "none", "marker-end": "url(#tip)", class: "arrow" }));
}

function drawBoard(state) {
  const svg = $("board");
  [...svg.querySelectorAll("g, defs")].forEach(n => n.remove());
  const inputs = state.columns.filter(c => c.slot !== "picked");
  const picked = state.columns.find(c => c.slot === "picked");
  const n = Math.min(4, Math.max(3, inputs.length + (picked && inputs.length < 4 ? 1 : 0)));
  const x0=112, dx=86, cw=72, ch=46, rows=[208,132], inputY=306, outputY=40;
  const width=x0+(n-1)*dx+cw/2+18, x=i=>x0+i*dx, center=(x(0)+x(n-1))/2;
  svg.setAttribute("viewBox",`0 0 ${width} 354`);
  const defs=el("defs",{}),marker=el("marker",{id:"tip",viewBox:"0 0 10 10",refX:8,refY:5,markerWidth:6,markerHeight:6,orient:"auto"});
  marker.append(el("path",{d:"M0 0 L10 5 L0 10 z",fill:"context-stroke"}));defs.append(marker);svg.append(defs);
  const g=el("g",{});svg.append(g);
  const text=(t,xx,yy,size=20,color="#5b6470",anchor="middle")=>g.append(el("text",{x:xx,y:yy,"font-size":size,fill:color,"text-anchor":anchor},t));
  const path=(d,color="#78838d",dash="none")=>g.append(el("path",{d,stroke:color,"stroke-width":2,fill:"none","stroke-dasharray":dash,"marker-end":"url(#tip)"}));
  const token=(word,role,xx,yy,cls="")=>{
    const group=el("g",{class:cls}),color=role==="prompt"?"#2c5aa0":"#8e6012";
    group.append(el("rect",{x:xx-34,y:yy-20,width:68,height:40,rx:8,fill:role==="prompt"?"#e3ebf7":"#f6ecd8",stroke:color,"stroke-width":2}));
    group.append(el("text",{x:xx,y:yy+7,"text-anchor":"middle","font-size":22,"font-weight":600,fill:color},word));g.append(group);
  };
  const intro=state.id==="cp_prompt";
  if (intro) {
    const mid=(x(0)+x(2))/2;
    g.append(el("rect",{x:x(0)-36,y:115,width:244,height:110,rx:14,fill:"#f6f7f8",stroke:"#cad0d5","stroke-width":1.5}));
    text("The same model",mid,158,24,"#1b2129");text("same fixed rules",mid,191,19);
    text("Next token?",mid,49,23,"#8e6012");path(`M ${mid} 114 V 66`,"#a8741a");
    inputs.forEach((c,i)=>{token(c.token,c.role,x(i),inputY);path(`M ${x(i)} ${inputY-23} V 230`,"#2c5aa0");});
    text("Known prompt",mid,346,20,"#2c5aa0");
  } else if (state.id==="cp_lookback") {
    const left=126, top=69, size=58;
    text("Which positions may each token read?",width/2,25,19,"#1b2129");
    PROMPT.forEach((name,i)=>{text(name,left+i*size+size/2,top-15,20,"#2c5aa0");text(name,left-16,top+i*size+36,20,"#2c5aa0","end");});
    PROMPT.forEach((_,row)=>causalAllowed(row,3).forEach((allowed,col)=>{
      const blocked=row===1&&col===2;
      g.append(el("rect",{x:left+col*size+3,y:top+row*size+3,width:size-6,height:size-6,rx:8,fill:allowed?"#d7ece9":blocked?"#f8e3df":"#f2f2ef",stroke:blocked?"#a73b32":"none"}));
      text(allowed?"✓":"×",left+col*size+size/2,top+row*size+38,25,allowed?"#157067":blocked?"#a73b32":"#85909a");
    }));
    text("“sky” cannot read ahead to “is”.",width/2,285,20,"#a73b32");
    text("✓ itself and the past   × later positions",width/2,322,17);
  } else {
    const visible=state.columns.slice(0,n);
    ["Layer 1","Layer 2"].forEach((label,l)=>text(label,70,rows[l]+7,20,"#5b6470","end"));
    visible.forEach((col,c)=>{
      for(let l=0;l<2;l++) {
        const kind=state.cells[l][c],style=CELL_STYLE[kind];
        const cell=el("g",{class:state.id==="cp_prefill"?`processing-row row-${l}`:""});
        cell.append(el("rect",{x:x(c)-cw/2,y:rows[l]-ch/2,width:cw,height:ch,rx:8,fill:style.fill,stroke:style.stroke,"stroke-width":style.width||1.5,"stroke-dasharray":style.dash||"none"}));
        if(style.text) cell.append(el("text",{x:x(c),y:rows[l]+7,"text-anchor":"middle","font-size":22,fill:style.stroke},kind==="new"?"new":kind==="reused"?"reuse":kind==="rebuilt"?"redo":"K V"));
        g.append(cell);
      }
      if(col.slot!=="picked") {
        token(col.token,col.role,x(c),inputY,state.id==="cp_feed_blue"&&c===3?"feed-token":"");
        path(`M ${x(c)} ${inputY-24} V ${rows[0]+ch/2+4}`,col.role==="prompt"?"#8ba8cb":"#b58c40");
        path(`M ${x(c)} ${rows[0]-ch/2-4} V ${rows[1]+ch/2+5}`);
      } else {
        g.append(el("rect",{x:x(c)-34,y:inputY-20,width:68,height:40,rx:8,fill:"none",stroke:"#a9a59a","stroke-dasharray":"4 4"}));
      }
      text(String(c+1),x(c),346,18);
    });
    if(picked) {
      const outputX=x(Math.min(inputs.length,n-1));
      token(picked.token,"answer",outputX,outputY);
      text("chosen · not processed",width/2,85,18,"#8e6012");
      path(`M ${x(inputs.length-1)} ${rows[1]-ch/2-3} Q ${outputX} ${rows[1]-ch/2-3} ${outputX} ${outputY+23}`,"#a8741a");
    } else if(state.id==="cp_feed_blue") {
      text("The output becomes the next input.",width/2,40,20,"#8e6012");
    } else if(["cp_process_blue","cp_cache"].includes(state.id)) {
      text(state.cache?"Reuse the past. Process blue.":"Rebuild all four positions.",width/2,40,21,state.cache?"#157067":"#a73b32");
      text("Past + current results feed fresh computation.",width/2,78,17);
    } else if(state.id==="cp_prefill") { text("Together within a layer.",width/2,40,20,"#1b2129"); text("Then the next layer.",width/2,70,20,"#1b2129"); };
  }
  const used=[...new Set(state.cells.flat())].filter(k=>k!=="empty");
  $("legend").innerHTML=intro?"Known text goes in; the model computes the next choice.":state.id==="cp_lookback"?"This is the causal mask. Knowing a later token does not make it readable.":used.map(k=>`<span><i style="background:${CELL_STYLE[k].fill};border:1.5px solid ${CELL_STYLE[k].stroke}"></i>${LEGEND[k]}</span>`).join("");
  $("board-desc").textContent=describe(state);
}

function describe(state) {
  const tokens = state.columns.map((c) => `${c.token} (${c.slot === "picked" ? "picked, not processed" : "input"})`).join(", ");
  const rows = state.cells.map((row, l) => `layer ${l + 1}: ${row.map((k) => LEGEND[k] || k).join("; ")}`).join(". ");
  return `Positions: ${tokens}. ${rows}.`;
}

const UI_COPY = {
 cp_prompt: ["Start with a known prompt", "Each piece of text is a token. All three prompt tokens are already available; the next answer token has to be computed."],
 cp_lookback: ["Read the past, never the future", "Each row shows what one position may read. Even though “is” is already known, the earlier position “sky” cannot use it. This is causal attention."],
 cp_prefill: ["Known positions go through together", "Within each layer, attention mixes allowed context and a feed-forward network transforms each position. Layer 2 then uses layer 1’s outputs. This prompt-processing phase is prefill."],
 cp_pick_blue: ["The first answer comes from prefill", "The last prompt position produces next-token scores. Our toy chooses the highest: “blue”. It has been selected, but has not passed through the model yet."],
 cp_feed_blue: ["Blue becomes the next input", "Feed “blue” back into the same model. Its position is still unprocessed; the earlier prompt positions already have saved state."],
 cp_process_blue: ["Reuse the past. Process the new token.", "Each layer makes blue’s key and value: two saved lists of numbers. Attention uses the allowed earlier lists and blue’s new lists. Then the feed-forward network transforms the result. Earlier lists stay valid because their positions cannot read ahead to blue."],
 cp_pick_and: ["One more pass, one more choice", "Blue’s final-layer scores now choose “and”. That chosen token becomes the input of a later pass. Spare parallel hardware cannot supply an input that has not been chosen yet."],
 cp_cache: ["What does the cache actually save?", "Turn the cache off and watch the earlier positions get rebuilt. The exact toy’s scores and selected tokens stay the same. Caching saves repeated computation; it does not store an answer."],
 cp_close: ["Now you can trace the loop", "Known prompt → first choice → feed it back → reuse saved state → next choice. We stop this toy after two choices; real decoders continue until a stopping rule is met."]
};

// ---------- the explanation pane ----------
function render() {
  const step = STEPS[ui.step];
  const state = buildCheckpoint(step.checkpoint, { cache: ui.cache });
  drawBoard(state);
  $("where").textContent = `Core explanation · ${ui.step + 1} of ${STEPS.length}`;
  $("step-title").textContent = UI_COPY[step.checkpoint][0];
  const offCopy={
    cp_feed_blue:"Feed blue into position four. With the cache off, the coming pass will rebuild earlier results as well.",
    cp_process_blue:"Rebuild all four positions in each layer. Attention uses the allowed keys and values, including the current position’s own, then the feed-forward block produces fresh outputs. The exact toy’s choice stays the same.",
    cp_close:"Known prompt → first choice → feed it back → rebuild earlier state with cache off → next choice. We stop after two choices; real decoders continue until a stopping rule is met."
  };
  $("caption").textContent = (!ui.cache&&offCopy[step.checkpoint])||UI_COPY[step.checkpoint][1];
  $("full-caption").innerHTML = step.lines.map((t) => `<p>${t}</p>`).join("");
  const scores = $("scores");
  scores.hidden = !state.scores;
  if (state.scores) {
    const max = Math.max(...state.scores.list.map((s) => s.score));
    scores.innerHTML = `<small>Toy scores from position ${state.scores.column + 1} (top 3 of ${VOCABULARY.length})</small>` +
      state.scores.list.map((s) => `<div class="row${s.token === state.scores.pick ? " pick" : ""}"><span>${s.token}</span>` +
        `<span class="bar" style="width:${Math.max(4, (s.score / max) * 100)}%"></span><span class="num">${s.score.toFixed(2)}</span></div>`).join("");
  }
  $("readout").textContent = readout(state);
  $("back").disabled = ui.step === 0;
  $("next").disabled = false;
  $("next").textContent = ui.step === STEPS.length - 1 ? "Try a new case" : "Next step";
  $("cache").hidden = !["cp_process_blue", "cp_pick_and", "cp_cache", "cp_close"].includes(state.id);
  $("cache").setAttribute("aria-checked", String(ui.cache));
  $("cache").textContent = `KV cache: ${ui.cache ? "on" : "off"}`;
  renderPredictionResult();
}

function readout(state) {
  const parts = [];
  if (state.counts) parts.push(`${state.counts.made} new K/V pairs · ${state.counts.reused} saved pairs reused across the two layers.`);
  if (["cp_process_blue", "cp_cache"].includes(state.id)) {
    const other = buildCheckpoint(state.id, { cache: !ui.cache });
    parts.push(`With the cache ${ui.cache ? "off" : "on"} it would be ${other.counts.made} made, ${other.counts.reused} read. Picks either way: ${state.picks.join(", ")}.`);
  } else if (!ui.cache && ["cp_prompt", "cp_lookback", "cp_prefill", "cp_pick_blue"].includes(state.id)) {
    parts.push("The cache only changes anything from the second answer token on: the prompt has no earlier entries to reuse.");
  }
  return parts.join(" ");
}

// ---------- prediction ----------
function renderPredictionResult() {
  const reached = ui.step >= STEPS.findIndex((s) => s.checkpoint === PREDICTION.revealAtCheckpoint);
  const out = $("predict-result");
  if (!reached) out.textContent = ui.guess ? "Noted. Step through to see." : "You can skip this; the steps work either way.";
  else out.textContent = `${ui.guess ? (ui.guess === PREDICTION.correct ? "Your guess holds. " : "Not quite. ") : ""}${PREDICTION.explanation}`;
}

function setupPrediction() {
  $("predict-prompt").textContent = PREDICTION.prompt;
  PREDICTION.options.forEach((o) => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = o.label; b.setAttribute("aria-pressed", "false");
    b.addEventListener("click", () => {
      ui.guess = o.id;
      $("predict-options").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      renderPredictionResult();
    });
    $("predict-options").append(b);
  });
}

// ---------- depth: lanes ----------
function renderLanes() {
  const specs=[["lanes-requests",1,4],["lanes-prompt",1,8],["lanes-answer",1,6]];
  let invalid=false;
  const [requests,promptLength,answerTokens]=specs.map(([id,lo,hi])=>{
    const value=Number($(id).value),valid=$(id).value!==""&&Number.isInteger(value)&&value>=lo&&value<=hi;
    $(id).setAttribute("aria-invalid",String(!valid));invalid||=!valid;return value;
  });
  if(invalid){$("lanes-summary").textContent="Use whole numbers: 1–4 requests, 1–8 prompt tokens, 1–6 answer tokens. The diagram retains the last valid setup.";return;}
  const work = laneWork({ requests, promptLength, answerTokens });
  let html = "";
  for (let r = 0; r < requests; r += 1) {
    html += `<div class="lane"><b>Request ${r + 1}</b>` + work.passes.map((p, i) =>
      `<span class="trip ${p.kind}" title="trip ${i + 1}">${p.perRequest}</span>`).join("") + "</div>";
  }
  $("lanes").innerHTML = html;
  const first = work.passes[0];
  $("lanes-summary").textContent = `Trip 1 (the prompt) processes ${first.positions} positions together: ${promptLength} known tokens in each of ${requests} request${requests > 1 ? "s" : ""}. ` +
    (work.decodePasses ? `Each of the ${work.decodePasses} later trip${work.decodePasses > 1 ? "s" : ""} processes ${requests} position${requests > 1 ? "s" : ""}, one new token per request, because each needs the token picked just before it. ` : "") +
    `${work.selections} picks in total: the first pick of each request comes from trip 1, the rest from one later trip each.`;
}

// ---------- depth: the model ----------
const fmt = (v) => `[${v.map((x) => round(x).toFixed(2)).join(", ")}]`;
function renderTrace() {
  const run = runRequest();
  const t = run.passes[ui.trace === "prefill" ? 0 : 1].trace;
  const rows = t.layers.map((l) =>
    `<tr><td>Layer ${l.layer + 1} in</td><td>${fmt(l.input)}</td></tr>` +
    `<tr><td>after attention</td><td>${fmt(l.mixed)}</td></tr>` +
    `<tr><td>after feed-forward</td><td>${fmt(l.output)}</td></tr>`).join("");
  const scores = [...t.scores.list].sort((a, b) => b.score - a.score).map((s) => `${s.token} ${round(s.score).toFixed(2)}`).join(" · ");
  $("trace").innerHTML = `<table><thead><tr><th>Stage</th><th>2 numbers</th></tr></thead><tbody>${rows}` +
    `<tr><td>scores</td><td class="score-list">${scores}</td></tr><tr><td>greedy pick</td><td>${t.scores.pick}</td></tr></tbody></table>`;
  const worked=t.layers.map(l=>{
    const f=l.feedForward;
    return `<details><summary>Layer ${l.layer+1}: compute the feed-forward block</summary><p>Matrix × vector: each row of the matrix is multiplied with the input, then added. ReLU keeps positive numbers and turns negatives into zero. Add the result back to the block input.</p><dl>
      <dt>Block input</dt><dd>${fmt(f.input)}</dd>
      <dt>First matrix</dt><dd>${f.matrixIn.map(fmt).join("<br>")}</dd>
      <dt>Matrix × input</dt><dd>${fmt(f.hidden)}</dd>
      <dt>After ReLU</dt><dd>${fmt(f.activated)}</dd>
      <dt>Second matrix</dt><dd>${f.matrixOut.map(fmt).join("<br>")}</dd>
      <dt>Matrix × activated</dt><dd>${fmt(f.delta)}</dd>
      <dt>Add to block input</dt><dd>${fmt(f.output)}</dd></dl></details>`;
  }).join("");
  $("trace").insertAdjacentHTML("beforeend",`<div class="ffn-worked">${worked}</div>`);
  document.querySelectorAll("[data-trace]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.trace === ui.trace)));
}

const ATTN_TOKENS = [...PROMPT, "blue"];
const attnState = { pos: 3, mask: causalAllowed(3, 4), query: null };
function setupAttention() {
  ATTN_TOKENS.forEach((t, i) => $("attn-pos").append(new Option(`${i + 1}: ${t}`, String(i))));
  $("attn-pos").value = "3";
  const reset = () => {
    attnState.mask = causalAllowed(attnState.pos, ATTN_TOKENS.length);
    attnState.query = layerOneProjection(ATTN_TOKENS[attnState.pos]).query.map((x) => round(x));
    $("attn-q0").value = attnState.query[0]; $("attn-q1").value = attnState.query[1];
    $("attn-q0").setAttribute("aria-invalid","false"); $("attn-q1").setAttribute("aria-invalid","false");
    renderAttention();
  };
  $("attn-pos").addEventListener("change", () => { attnState.pos = Number($("attn-pos").value); reset(); });
  ["attn-q0", "attn-q1"].forEach((id, i) => $(id).addEventListener("input", () => {
    const v = Number($(id).value);
    const valid = $(id).value !== "" && Number.isFinite(v) && Math.abs(v) <= 10;
    $(id).setAttribute("aria-invalid",String(!valid));
    if (valid) { attnState.query[i] = v; renderAttention(); }
    else $("attn-out").textContent = "Use a query value between -10 and 10 for this toy. The last valid calculation is shown above.";
  }));
  $("attn-causal").addEventListener("click", reset);
  $("attn").addEventListener("change", (e) => {
    if (e.target.dataset.mask !== undefined) { attnState.mask[Number(e.target.dataset.mask)] = e.target.checked; renderAttention(); }
  });
  reset();
}
const vectorHTML=(v)=>`<span class="vector" aria-label="[${v.map(x=>round(x).toFixed(2)).join(", ")}]">${v.map(x=>`<span>${round(x).toFixed(2)}</span>`).join("")}</span>`;
function renderAttention() {
  const kv = ATTN_TOKENS.map((t) => layerOneProjection(t));
  const res = attend(attnState.query, kv.map((k) => k.key), kv.map((k) => k.value), attnState.mask);
  const rows = ATTN_TOKENS.map((t, i) => `<tr class="${attnState.mask[i] ? "" : "masked"}"><td><label><input type="checkbox" data-mask="${i}" ${attnState.mask[i] ? "checked" : ""}> ${t}</label></td>` +
    `<td>${vectorHTML(kv[i].key)}</td><td>${vectorHTML(kv[i].value)}</td><td>${Number.isFinite(res.scores[i]) ? round(res.scores[i]).toFixed(2) : "masked"}</td><td>${round(res.weights[i]).toFixed(2)}</td></tr>`).join("");
  $("attn").innerHTML = `<table><thead><tr><th>allow</th><th>key</th><th>value</th><th>score</th><th>weight</th></tr></thead><tbody>${rows}</tbody></table>`;
  const causal = attnState.mask.every((m, i) => m === (i <= attnState.pos));
  const total = res.weights.reduce((a, b) => a + b, 0);
  if (!res.valid) {
    $("attn-out").textContent = "No positions are allowed. Softmax has no valid result; allow at least one position or restore the causal mask.";
    return;
  }
  $("attn-out").textContent = `Query ${fmt(attnState.query)} from “${ATTN_TOKENS[attnState.pos]}”. Weights add up to ${round(total).toFixed(2)}. Output = ${fmt(res.output)}. ` +
    (causal ? "Mask is causal: this position reads itself and earlier positions only." : "Mask edited: this is no longer the causal rule; a real decoder never lets a position read a later one.");
}

// ---------- transfer ----------
function setupTransfer() {
  $("transfer-prompt").textContent = TRANSFER.prompt;
  const revealBeat = SCENES.flatMap((s) => s.beats).find((b) => b.id === TRANSFER.revealBeat);
  $("transfer-answer-text").textContent = TRANSFER.answer ?? revealBeat.narration;
  [
    {score:2,text:"I explained both: the prompt is already known; a newly chosen token must be processed before choosing its successor."},
    {score:1,text:"I explained one of those links, but not both."},
    {score:0,text:"I said a GPU cannot do parallel work, or that future answer tokens are already available."}
  ].forEach(r=>{
    const label=document.createElement("label");
    label.innerHTML=`<input type="radio" name="teachback-score" value="${r.score}"> <b>${r.score}</b>: ${r.text}`;
    $("teachback-rubric").append(label);
  });
  const enableExport=()=>$("transfer-export").disabled=ui.score===null||ui.teachbackScore===null;
  $("teachback-rubric").addEventListener("change",e=>{ui.teachbackScore=Number(e.target.value);enableExport();});
  TRANSFER.rubric.forEach((r) => {
    const label = document.createElement("label");
    label.innerHTML = `<input type="radio" name="score" value="${r.score}"> <b>${r.score}</b>: ${r.text}`;
    $("transfer-rubric").append(label);
  });
  $("transfer-reveal").addEventListener("click", () => {
    ui.revealed = true; $("transfer-key").hidden = false; $("transfer-reveal").disabled = true; $("transfer-answer-text").focus?.();
  });
  $("transfer-rubric").addEventListener("change", (e) => { ui.score = Number(e.target.value); enableExport(); });
  $("transfer-export").addEventListener("click", () => {
    const record = { lesson: REVISION, check: TRANSFER.id, transfer_score: ui.score, teachback_score: ui.teachbackScore, prediction: ui.guess, scored_by: "self", date: new Date().toISOString().slice(0, 10) };
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(record, null, 2)], { type: "application/json" }));
    a.download = `transfer-score-${record.date}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
}

// ---------- depth routing ----------
function openPanel(panel) {
  if (panel === "cache") {
    ui.step = STEPS.findIndex((s) => s.checkpoint === "cp_cache"); render();
    $("stage").scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" }); $("cache").focus(); return;
  }
  const requestedAttention = panel === "attention";
  if (requestedAttention) panel = "model";
  document.querySelectorAll(".deeper > .panel").forEach(n => n.hidden = n.id !== `panel-${panel}`);
  const node = $(`panel-${panel}`);
  if (!node) return;
  node.hidden = false;
  node.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  node.querySelector("h3").setAttribute("tabindex", "-1");
  node.querySelector("h3").focus({ preventScroll: true });
  if (requestedAttention) { $("attn-h").tabIndex=-1; $("attn-h").scrollIntoView({block:"start"}); $("attn-h").focus({preventScroll:true}); }
}

function setupAsk() {
  $("ask").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = $("ask-input").value.trim();
    if (!text) return;
    const hit = matchIntent(text);
    const out = $("ask-result");
    if (hit) { out.textContent = `Opening: ${hit.label}.`; openPanel(hit.panel); return; }
    out.textContent = `This page has no answer for “${text}”. It only opens its own prepared views and never generates replies. ` +
      "Ask that question in the Claude or Codex conversation where you are exploring this project.";
  });
}

// ---------- wiring ----------
function go(i) { ui.step = Math.max(0, Math.min(STEPS.length - 1, i)); render(); }
$("back").addEventListener("click", () => go(ui.step - 1));
$("next").addEventListener("click", () => ui.step === STEPS.length - 1 ? openPanel("transfer") : go(ui.step + 1));
function startOver() {
  Object.assign(ui, {step:0,cache:true,guess:null,trace:"prefill",score:null,teachbackScore:null,revealed:false});
  $("predict").open=false;
  $("predict-options").querySelectorAll("button").forEach(b=>b.setAttribute("aria-pressed","false"));
  document.querySelectorAll(".deeper > .panel").forEach(n=>n.hidden=true);
  ["transfer-answer","teachback-answer","ask-input"].forEach(id=>$(id).value="");
  $("ask-result").textContent="";
  $("transfer-key").hidden=true; $("transfer-reveal").disabled=false; $("transfer-export").disabled=true;
  document.querySelectorAll('#transfer-key input[type="radio"]').forEach(n=>n.checked=false);
  $("attn-pos").value="3"; $("attn-pos").dispatchEvent(new Event("change"));
  $("lanes-requests").value="2"; $("lanes-prompt").value="3"; $("lanes-answer").value="2";
  $("lesson-film").pause(); $("lesson-film").currentTime=0;
  document.querySelectorAll(".full-line").forEach(n=>n.open=false);
  renderLanes(); renderTrace(); go(0); $("step-title").focus();
}
$("reset").addEventListener("click", startOver);
$("cache").addEventListener("click", () => { ui.cache = !ui.cache; render(); });
document.querySelectorAll("[data-open]").forEach((b) => b.addEventListener("click", () => openPanel(b.dataset.open)));
document.querySelectorAll("[data-trace]").forEach((b) => b.addEventListener("click", () => { ui.trace = b.dataset.trace; renderTrace(); }));
["lanes-requests", "lanes-prompt", "lanes-answer"].forEach((id) => $(id).addEventListener("input", renderLanes));
document.addEventListener("keydown", (e) => {
  if (e.target.closest("input, textarea, select, video, [contenteditable=true]") || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "ArrowRight") {e.preventDefault();go(ui.step + 1);}
  else if (e.key === "ArrowLeft") {e.preventDefault();go(ui.step - 1);}
  else if (e.key === "Home") { e.preventDefault(); startOver(); }
  else if ((e.key === "c" || e.key === "C") && !$("cache").hidden) { ui.cache = !ui.cache; render(); }
});
document.querySelectorAll(".deeper > .panel").forEach(panel=>{
  const b=document.createElement("button");b.type="button";b.className="return-core";b.textContent="Return to the core explanation";
  b.addEventListener("click",()=>{panel.hidden=true;$("stage").scrollIntoView({block:"start"});$("step-title").focus({preventScroll:true});});panel.append(b);
});
const film=$("lesson-film");
$("film-sound").addEventListener("click",()=>{film.muted=!film.muted;});
film.addEventListener("volumechange",()=>{
  const on=!film.muted&&film.volume>0;$("film-sound").setAttribute("aria-pressed",String(on));
  $("film-sound").textContent=on?"Sound on · mute":"Sound off · unmute";
  $("film-status").textContent=on?"Narration is on. Your device also controls listening volume.":"Narration is muted. You can follow the English captions or unmute.";
});
film.addEventListener("error",()=>{$("film-status").textContent="The film could not load. Serve the delivered review bundle with node review.mjs; the transcript remains available below.";});
const FILM_CHAPTERS = /* ACTUAL_TIMELINE_CHAPTERS */ [];
FILM_CHAPTERS.forEach(chapter=>{
  const button=document.createElement("button");button.type="button";button.textContent=chapter.title;
  button.addEventListener("click",()=>{
    const film=$("lesson-film");
    const seek=()=>{film.currentTime=chapter.seconds;film.play().catch(()=>{$("film-status").textContent="Press Play to start the narration.";});};
    if(film.readyState)seek();else {film.addEventListener("loadedmetadata",seek,{once:true});film.load();}
  });
  $("film-chapters").append(button);
});
$("transcript").innerHTML=SCENES.map(s=>`<h3>${s.title}</h3>${s.beats.map(b=>`<p>${b.narration}</p>`).join("")}`).join("");
setupPrediction(); setupAttention(); setupTransfer(); setupAsk(); renderLanes(); renderTrace(); render();
