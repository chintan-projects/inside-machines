# Interactive explanations

Default to one self-contained HTML file. Keep causal state in a pure, inspectable
model and let the drawing render that state. Use a purposeful control, plain labels,
an optional prediction/reveal and a changed-situation question. A next button alone
is not the mechanism. Core explanation must stand alone before optional depth.

Physical artwork uses the actual Anatomy kit. An installed `anatomy` skill or the
repository's `vendor/anatomy` is the dependency; do not duplicate its source in this
skill. If it is unavailable, offer installation from the upstream
[MIT-licensed Anatomy repository](https://github.com/wheresryan22/anatomy), following
the host's skill installer. Inspect/pin the source and retain its license. A
generic diagram may be useful when explicitly requested, but do not substitute
one while claiming the Anatomy workflow ran.

Computation uses labeled arrays, operations and dependencies; read `computing.md`.
Do not make up an appliance whose moving parts conceal an algorithm. For a code
change, use the actual diff and a bounded deterministic trace. Keep source paths
and revision evidence next to the relevant claim.

Use browser tooling available in the current environment. Serve only the trusted
output on loopback when required, rather than exposing the project root or private
conversations. Check the actual desktop/narrow layouts and key states. Keep reset,
keyboard, reduced-motion and sound-off paths usable. Viewport simulation is not a
real-phone check, and passing structural checks does not establish human learning.
