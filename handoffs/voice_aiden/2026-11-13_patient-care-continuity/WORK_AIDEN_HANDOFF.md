# Voice Aiden -> Work Aiden: Patient Care Continuity (Medical Garden proposal)

**Date:** 2026-11-13 (Pacific)  
**Status:** Proposed handoff for human/Work review. No Medical Garden implementation, independent source research, diagnosis, provider contact, or canonical admission is claimed.  
**Provenance:** Voice discussion, not a new Digest review. The earlier Chat/Digest medical-access direction was discussed conversationally; this packet does not claim to reproduce an independently retrieved Chat/Digest document.

## Why this matters

A clinically appropriate service can exist on paper while the route from **symptoms to evidence-based investigation and usable care** breaks at referral intake, specialty triage, tests, authorization, communications, cost disclosure, or follow-up. Administrative activity (a scheduled service, an offered class, a referral sent, a rights notice, an accommodation request) must not be mistaken for a specialist evaluation, an actual treatment, a completed accommodation, or improved health.

The generalizable failure mode to investigate is **service substitution or route drift**: a request for medical assessment may be redirected toward a distinct education/management offering. That can be entirely legitimate in some cases and a mismatch in others. The evidence question is what was ordered, what was offered, why the route changed, and whether the patient retained a viable path to requested clinical assessment.

Use *synthetic or public-policy* examples; do not encode an individual's health history or correspondence.

## Proposed mechanism: Patient Care Continuity

Reuse, rather than replace, existing **Thread of Continuity**, **Safeguard Reality Check**, **Relay Continuity**, **First Evidence Arrival**, and Garden's ten-node supplied-pass pattern. Track a longitudinal **care pathway** whose stages and outcomes remain separate:

1. **Need and clinical question** — what type of evaluation or intervention is sought; distinguish diagnostic investigation from counseling/management.
2. **Referral intent and dispatch** — requesting clinician, specialty/service type, date, reason, supporting records; do not assume receipt.
3. **Receipt and triage** — whether the receiving service acknowledged the referral, changed its destination, provided reasons, or requested prerequisites.
4. **Prerequisites and coverage** — an updated test, insurance eligibility, prior authorization, network status, informed cost disclosure. *Requiring a prerequisite is not the same as providing the specialist visit; a self-pay service is not proof all diagnostic care is self-pay.*
5. **Communication and accommodation** — channels offered, authorized care coordination, request/response, functional accessibility and whether the alternative actually worked. Distinguish an authorization to communicate from permission to consent to medical treatment.
6. **Appointment and clinical action** — booked, attended, examined, tests performed, findings explained, management or treatment selected. Keep counseling and clinical investigation as different service types.
7. **Outcome, follow-up, and remedy** — documented clinical benefit or residual symptoms, next referral, appeal/grievance, corrected route, denial and response, actual remedy. "Unknown" is the default until supported.

At each stage record: *claimed policy*, *responsible actor*, *dated observed action*, *source and lineage*, *verification standard*, *patient cost type if documented*, *status* (completed / failed / pending / unknown / contested), *next handoff*, and *patient-usable effect if established*. Do not infer causal or legal conclusions from chronology or absence of a record.

## Questions for the Medical Access, Clinical Evidence and Outcomes wing

- When a clinician refers a patient to a medical specialty, what does the written referral say, what service does scheduling actually offer, and what explains any difference?
- Which components of the pathway are **diagnostic medical care**, **audiology tests**, **counseling/education**, or **elective management**? What does each payer actually cover, with authorization and provider/network restrictions distinguished?
- Does a requested updated test become a bridge to specialist care, or an indefinite loop? Is there evidence of a scheduled/attended medical assessment?
- When disability affects phone-based scheduling, can the person obtain an effective alternative (writing, coordinator communication, properly scoped representative authorization)? Track request, response, implemented access, and limits rather than assume compliance.
- Who can correct a route mismatch: referral sender, specialty triage, authorization team, patient relations, payer grievance process? Is a correction acknowledged and realized?
- What **clinical investigation, treatment decision, and patient-relevant outcome** can be verified? "Offered help" is not "received useful care." Equally, uncertainty about cause is not by itself proof of negligent care.

