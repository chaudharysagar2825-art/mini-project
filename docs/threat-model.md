# Threat model (architecture stage)

This preliminary list supports future design work. It is not a completed security assessment.

| Threat | Potential impact | Planned architecture-level mitigations |
|---|---|---|
| Unauthorized access or account compromise | Exposure or misuse of sensitive records | Strong authentication design, role-based authorization, least privilege, session controls, and access review. |
| Data leakage or insecure storage/transport | Loss of confidentiality | Data minimization, encryption boundaries, protected keys, environment separation, and privacy-conscious logging. |
| Insider misuse | Improper viewing or disclosure | Narrow role scopes, audit events, periodic access review, and defined sanctions/response procedures. |
| Insecure integrations | Disclosure, spoofed messages, or unsafe contact | Isolated adapters, explicit consent and safety constraints, authenticated interfaces, and integration-specific assessment. |
| Credential exposure | Unauthorized system access | Secret manager in future deployment, no committed credentials, rotation and revocation procedures. |
| Malicious or malformed input | Abuse, service disruption, or misleading analysis | Input validation, size/rate controls, secure parsing, and human review of consequential outputs. |
| Alert abuse or false positives | Distress, unsafe contact, or inappropriate escalation | Human review, provenance, documented escalation policy, safe-contact checks, and contest/correction paths. |
| Privacy violations or re-identification | Harm to a person or loss of trust | Purpose limitation, minimum necessary access, retention limits, de-identification review, and incident response. |

Future work should map assets, actors, trust boundaries, abuse cases, and residual risk with security, privacy, domain, and lived-experience reviewers. Controls must be validated before deployment; this scaffold does not provide them.
