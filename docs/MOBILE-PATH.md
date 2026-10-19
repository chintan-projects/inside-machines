# Web → PWA → iOS and Android

The first delivery is the Vercel-hosted family alpha. Native application binaries and store submission are later work.

## Reuse boundaries

| Component | PWA | Future native app |
| --- | --- | --- |
| Catalog, lookup, deduplication | Same server API | Reuse `/api/v1` |
| Generation and its budget ledger | Server-side queue phases | Reuse without device model credentials |
| Lessons and assumptions | Version-1 JSON contract | Decode the same validated artifact |
| Narrated videos and captions | HTML video + WebVTT | Native video player with downloaded files/captions |
| Interactive scene | React/SVG renderer | Initially embed the web player, or implement its small shape/transform vocabulary in a native renderer |
| Follow-up chat and feedback | Authenticated HTTP/SSE | Reuse server behavior with platform networking |
| Offline library | IndexedDB, app-shell service worker | Platform file storage and local database; user-scoped download lifecycle |
| Identity and installation | Invite cookie + browser installation | Add durable account/refresh-token flows and secure platform credential storage before a public native release |

The scene contract contains shapes, bounded transforms, causal stages and text. It contains no provider credentials, generated JavaScript or platform UI code. A native renderer must match the stage/transform behavior, not assume that the entire React interface ports unchanged. Keep shared contract fixtures to verify both renderers.

## Recommended sequence

1. Finish the hosted alpha end to end: actual new-machine generation, video, private follow-up, feedback, reuse and observed cost.
2. Test with family for a week using ordinary links and optional PWA installation. Use the owner report to examine requests, repeated use, confusing lessons, failures and cost.
3. Verify PWA cold launch, interrupted downloads, storage eviction, offline logout, text scaling and accessibility on real iPhone and Android devices. Emulated Chrome sizing alone does not prove those behaviors.
4. Choose a native approach based on observed gaps. A wrapper can reuse more UI; native scene and download screens offer more platform control but require additional implementation. Store acceptance is not established by a working wrapper.
5. Add native account recovery, download management, links/sharing, accessibility and lifecycle handling. Add purchasing only after the product and pricing decision is made.

## Inference and keys

Existing published lessons, downloaded videos and included questions do not need a model request for repeat viewing. New generation and fresh chat currently use the server-side OpenAI adapter. The shared gateway can accommodate another hosted adapter later; that integration has not been implemented or benchmarked here.

Customers do not need their own frontier-model API keys. The operator configures the provider and pays for server-side inference. A future optional on-device model is a separate product and engineering choice; it is not a prerequisite for shipping the PWA or native clients.

## What the web alpha must teach us first

Do people return to explanations? Does a visual help them predict what happens? Which machines recur enough for the shared library to save generation cost? How often do people need a fresh follow-up rather than an included question? What are median and tail costs for an accepted new lesson, including failures? Those answers should drive native investment and monetization.
