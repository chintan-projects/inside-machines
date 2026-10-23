# Deployment ownership audit and migration record

Updated: 2026-10-22 (Pacific time). **Live application, Neon database and active
private Blob storage are owned by the verified personal Gmail account. GitHub
login authorization remains pending for automatic Git deployments.**

The deployment and spend values below describe the migration snapshot. Later
curated-library releases and paid verification attempts are recorded in the
[integration journal](../journal/2026-10-20-curated-integration.md) and
[native production journal](../journal/2026-10-22-native-integration.md); use the owner
workspace for current spending.

## Public preview update — 2026-10-22

The owner explicitly requested public visitor access. Production now runs
`31a9360` at Ready deployment `dpl_5dk1png3msomcnr21wSfLuALeHjG` under the same
verified Gmail identity and resources. Vercel Authentication now covers **preview
deployments only** (`deploymentType=preview`); no plan upgrade was needed.
All four production aliases were checked without cookies or bypass headers and
return the current public shell and `public_access=true`. Owner administration
and private conversations retain application authorization. Private Blob URLs
still reject anonymous access; public lesson media is served through the app.

The app's $50 ceiling is unchanged. The observed ledger remains $5.988597538461539
with zero reservations, including earlier conservative uncertain-billing
allowances. No paid call was made for public access or verification. Thirty prior
lesson revisions and existing private histories were preserved. Exact native
preview permissions expose the refrigerator path and GPU insight with draft
labels; they do not activate replacements, approve quality or send release notices.
See the [public preview journal](../journal/2026-10-22-public-preview.md).

The migration snapshot below retains its historical protection/spend values.
GitHub's login connection is still required for automatic Git deployments; the
current production build was deployed explicitly with the isolated personal CLI.

## Verified ownership

| Item | Verified destination |
| --- | --- |
| Vercel primary account | `chintansanghvi5@gmail.com`, username `csanghvi` |
| Workspace | `cdt9s-projects`, `team_5LoBlu5cjsIC1oEzRItHF6o8` |
| Membership and billing | Confirmed Owner; Hobby active; billing email matches Gmail |
| Project | `inside-machines-alpha`, `prj_ok8CKAxGVlADIiJyECM6wukxrUnn` |
| Neon | Existing `inside-machines-db`, `store_ZqexGu717dNkmfMV`, Free |
| Active private Blob | `inside-machines-assets`, `store_3LF9qetVQ3IptgHA`, `iad1` |
| Migration runtime | `dpl_HY4oCMJcg2wpWXxZVa2dH1WAa1Zk`, Ready, Gmail workspace |

