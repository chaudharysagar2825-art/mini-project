# Database design (conceptual)

`database/schema.sql` and `database/seed_demo_data.sql` are comment-only placeholders. No database schema or seed records are implemented.

## Planned entities

- **Users:** identity references, role assignments, and account lifecycle metadata.
- **Victim cases:** a restricted case context associated with authorized participants.
- **Consent records:** purpose, version, status, and lifecycle events.
- **Safe contacts:** person-approved communication preferences and constraints.
- **Check-ins:** time-stamped, purpose-limited self-reports.
- **Assessments:** future analysis metadata and human interpretation; not diagnoses.
- **Alerts:** review workflow, status, provenance, and disposition metadata.
- **Referrals:** consent-aware destination and status references.
- **Audit logs:** protected records of significant access and workflow events.

## Conceptual relationships

A user may have one or more role-scoped relationships to a case. A case may have consent records, safe-contact preferences, check-ins, assessments, alerts, referrals, and audit events. Assessments may reference their source check-ins and the analysis version that produced them. Alerts and referrals should record appropriate human review and provenance. Exact cardinalities and deletion behavior require domain and privacy review.

## Design decisions required before implementation

Define identifiers, tenant/isolation boundaries, encryption and key management, field-level minimization, access policies, audit integrity, backups, retention and deletion, consent withdrawal behavior, migrations, and synthetic-only development fixtures. Avoid copying sensitive content into logs or analytics. This is not a verified compliance design.
