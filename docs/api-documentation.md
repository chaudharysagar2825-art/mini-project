# API boundaries (planned)

No API endpoints are implemented by this repository. The groups below are conceptual service boundaries for a later implementation; they do not describe working routes, payloads, or guarantees.

| API group | Future responsibility |
|---|---|
| Authentication | Establish and manage an appropriately secured session. |
| Cases | Maintain authorized case context and lifecycle. |
| Consent | Record, inspect, and revoke purpose-specific consent. |
| Check-ins | Receive and retrieve permitted check-in records. |
| Alerts | Support human-reviewed alert workflow and audit events. |
| Referrals | Coordinate consent-aware referral status. |
| Dashboards | Provide role-scoped, minimum-necessary summaries. |
| Audit | Record and expose protected audit information to authorized reviewers. |

Before implementation, define authentication, authorization, role scopes, input validation, versioning, error handling, rate limits, idempotency, privacy-safe telemetry, retention, and abuse controls. Sensitive operations need an explicit threat and privacy review. AI-generated information must retain provenance and review status and must not be exposed as a diagnosis or autonomous decision.