Use [Inside Machines](https://inside-machines-alpha.vercel.app) or the
[Gmail workspace alias](https://inside-machines-alpha-cdt9s-projects.vercel.app).
The old source-workspace stable alias and its Git-main alias were explicitly
reassigned to this same deployment to preserve previously shared links.

Vercel Authentication remains Standard Protection
(`all_except_custom_domains`). App family/owner access remains enabled. The
application's AI ceiling is still **$50** and its recorded spend is unchanged at
**$3.212849538461539**, with zero outstanding reservations. This application limit
is not a Vercel account-wide billing limit. No paid model calls or plan upgrades
were made for the migration.

## Original cause

The source Hobby scope `chintan-4466s-projects` was a personal workspace owned by
an identity whose verified primary and billing email was the work address. It
was separate from the Liquid AI organization, which did not own this project.
The distinct Gmail account requested access to its protected deployment; Vercel
sent the notification to the work-email owner. A personal-looking workspace name
was insufficient evidence of ownership. Approving viewer access or changing the
work identity's email would not have moved the application and its resources.

The source login and unrelated Liquid AI team membership were preserved.

## Completed execution

1. Authenticated the Gmail account through Vercel's device login, with its CLI
   credentials isolated from the existing source login. Verified primary email,
   owned workspace, membership, plan and billing email through authenticated APIs.
2. Privately inventoried project configuration, integration connections, aliases
   and all three environment targets. Exported available environment values;
   **sensitive values such as the production OpenAI key are not exportable**.
   Those were preserved by Vercel's native project transfer, and the new hosted
   runtime confirms generation remains enabled. An environment export alone is
   not a complete recovery copy of sensitive credentials.
3. Backed up and validated the complete database and every private Blob object.
   Saved database/collection hashes and object hashes in ignored, owner-only
   local files. Rechecked zero active jobs and reservations before transfer.
4. Installed the free Neon integration in the Gmail workspace, then used the
   documented [cross-account claim flow][claims] and [Neon resource flow][flows]
   to transfer the existing project and Neon
   resource. Vercel returned zero resource-transfer errors and a fulfilled Neon
   provider result. Both resources retain their IDs and now report the Gmail
   workspace as owner. Neon remains connected to the project.
5. The normal [Blob transfer picker][stores] could not select this separate Hobby account.
   Created a Gmail-owned **private** store instead, copied all **17 objects /
   12,765,940 bytes**, and downloaded each destination object to verify its hash
   and size. Reconnected it using the normal `BLOB_READ_WRITE_TOKEN` in production,
   preview and development. Removed the temporary migration-prefixed connection.
6. Verified session/invite/owner settings and the budget across all three targets.
   Relinked the checkout to the Gmail-owned project. Re-ran engineering checks
   and the Linux deployment packaging verifier before a staged production build.
7. Built the local runtime from `2e02599` using the verified Gmail CLI identity,
   holding the existing production domains while the candidate was checked. Its
   hosted health check confirmed the preserved sensitive API key was injected.
8. Briefly paused the previous production deployment and took a fresh snapshot.
   Changed only **25 lesson/job storage references** to the 17 verified new
   objects in one transaction. Preserved lesson specs, revision identities,
   artifact bytes/hashes, private history and usage accounting. The reverse
   mapping was checked against the snapshot for rollback.
9. Verified the candidate, promoted it, reopened production, and reassigned the
   legacy stable aliases. The active runtime has no source-owned storage
   dependency. The disconnected source Blob store is retained solely as a
   rollback copy; it was not deleted.

All credentials, snapshots, downloaded media, verification sessions and API
inventories remain ignored by Git and excluded from deployment packaging.

## Observed verification and limits

- Ruff, strict mypy, 163 backend tests including three disposable Postgres tests,
  86.89% backend coverage, TypeScript, ESLint, ten JavaScript tests, frontend build
  and Linux packaging verifier passed.
- Authenticated hosted checks passed: health, generation readiness, owner session,
  active catalog, all nine existing videos with original byte hashes, MP4 range
  requests (206), and captions. The family API rejects unauthenticated access
  (401); the private Blob URL rejects public access.
- The database comparison preserves every existing user/session, all private
  chats, feedback, events, learning reviews and the complete ledger. The only new
  private records retained are an explicitly created migration verification owner
  user and login event. Its temporary session was revoked after verification;
  the revoked credential correctly receives 401. Lesson specs and usage totals
  are unchanged.
- No new paid generation/chat operation was requested. Queue packaging passed;
  a new post-migration paid queue job was not run. These checks establish the
  observed migration behavior, not factual certification, beginner learning
  quality, or owner approval of the lesson craft. BUG-004 remains open.

## Remaining GitHub authorization

Cross-account claiming cleared the Git repository link. The original
repository is now public at `chintan-projects/inside-machines`; its history
was preserved and the current framework merged to `main`. Reconnecting it again
after publication through the Gmail CLI still returned Vercel's explicit
**Add a Login Connection** requirement.

The owner must connect GitHub account `chintan-projects` in the Gmail Vercel
account's [Authentication settings][connections]. This is separate from CLI
device authentication. Do not merge accounts or remove a work-account login
connection silently if Vercel reports a conflict.

After authorization, reconnect the original repository with the Gmail profile,
verify its `main` branch link, and verify the next Git-triggered deployment's
owner, resources and Ready state. Automatic Git deployment is not restored merely
because the CLI deployment succeeded. Track this as BUG-008.

## Future deployment and recovery

The checkout now links to `team_5LoBlu5cjsIC1oEzRItHF6o8`. The default machine-wide
CLI profile was left separate from the Gmail login for unrelated work. Use the
isolated personal profile (`--global-config .vercel/migration-target-auth`) and
`--scope cdt9s-projects`, and reverify the primary email and resource ownership
before deployments. A missing personal profile must prompt Gmail login, not
creation of another project under the default work identity.

After a new deployment is Ready, also verify the legacy
`inside-machines-alpha-chintan-4466s-projects.vercel.app` and
`inside-machines-alpha-git-main-chintan-4466s-projects.vercel.app` aliases. These
cross-account migration aliases do not advance with the two ordinary personal
production aliases automatically. Check their project/owner first, explicitly
assign them to the verified Ready runtime using the isolated personal profile,
and verify all four targets before importing data that requires the new schema.
An alias containing `git-main` does not establish a Git automation connection.

Keep source snapshots and the disconnected Blob copy until the owner is
satisfied with the migrated service. A rollback must reverse only the internal
asset references, restore the matching prior deployment/environment and preserve
new private activity. Never replace the entire live database with an old snapshot
or uninstall Neon to repair an integration connection.

[connections]: https://vercel.com/account/authentication
[projects]: https://vercel.com/docs/projects/transferring-projects
[claims]: https://vercel.com/docs/deployments/claim-deployments
[flows]: https://vercel.com/docs/integrations/create-integration/marketplace-flows
[stores]: https://vercel.com/docs/storage#transferring-your-store
