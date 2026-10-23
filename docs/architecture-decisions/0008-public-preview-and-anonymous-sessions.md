# ADR 0008: public learning previews with private anonymous sessions

Date: 2026-10-22. Status: implemented and locally verified; hosted publication verification pending.

The owner explicitly requests a public repository and app with no visitor login,
invite or special access. The previous family gate prevents that experience.
Removing owner authorization or merging every visitor into one account would
instead expose private discussions or paid production controls.

Public mode therefore permits anonymous reading of lesson metadata, learning
paths, diagrams, video and captions. The browser silently obtains a unique opaque
visitor session for private questions, feedback, interest requests and offline
identity. An existing owner/member cookie is reused. Credentials and private
conversations never enter shared artifacts or a public catalog response.

Owner administration still requires owner authorization. Visitor requests collect
interest without paid authoring; optional live chat retains atomic budget and
anonymous admission limits. Bounded durable counters share the existing Store
transaction, retain active limits independently of telemetry rotation and migrate
legacy admission events before trimming. Active buckets are never evicted to
make room for a new visitor. No model call is needed to browse or play a saved
explanation. Closed-mode deployments remain supported by explicit configuration.

Public access is not evidence of learning quality. A new owner-operated preview
permission binds the exact root spec/video, graph and node artifacts. It exposes
those native drafts with a visible review label. A changed or revoked binding
fails closed. Unresolved same-artifact rejections remain blocking across
composition changes. This operation does not write quality passes, activate a replacement,
alter old revisions or send release notifications. The existing human review and
quality release contracts remain separate.

The public repository must contain source, third-party notices, a current README
and deliberately selected screenshots. Raw captures, production media/data,
credentials and private conversations remain excluded. Review all reachable Git
history for actual secrets before changing visibility. Do not invent a root
license or imply third-party endorsement.

Verify cookieless public reads, separate visitor chats, protected owner operations,
paid-authoring denial, budget/throttle behavior, preview binding/revocation, old
private-history preservation, phone/desktop journeys and hosted no-login access.
Publish screenshots only after the public visitor flow renders correctly.
