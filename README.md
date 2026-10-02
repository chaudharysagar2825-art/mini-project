# Manas Setu

**SIH 2026 · Problem Statement SIH26094**  
**AI-Powered Dynamic Mental Health Monitoring and Distress Prediction System for Victims of Atrocities**  
Ministry of Social Justice and Empowerment · Software · MedTech / BioTech / HealthTech

## Purpose

Manas Setu is a proposed privacy-preserving, human-supervised decision-support and referral architecture for the stated SIH problem. It is intended to guide future design of consent-based check-ins, authorized review, and safe referral boundaries. It is not a diagnosis or an autonomous clinical, legal, or emergency decision-maker.

> **This repository is an architecture/scaffold repository. Application implementation is intentionally not included.**

## Architecture

The proposed structure separates a web client, backend API boundaries, a future AI/risk analysis layer, conceptual data design, integration adapters, and deployment scaffolding. Intended flow: person and chosen channel → consent and identity boundary → backend services → data layer and bounded analysis → human review → authorized support or referral.

**AI assists. Humans review. Authorized services respond.** Any future AI-generated risk information is fallible decision-support and requires appropriate human review.

## Repository structure

| Path | Planned responsibility |
|---|---|
| `docs/` | Problem framing, requirements, system design, privacy, security, and roadmap |
| `frontend/` | Future web-client architecture placeholders |
| `backend/` | Future API, model, service, and security boundaries |
| `ai/` | Future risk, NLP, voice, and evaluation boundaries; no models |
| `database/` | Conceptual database design placeholders; no functioning schema |
| `integrations/` | Future SMS, IVR, notification, and Tele-MANAS adapter boundaries |
| `deployment/` | Documentary container and reverse-proxy scaffolding |
| `scripts/` | Future setup and demo-data boundaries |
| `.github/` | Contribution, security, issue, PR, and CI templates |

## Technology direction

The scaffold points toward React/TypeScript with Vite for a possible frontend and Python for possible backend and AI boundaries. These are planning choices only; dependencies are not installed and no application workflows are implemented.

## Privacy and safety principles

- Informed, purpose-specific, revocable consent and safe-contact preferences.
- Data minimization, purpose limitation, least-privilege access, and a reviewed retention lifecycle.
- No real victim information, personal data, medical records, credentials, or production secrets in this repository.
- Human review for AI-generated signals; no AI score is a diagnosis or final decision.
- No claim of legal compliance, clinical efficacy, or operational readiness.

## Current status

Architecture/scaffold only. Source files are placeholders; SQL, CI, Docker, and integrations are documentary scaffolding. No functional application, real data, external service connection, or production deployment is included.

## Future roadmap

See [`docs/implementation-roadmap.md`](docs/implementation-roadmap.md): architecture validation, backend foundation, database, frontend, AI/risk evaluation, integrations, security testing, evaluation, and deployment readiness.
