# Frontend prototype outline (planned)

The frontend directories describe intended areas for a later prototype. No screens, forms, routes, or workflows are implemented here.

## Conceptual areas

- **Authentication:** future entry boundary; identity verification and recovery need a separate security design.
- **Consent:** plain-language purpose, choices, status, and withdrawal controls.
- **Victim dashboard:** a private, accessible overview of the person's own participation and available support options.
- **Check-ins:** optional, accessible self-report prompts with skip and pause choices.
- **Safe contact:** preferred channels, timing, and constraints; avoid revealing sensitive context through notifications.
- **Alerts:** human-review status and carefully limited information for authorized roles.
- **Referrals:** consent-aware referral status and next-step information, subject to service availability.
- **Support dashboard:** role-scoped queue and context for trained/authorized human review.
- **Authorized-user dashboard:** minimum necessary case and audit context for approved roles.

## Structure

`src/app`, `routes`, `components`, `features`, `services`, `hooks`, `types`, `styles`, and `assets` separate future application concerns. Feature folders map to auth, consent, safe contact, check-ins, alerts, referrals, and dashboards. The API client file is a boundary placeholder only.

## Prototype principles

Future design should be trauma-informed, multilingual, accessible, discreet where safe, and tested with appropriate consent and safeguarding. It should clearly explain that automated analysis is fallible decision-support and that the interface is not a substitute for emergency or clinical services.
