# Deployment ownership audit and correction plan

Audit date: 2026-10-19. Status: **migration pending authenticated target scope
verification**. The owner has been asked for the personal workspace URL after
signing in with Gmail. Hold Git pushes and deployments until that destination is
verified.

## Confirmed findings

- `inside-machines-alpha` belongs to a personal Hobby scope, separate from the
  Liquid AI organization. The organization does not own this project.
- The authenticated CLI user and deployment creator are the work-email owner.
  Account Settings lists only the work email, marked **Verified Primary**. The
  source Hobby scope also uses the work email for billing.
- Vercel's External Access list contains a pending request from a distinct
  requester identity for the stable project alias. The supplied access-request
  email identifies that requester as the personal Gmail account. The Gmail
  account's authenticated profile, primary email, workspace ownership and plan
  have **not** yet been inspected.
- Vercel Authentication uses **Standard Protection**. The separate requester
  lacks deployment access, which explains the access request. Vercel sends
  account notifications to the owner's primary email, explaining delivery to the
  work address. Approving viewing access would not transfer ownership.
- The source scope contains the connected Neon database `inside-machines-db`
  (Free, Available) and private Blob store `inside-machines-assets` (Available).

Evidence: read-only CLI/API account, team and project metadata; Account Settings;
Deployment Protection / External Access; Storage inventory; and the supplied
access-request screenshot. No database contents or private assets were browsed.
See [Vercel Authentication][authentication] and [primary email routing][emails].

## Correction plan

1. In a separate browser profile or private window, authenticate with the Gmail
   account. Verify its primary email, personal workspace URL, owner role and plan.
   Preserve the source login. Prefer moving to this distinct account rather than
   changing the existing work identity's primary email across its teams.
2. Before any move, privately inventory environment-variable targets, integration
   connections, database identity, Blob references, application signing secrets,
   aliases and Git linkage. Preserve existing data and configuration without
   recording credentials here. Verify the destination can access the private Git
   repository and accommodate the project and resources.
3. Choose the supported project transfer route after verifying both scopes.
   Standard transfers require ownership of the source and membership of the
   destination. Cross-account claim transfers are also documented. Project
   transfers preserve deployments, configuration, aliases, Git linkage and
   project environment variables, but integrations and Blob require separate
   handling. Variables defined in `vercel.json` need separate review. The claim
   documentation only promises automatic associated-resource transfer for Prisma;
   do not assume it moves Neon or Blob. See [project transfers][projects] and
   [cross-account claims][claims].
4. Plan Neon independently, preserving the existing database and its data. A
   resource transfer requires Owner/Member access on both scopes, Neon installed
   at the destination, and all project connections disconnected. The documented
   operation is irreversible. Alternatively, a supported whole-installation
   transfer requires Neon absent from the destination and all source connections
   disconnected. Choose one route; their destination prerequisites differ.
   Disconnecting removes integration variables from project configuration;
   existing deployments retain their deployed variables. Reconnect the resource
   and restore the intended environment targets before a new deployment. See
   [resource transfers][resources] and [installation transfers][installations].
5. Transfer the existing private Blob store separately through Storage → store →
   Settings → Transfer Store, subject to verified destination eligibility.
   Preserve its objects and references, reconnect the project, and verify the
   private-access configuration. See [store transfers][stores].
6. After all connections are restored, authenticate the CLI as the Gmail owner,
   relink the checkout to the verified destination, and inspect environment
   configuration without printing secret values. Run deployment readiness checks
   before a controlled deployment. Verify ownership, Git linkage, production
   health, existing lesson/job records, private asset delivery, session continuity
   and access while signed in as the Gmail owner. Use existing records for
   validation; do not trigger a paid lesson merely to test the migration.

If dual-scope membership or Hobby limitations block resource transfer, stop and
resolve a supported migration route with the owner. No paid plan upgrade is
assumed. Keep Vercel Authentication enabled; disabling protection is not an
ownership correction. Do not uninstall Neon to make room: uninstalling a native
integration deletes its associated products and data.

**Audit outcome:** no project settings, access grants, credentials, deployments,
database data or stored assets were changed or moved. This document records a
pending plan, not a completed account migration.

[authentication]: https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication
[emails]: https://vercel.com/docs/accounts#changing-your-primary-email-address
[projects]: https://vercel.com/docs/projects/transferring-projects
[claims]: https://vercel.com/docs/deployments/claim-deployments
[resources]: https://vercel.com/docs/integrations/install-an-integration/product-integration#transfer-a-resource-to-another-team
[installations]: https://vercel.com/docs/integrations/install-an-integration/transferring-an-integration
[stores]: https://vercel.com/docs/storage#transferring-your-store
