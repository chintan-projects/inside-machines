"""Trusted, content-addressed physical artwork sets for the shared scene engine."""

import hashlib
import re
from dataclasses import dataclass
from functools import lru_cache
from xml.etree import ElementTree

from .contracts import LessonSpec
from .settings import ROOT


# Trusted startup composition, never a file name, path or URL supplied by a client/model.
@dataclass(frozen=True)
class ArtworkSet:
    """A trusted revision family, ordered scenes and a whole-system locator."""

    revisions: tuple[str, ...]
    scenes: tuple[str, ...]
    context: str


ARTWORK = (
    ArtworkSet(
        ("bagged-vacuum-ce-2", "bagged-vacuum-ce-3", "bagged-vacuum-ce-4", "bagged-vacuum-ce-5"),
        ("vacuum-fan", "vacuum-nozzle", "vacuum-bag"),
        "vacuum-context",
    ),
)


@lru_cache(maxsize=8)
def asset_source(name: str) -> str:
    """Load and validate author-controlled SVG; external references are prohibited."""
    if name not in {name for artwork in ARTWORK for name in (*artwork.scenes, artwork.context)}:
        raise ValueError("Unknown authored section asset")
    source = (ROOT / "public/figures" / f"{name}.svg").read_text()
    root = ElementTree.fromstring(source)
    for node in root.iter():
        if node.tag.split("}")[-1] in ("script", "foreignObject", "image", "use"):
            raise ValueError("Unsupported authored SVG element")
        for key, value in node.attrib.items():
            if key.startswith("on") or "href" in key or re.search(r"url\((?!#)", value):
                raise ValueError("Authored SVG cannot load code or external resources")
    return source


def vacuum_art_fingerprint() -> str:
    """Bind geometry, labels and material sources to an immutable lesson revision."""
    return artwork_fingerprint(ARTWORK[0])


def artwork_fingerprint(artwork: ArtworkSet) -> str:
    """Derive source identity without accepting a caller-selected path."""
    return hashlib.sha256(
        "".join(asset_source(name) for name in (*artwork.scenes, artwork.context)).encode()
    ).hexdigest()


def section_asset(spec: LessonSpec, index: int) -> tuple[str, set[str]]:
    """Resolve a registered art set and the static primitive identities it replaces."""
    teaching = spec.teaching
    artwork = next(
        (
            a
            for a in ARTWORK
            if teaching is not None
            and teaching.renderer_fingerprint == artwork_fingerprint(a)
            and spec.canonical in a.revisions
        ),
        None,
    )
    if artwork is None or len(spec.stages) != len(artwork.scenes) or not -1 <= index < len(artwork.scenes):
        raise ValueError("This artwork revision is unavailable; preserve its original media")
    source = asset_source(artwork.context if index == -1 else artwork.scenes[index])
    root = ElementTree.fromstring(source)
    replaced = set(root.attrib.get("data-replaces", "").split())
    # Only trusted artwork enters this markup path. Poses/text remain validated data.
    inner = source[source.index(">") + 1 : source.rindex("</svg>")]
    return inner, replaced
