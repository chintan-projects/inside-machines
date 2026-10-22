"""One finite, repository-approved native renderer manifest shared with the web build."""

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .native_contracts import ID, SHA, NativeData, NativeLessonSpec
from .settings import ROOT

REGISTRY_FILE = ROOT / "native/registry.json"


def canonical_digest(value: object) -> str:
    """Use the same Python canonical serialization for native registry/proof identity."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class NativeSource(NativeData):
    path: str = Field(min_length=3, max_length=240)
    sha256: str = Field(pattern=SHA)

    @model_validator(mode="after")
    def local_source(self) -> "NativeSource":
        if Path(self.path).is_absolute() or ".." in Path(self.path).parts or "\\" in self.path:
            raise ValueError("Approved native source paths must remain inside the repository")
        return self


class RendererRegistration(NativeData):
    id: str = Field(pattern=ID)
    fingerprint: str = Field(pattern=SHA)
    lessons: list[str] = Field(min_length=1, max_length=12)
    sources: list[NativeSource] = Field(min_length=1, max_length=80)
    spec_sha256: dict[str, str] = Field(min_length=1, max_length=12)

    def source_identity(self) -> str:
        """Spec hashes are outside this payload to avoid a self-referential fingerprint."""
        return canonical_digest({"id": self.id, "lessons": self.lessons,
                                 "sources": [s.model_dump(mode="json") for s in self.sources]})

    @model_validator(mode="after")
    def bound_registration(self) -> "RendererRegistration":
        if (len(set(self.lessons)) != len(self.lessons)
                or set(self.spec_sha256) != set(self.lessons)
                or [s.path for s in self.sources] != sorted({s.path for s in self.sources})
                or any(len(h) != 64 or any(c not in "0123456789abcdef" for c in h) for h in self.spec_sha256.values())
                or self.source_identity() != self.fingerprint):
            raise ValueError("Native registration must bind unique lessons, exact source bytes and spec hashes")
        return self


class NativeRegistry(NativeData):
    schema_version: Literal["native-renderers-1"]
    renderers: list[RendererRegistration] = Field(max_length=32)

    @model_validator(mode="after")
    def unique_registry(self) -> "NativeRegistry":
        if len({r.id for r in self.renderers}) != len(self.renderers):
            raise ValueError("Native renderer identities must be unique")
        ids = [lesson for renderer in self.renderers for lesson in renderer.lessons]
        if len(set(ids)) != len(ids):
            raise ValueError("A native revision has exactly one approved renderer")
        return self


def renderer_for(spec: NativeLessonSpec) -> RendererRegistration:
    """Resolve only the deployed repository manifest; clients never supply registrations."""
    from .starters import digest_spec

    registry = NativeRegistry.model_validate_json(REGISTRY_FILE.read_text())
    registration = next((r for r in registry.renderers if r.id == spec.renderer.id), None)
    if (registration is None or registration.fingerprint != spec.renderer.fingerprint
            or registration.spec_sha256.get(spec.canonical) != digest_spec(spec)):
        raise ValueError("The exact native artwork, rules, cues and lesson metadata are not registered")
    return registration


def verify_sources(registration: RendererRegistration) -> None:
    """Local production verifies the actual approved files before importing prebuilt media."""
    for source in registration.sources:
        path = (ROOT / source.path).resolve()
        if not path.is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != source.sha256:
            raise ValueError("Native production source changed; prepare a new registered revision")
