# Privacy and consent architecture

This is a set of proposed safeguards for a sensitive, future system. It is not legal advice and does not establish compliance with any law or standard.

## Informed and revocable consent

Before any future collection, explain purpose, data categories, intended recipients, limitations, retention approach, and possible consequences in accessible language. Consent should be specific, freely given, recorded, and revocable. A future system must define what withdrawal stops, what records may need to be retained for a justified purpose, and how that distinction is explained. Do not make participation a condition of unrelated support unless an authorized policy explicitly establishes that basis.

## Data minimization and purpose limitation

Collect the least information needed for a stated purpose. Separate identity and contact information from sensitive check-in content where feasible. Reuse or secondary analysis requires a separately reviewed purpose and appropriate permission. Do not collect real victim data in this scaffold.

## Access, encryption, and auditability

Plan least-privilege, role-based access; secure identity and authorization boundaries; protected secrets; encryption in transit and at rest appropriate to the deployment; key management; and tamper-resistant audit records. Audit access to sensitive records without duplicating their contents into logs. Exact controls need threat and implementation review.

## Retention and sensitive-data handling

Define retention, deletion, backup expiry, legal holds, and incident response before launch. Restrict development fixtures to clearly synthetic data. Establish controlled environments and access review for any later real-data work. Do not place secrets or personal information in source control.

## Safe communication and human oversight

Let a person specify safe channels, timing, and content constraints, and avoid sensitive previews or messages that could create risk. Define how preferences are honored by each integration. AI-generated risk information is fallible decision-support and requires appropriate human review; it is not a diagnosis or an autonomous clinical, legal, or emergency decision.
