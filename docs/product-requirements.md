# Product requirements (proposed)

This is a requirements outline for a future implementation. None of the capabilities below are implemented in this architecture repository.

## Person-facing experience

- Offer an understandable, accessible way to learn the service's purpose, limits, and data use.
- Let a person choose whether to participate, what to share, preferred language/channel, and safe-contact constraints.
- Support voluntary check-ins with the ability to skip, pause, or withdraw.
- Explain how to reach appropriate human support; do not imply the system is an emergency service.

## Consent and identity

- Record purpose-specific consent and its version, status, and relevant timestamps.
- Make consent revocable and define what happens to future processing and retained records after withdrawal.
- Separate identity/contact data from check-in content where feasible; apply least-privilege access.

## Check-ins and distress monitoring

- Accept only information necessary for a clearly stated purpose.
- Preserve source, time, and context needed for a reviewer to interpret a check-in.
- Treat any future model or rules output as a fallible signal for review, never as diagnosis or a final decision.
- Provide a documented path for correction, contesting, and contextual review.

## Counsellor and authorized-support workflow

- Present only information the current role is authorized to see.
- Show provenance and limitations of any generated signal, with a human review state.
- Allow an authorized reviewer to document a disposition and appropriate next steps under future approved procedures.
- Support referral coordination without promising service availability or outcome.

## Alerts and referrals

- Define who may create, view, acknowledge, and close a future alert.
- Require human review and a documented rationale before consequential action.
- Respect consent, safe-contact settings, escalation procedures, and service boundaries.
- Integrations remain disabled until separately assessed, approved, and implemented.

## Dashboards, auditability, and operations

- Provide role-scoped summaries and avoid exposing unnecessary sensitive details.
- Record access and significant workflow events in an appropriately protected audit trail.
- Establish retention, deletion, incident response, accessibility, and service-continuity requirements before launch.

## Quality attributes

Future design work should assess privacy, security, usability, accessibility, reliability, language support, explainability, and safe failure. These requirements need validation with relevant experts and affected communities; this document is not a clinical protocol or compliance determination.
