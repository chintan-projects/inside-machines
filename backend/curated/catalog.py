"""Trusted curated scope registry; no runtime imports, endpoints or credentials from clients."""

from types import MappingProxyType

from .home import HOME
from .kitchen import KITCHEN
from .plumbing import PLUMBING
from .thermal import THERMAL
from .transport_computing import TRANSPORT_COMPUTING

SYSTEMS = MappingProxyType({s.id: s for s in (*TRANSPORT_COMPUTING, *KITCHEN, *HOME, *THERMAL, *PLUMBING)})
if len(SYSTEMS) != 20:
    raise ValueError("The curated launch registry must contain twenty unique systems")
