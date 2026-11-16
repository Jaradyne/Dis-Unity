# Medical Access, Clinical Evidence and Outcomes

**A referral, a booked appointment and received care are different events.** Patient Care Continuity keeps the clinical question connected to the service requested, the actual actions taken and the result for the patient.

Completed for review November 16, 2026 Pacific. [Readable fictional pathway](generated/PATIENT_CARE.md) · [Public-policy comparison](POLICY_COMPARISON.md) · [Chat/Digest handoff](HANDOFF_CHAT_DIGEST.md) · [Review](REVIEW.md).

## The demonstration

One explicitly fictional case has two retained assessment revisions. It begins with a specialty referral that was sent, received and triaged. A prerequisite test and written communication alternative are requested; a separate self-pay management service is offered. Medical coverage and usable clinical care are initially unknown.

The second revision adds completion of the prerequisite, correction of the referral route, appointment authorization, scoped coordinator authorization and booking. These are successful administrative steps in the fiction. **Attendance, specialist assessment, treatment, health benefit and effective written accommodation remain UNKNOWN.** The system does not infer failure from missing outcome evidence or infer protection from formal policy.

Every milestone retains its service type, responsible actor, evidence references, verification standard, cost description, next handoff and any supported usable effect. Source families are counted once. The [original records](../../../operations/medical-access/20261113/records.json) are referenced through the shared resolver; no historical archive is duplicated. Original entries remain in the [journal](../../../operations/medical-access/20261113/journal.json).

## Replay

From the repository root:

```bash
python scripts/patient_care.py validate
python scripts/patient_care.py check
python -m unittest discover -s tests -p test_patient_care.py -v
```

`replay` prints the reconstructed assessments. `build` regenerates the saved projections after a deliberate input revision; `check` compares them without changing inputs. It reconstructs the supplied Garden pass twice and compares exact output bytes. The pass has ten nodes, one resting branch and zero provider calls. The supplemental tree does not change the core registry or dispatch policy.

The tests reject substituting dispatch for receipt, receipt for triage, a prerequisite or counseling for medical assessment, an optional fee for blanket exclusion, a request for an implemented accommodation, scheduling authority for treatment consent, missing outcomes for failure, formal rights for a remedy, or repeated sources for independent corroboration. Both positive and negative conflicting records remain contested instead of becoming a confirmed success or failure. History and source mutations fail validation.

## What is empirical

The [separate policy check](POLICY_COMPARISON.md) inspected one provider's public service/referral descriptions and one payer's handbook and corrections. It identifies service and authorization distinctions. It establishes no individual's eligibility, diagnosis, inaccessible appointment, wrongdoing or health outcome. Policy excerpts are not inserted as evidence that the fictional events happened.

The fixture retains a hypothetical question about a later attendance record. It authorizes no record acquisition. The one proposed public follow-up is a service-code match between an official diagnostic referral form and a current payer authorization entry, with effective date and network conditions preserved. Even a positive match would establish only a documented pathway, not delivered care.

The [handoff intake](HANDOFF_INTAKE.md) distinguishes the exact Voice proposal from conversational Chat/Digest direction. This bounded implementation adds no private records, outreach, eligibility decision, recurring monitoring, provider inference, Governor authority or canonical admission. Replay verifies the supplied record's consistency; human source review remains necessary to establish what it means.