## First bounded demonstration / Work deliverables

**A.** Create a compact typed pathway record or extension compatible with existing shared relays and safeguard assessments; prefer shared references over copying historical evidence. Do not force a clinical causal inference into an administrative relay.

**B.** Build **one clearly fictional, nonidentifying fixture**:
- a specialty referral sent and confirmed received;
- triage asks for a dated prerequisite test;
- a separate self-pay educational/management service is offered;
- insurance coverage for the medical visit is initially *unknown* (not presumed denied);
- a written communication accommodation and scoped care-coordinator authorization are *requested*, not assumed granted;
- no specialist appointment, treatment or outcome is claimed without a corresponding event.

Then append a **fictional later revision** that documents a successful redirect/authorized appointment, preserving every earlier event. Add a contrasting failed/unknown variant if useful for negative tests.

**C.** Propose one narrowly scoped **public-source** research check before drawing any real-world conclusion: compare one provider's documented specialty referral / scheduling policy with one payer's published coverage / authorization rule relevant to that service type. Record publication/effective dates, network exceptions, access limitations, and exact source lineage. If source access fails, return UNKNOWN, not a policy assertion.

**D.** Save a single supplied ten-node Garden pass and Chat/Digest review intake, with clear evidence thresholds and one next test. This handoff alone does not authorize outreach, collection, medical record processing, claims adjudication, or a new recurring Bee.

**E.** Add replay and negative tests: referral dispatched != received; received != triaged; test prerequisite != specialist visit; management counseling != medical diagnostic evaluation; optional fee != all care uncovered; accommodation requested != provided; proxy for scheduling != healthcare decision maker; no documented outcome != confirmed failure; formal rights != successful remedy; shared source reused != corroboration.

## Privacy, health, and authority boundary

**Do not publish or infer any identifiable patient's symptoms, diagnoses, finances, address, treating clinicians, appointments, emails, disability records, or insurance identifiers** in this public repository. The motivating conversation is private. No individual complaint is established in this packet. A provider offering a different service is not automatically wrongdoing; a quoted estimate is not verified billing; coverage and medical appropriateness require case-specific primary records.

This is a method and an investigatory question, **not medical advice**, an assertion that an accommodation has been granted, a legal violation finding, or a measured treatment outcome. Before reusing statutory claims (ADA/Section 504, HIPAA authorization) or medical guidelines, independently verify current authoritative source text and jurisdiction and separate the law's requirements from practical enforcement.

Do not send email, file grievances, schedule appointments, contact providers or payers, start monitoring, copy private chats, run a live provider model, activate Governor authority, or alter canonical evidence without separate explicit authorization.

## Existing project anchors

- [PR #38 Thread of Continuity](https://github.com/Jaradyne/Dis-Unity/pull/38)
- [PR #39 Safeguard Reality Check](https://github.com/Jaradyne/Dis-Unity/pull/39)
- [PR #43 Relay Continuity](https://github.com/Jaradyne/Dis-Unity/pull/43)
- [PR #52 Care, Consent and State Power](https://github.com/Jaradyne/Dis-Unity/pull/52) and `reports/care-autonomy/20261104/HANDOFF_CHAT_DIGEST.md`
- [PR #53 RC-015 all-Garden review](https://github.com/Jaradyne/Dis-Unity/pull/53) and `reports/all-garden/20261104/HANDOFF_CHAT_DIGEST.md`

**One-line handoff to Workypoo:** Make the gap between a documented medical referral and *verified, accessible clinical care* measurable, while never converting administrative motion into treatment success or turning a private person's distress into public case data.
