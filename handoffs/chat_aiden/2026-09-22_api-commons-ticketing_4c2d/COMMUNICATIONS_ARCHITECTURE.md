# Communications architecture — soft and replaceable

Human interaction should not depend on one platform.

Possible surfaces:
- GitHub — durable public technical record
- Thinking Mailbox / published Sheet — low-friction structured input
- future Discord — conversational human/agent exchange, field reports and commands
- email — subscriptions, attachments, direct correspondence and sources with no public feed
- future website/app (possibly Vercel-hosted) — friendly public portal/dashboard
- future Bluesky/other social platforms — public discovery and discussion if they become a better fit

Architecture rule:
**The platform is an interface, not the memory.**

Every important inbound message should become a Question, source record, field report or correspondence packet before it matters to canonical research.

## Why email exists when RSS exists

Use RSS/API first when available.

Email adds things feeds often cannot:
- private/direct human replies
- newsletters with no RSS
- mailing lists
- attachments
- subscription-only alerts
- requests for collaboration
- replies to outreach
- account-specific notices

Recommendation: create a dedicated Dis-Unity research Gmail rather than using the user's personal/Jaradyne mailbox. Give automation read-only OAuth initially. The mailbox can remain low-stakes/public-minded while still protecting its credential.

## Discord later

A public Discord becomes valuable when there is actual human participation to coordinate. Prefer bot commands/forms for structured reports and needs/offers, while leaving ordinary channels for conversation.

Do not make Discord canonical storage.
