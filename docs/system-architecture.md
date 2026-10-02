# System architecture (high level)

All components below are proposed architecture boundaries. This repository does not implement them.

```text
Victim / User
      ↓
Mobile / Web / Chatbot / IVR / SMS
      ↓
Consent + Identity Boundary
      ↓
Backend Services
      ↓
Data Layer
      ↓
AI / Risk Analysis Layer
      ↓
Human Review
      ↓
Alerts / Referrals / Support Services
```

The listed channels are possible future access channels, not existing integrations. Consent and identity boundaries govern whether information may be collected and used. Backend services would enforce authorization and workflow rules; the data layer would apply a reviewed retention and protection design. An analysis component could provide a bounded signal with provenance and uncertainty for authorized review.

**AI assists. Humans review. Authorized services respond.** AI output is decision-support only; it is not a diagnosis and must not replace appropriate human oversight or make final clinical, legal, or emergency decisions. A human reviewer considers context and approved procedures before action. Any notification or referral requires separately defined consent, safety, and service workflows.

Future deployment requires threat modeling, privacy assessment, clinical/domain review, accessibility work, operational planning, and validation. No service in this diagram is live in this repository.
