"""Trusted authoring guidance; teaching and rendering contracts remain shared."""

import json
import re
from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Literal

from .contracts import canonicalize


@dataclass(frozen=True)
class ConceptGuide:
    """Versioned instructions, not executable plugins or factual certification."""

    id: str
    representation: Literal["physical", "information", "mixed", "evidence-led"]
    research: str
    authoring: str
    review: str


GENERAL = ConceptGuide(
    "general-concept-1",
    "evidence-led",
    "Determine whether the explanation concerns a physical mechanism, information processing, "
    "or both. Research the actual causal dependencies and limits of the declared scope.",
    "Choose the representation from evidence: a recognizable cutaway for physical hardware, "
    "or a labeled computational/relational view for an abstract process. Identify what each "
    "node, connection and movement represents. A box-and-arrow view is valid only when its "
    "internal state changes explain a relationship; a sequence of text boxes is insufficient. "
    "Do not invent a physical machine to make an abstract topic fit the renderer. Use 8–24 "
    "purposeful context parts, including labels; do not add filler to meet a part count.",
    "Check representation against scope. Distinguish material or energy transfer from "
    "information dependencies; no metaphor may be presented as literal implementation.",
)

PHYSICAL = ConceptGuide(
    "physical-mechanism-1",
    "physical",
    "Identify working components, material/energy paths, constraints and relevant conservation rules.",
    "Draw a recognizable physical object with purposeful solids and a legible cutaway, "
    "about 18–24 context parts. Use front/top/side surfaces only where they clarify volume. "
    "Identify motor, input, output, fluids or heat markers only where relevant. Show markers "
    "crossing actual openings, not solid walls, shafts or closed housings. Label each port. "
    "Use separate upper/lower wall paths for an open passage, never a U-shaped closed end. "
    "Closed working-fluid loops need continuous tubing, not fictitious leaks. Draw relevant "
    "physical surroundings in each inset and explain enlarged sections in narration.",
    "Trace actual material/energy paths, relevant conservation, openings and solid clearances. "
    "Check a recognizable object and coherent internal geometry, without claiming exact-model internals.",
)

GPU = ConceptGuide(
    "gpu-computing-1",
    "mixed",
    "Distinguish a general parallel-computing explanation from vendor/architecture-specific "
    "execution. Research independent work, dependencies, execution groups and memory limits. "
    "Do not generalize NVIDIA/CUDA specifics to every GPU.",
    "Honor the requested subtopic; these are constraints, not a mandatory whole-GPU tour. "
    "For parallel-computing explanations use labeled work items, execution lanes/groups and memory regions with visible data "
    "dependencies. Show independent items progressing concurrently and dependent items "
    "waiting for prerequisites. Reconnect this logical view to chip/memory hardware only "
    "where sourced. State that illustrative lanes/counts/timing are not an actual die layout "
    "or benchmark. A meaningful counterfactual changes dependencies or data availability. "
    "Do not imply a GPU is always faster, that every task starts at once, or that memory "
    "and scheduling are free. Use 8–24 purposeful context parts with legible labels.",
    "Check dependency order, available parallelism, memory movement and qualitative limits. "
    "Reject invented speedups/core counts, universal vendor-specific execution, or a drawing "
    "that equates more lanes with guaranteed proportional speedup.",
)

LLM = ConceptGuide(
    "language-model-1",
    "information",
    "Bound the architecture and distinguish training from inference. For an autoregressive "
    "decoder example research tokenization, contextual representations, attention/feed-forward "
    "transformations, output scores and generation. Other architectures require their own evidence.",
    "Honor the requested scope; do not answer a training question with a generation tour. "
    "Training needs an objective, error signal and parameter updates, grounded in its evidence. "
    "For a decoder-only generation overview, show token pieces (not necessarily words), "
    "numeric representations, context mixing and learned transformations, candidate scores, "
    "selection, and appending a token to the context. Use labeled token tiles, vectors or "
    "small matrices whose dependency/state changes teach the operation. Counts/values are "
    "illustrative unless a declared computed toy model supplies them. Do not add pumps, "
    "fluid flow, a literal brain or decorative server hardware. Training/parameter updates "
    "are separate from ordinary inference; attention is not the whole network. A changed "
    "context may change candidates; it need not change the selected token. Scores are not "
    "truth probabilities or an explanation of a model's private reasoning. Use 8–24 "
    "purposeful context parts. Keep new terminology subordinate to its job.",
    "Apply the checks relevant to the declared subtopic and architecture: token/word distinction, causal context visibility, "
    "attention plus other learned transformations, score/selection distinction, and training "
    "versus inference. Reject guaranteed truth, invented actual weights/probabilities, "
    "retrieval or permanent learning presented as inherent to every generated reply.",
)

GUIDES = MappingProxyType({guide.id: guide for guide in (GENERAL, PHYSICAL, GPU, LLM)})


def guide_for(question: str, guide_id: str = "") -> ConceptGuide:
    """Resolve only trusted guides; a stored unknown version fails before a paid call."""
    if guide_id:
        if guide_id not in GUIDES:
            raise ValueError("Unsupported concept guide version")
        return GUIDES[guide_id]
    topic = canonicalize(question)
    gpu = bool(re.search(r"\bgpu\b", topic))
    llm = bool(re.search(r"\bllm\b", topic))
    if gpu and llm:
        return GENERAL
    if gpu and re.search(r"\b(cooling|fan|thermal|fabrication|manufacturing)\b", topic):
        return PHYSICAL
    if gpu:
        return GPU
    if llm:
        return LLM
    if re.search(
        r"air-condition|washing|washer|refriger|pressure-cook|espresso|vacuum|plumbing|sink-trap|microwave",
        topic,
    ):
        return PHYSICAL
    return GENERAL


def guide_policy() -> str:
    """Include every trusted guide in author-checkpoint compatibility identity."""
    return json.dumps([asdict(GUIDES[id]) for id in sorted(GUIDES)], sort_keys=True)
