# Mini Project

## Manas Setu architecture scaffold

- **Repository:** Mini Project (mini-project)
- **Project:** Manas Setu
- **SIH 2026 problem statement:** SIH26094 — AI-Powered Dynamic Mental Health Monitoring and Distress Prediction System for Victims of Atrocities
- **Organization:** Ministry of Social Justice and Empowerment
- **Category / theme:** Software / MedTech, BioTech and HealthTech

## Purpose

Manas Setu is a proposed privacy-preserving, human-supervised decision-support and referral architecture for the stated SIH problem. It outlines how future consent-based check-ins, authorized human review, and safe referral boundaries could fit together.

> **This repository is an architecture/scaffold repository. Application implementation is intentionally not included.**

It is not a diagnostic system or an autonomous clinical, legal, or emergency decision-maker. No feature described here should be read as implemented or operational.

## Architecture at a glance

The planned boundaries include a web client, backend API, data layer, future AI/risk analysis components, integration adapters, and deployment scaffolding.

Person and chosen channel → consent and identity boundary → backend services and data layer → future decision-support analysis → authorized human review → support or referral services.

**AI assists. Humans review. Authorized services respond.** Any future AI-generated risk information is fallible decision-support, not a diagnosis, and requires appropriate human review.

## Repository structure

| Directory | Planned responsibility |
|---|---|
| docs/ | Problem framing, requirements, architecture, privacy, security, and roadmap |
| frontend/ | Future web-client structure and feature boundaries |
| backend/ | Future API, model, service, and security boundaries |
| ai/ | Future risk, NLP, voice, and evaluation boundaries; no models |
| database/ | Conceptual data design; no functioning schema |
| integrations/ | Future SMS, IVR, notification, and Tele-MANAS adapter boundaries |
| deployment/ | Documentary container and reverse-proxy scaffolding |
| scripts/ | Future setup and synthetic demo-data boundaries |
| .github/ | Contribution, security, issue, PR, and CI templates |

See [system-architecture.md](docs/system-architecture.md) for the high-level design and [technical-blueprint.md](docs/technical-blueprint.md) for component boundaries.

## Technology direction

The scaffold points toward React/TypeScript with Vite for a possible frontend and Python for possible backend and AI boundaries. These are planning choices only. Dependencies are not installed, and no application workflows are implemented.

## Privacy and safety principles

- Informed, purpose-specific, revocable consent and safe-contact preferences.
- Data minimization, purpose limitation, least-privilege access, and a reviewed retention lifecycle.
- No real victim information, personal data, medical records, credentials, or production secrets in this repository.
- Human review for AI-generated signals; no AI score is a diagnosis or final decision.
- No claim of legal compliance, clinical efficacy, or operational readiness.

Read [privacy-and-consent.md](docs/privacy-and-consent.md) and [threat-model.md](docs/threat-model.md) for the proposed safeguards and risks.

## Current status

Architecture/scaffold only. Source files are placeholders; SQL, CI, Docker, and integration files are documentary scaffolding. No functional application, real data, external service connection, or production deployment is included.

## Future roadmap

The proposed phases are documented in [implementation-roadmap.md](docs/implementation-roadmap.md): architecture validation, backend foundation, database, frontend, AI/risk evaluation, integrations, security testing, evaluation, and deployment readiness.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
