# Independent Medical Access review

November 16, 2026 Pacific · reviewer `medical_final_review` · **PASS WITH LIMITS**.

The reviewer is separate from the runtime and public-policy authors. This review covers the final files pinned below and the bounded acceptance criteria in Voice's merged PR #55 handoff. It does not approve a patient investigation or make an empirical clinical, coverage or legal finding.

## What passed

- Inspected the schema, finite milestone validator, shared reference resolution, journal and projections. One fictional case preserves 21 milestone types and two dated revisions. A successful administrative correction and booking remain distinct from delivered clinical care. The original assessment cutoffs and supplied timestamps are retained; fixture dates are not actual patient observations.
- Confirmed matching observation/service types are required for evidence-backed stages. Dispatch cannot establish receipt; triage, prerequisite testing and education cannot establish medical assessment; requests cannot establish implemented accommodation; scheduling authority cannot establish treatment consent. Optional fees do not determine another service's coverage, and missing outcome records cannot establish success or failure.
- Confirmed the final contradiction checks reject both completed and failed status when matching evidence conflicts. Mixed positive/negative evidence can remain contested. Policy, request or booking records cannot establish a usable effect merely by changing their effect flag. A documented administrative route repair is allowed while clinical benefit stays UNKNOWN.
- Source records and journal entries are hash-bound. Revisions retain earlier event references, stage meanings and contrary evidence; future observations cannot support an earlier cutoff. Fourteen fictional event/source pairs resolve to one fictional family. Shared historical references are reused, not copied into a new archive or counted as independent corroboration.
- Ran `python scripts/patient_care.py check` and all **16** `test_patient_care.py` tests successfully. The check reconstructs the saved pass twice with byte-identical outputs: ten nodes, one resting branch, zero provider calls. Garden state SHA-256: `0fd99c8ecd65ca64d6719191010e8ff34aabb71de92af80bc335a91afb47da50`.
- Inspected the README, Chat/Digest intake, source ledger and CI addition. The actual proposed public follow-up is a single service-code match; the fixture's hypothetical later-attendance question is explicitly inactive. No personal patient data appears in the new fixture. Public-policy context is separate from fictional evidence.
- Confirmed shared Garden, Continuity, Safeguard and Relay runtime files, the core tree registry and canonical state are unchanged. Canonical SHA-256 remains `16d04f8bb35a588caca60517f90a11944cfbafac7951402d059a6d6131de97b7`. CI adds an offline replay check and no schedule.

## Public-source challenge

Reopened selected sections of [UCSF's group page](https://ears.ucsf.edu/en/tinnitus), [UCSF's tinnitus-care page](https://www.ucsfhealth.org/care/services/tinnitus-care), [Alliance's 2026 handbook](https://alamedaalliance.org/wp-content/uploads/MCAL-MBR_2026-Alliance-EOC_10242025-clean-current-.pdf) and [erratum2](https://alamedaalliance.org/wp-content/uploads/D.0058C_20260715_AAH_Mcal_EOC_Errata2Cln.pdf) on November 16. The selected service distinctions, fee descriptions, audiology category, network qualifications and authorization exceptions agree with the authored comparison. The report correctly does not turn a self-pay offering into blanket diagnostic noncoverage or published coverage into delivered care.

This was a selected-source challenge, not a complete re-audit of all eight surfaces, every handbook provision or code-specific eligibility. The authors' source ledger preserves undated publication/effectiveness fields and filename clues separately. Manual web inspection is expressly not a complete raw-response archive. A provider's promises and payer's procedures do not establish observed compliance or a protective result.

## Disposition and limits

Accept this bounded mechanism and fictional demonstration for integration, subject to the coordinator's repository-wide checks. No blocking defect remains in the reviewed scope. The demonstration validates consistency with supplied records, not truth of arbitrary new evidence. Human source classification/review remains necessary; hashes provide cooperative history integrity, not protection against an authorized editor deliberately rewriting and rehashing an entire journal. No independent clinical, medical-necessity, statutory-compliance or claims-adjudication engine is implemented or implied.

No contact, private-record acquisition, recurring collection, provider launch, Governor change or canonical admission was performed by this review. Richmond/Campus operational questions and actual essential-delivery outcomes remain outside this review.

## Exact reviewed files

SHA-256 hashes complete bytes. Review and checkpoints are excluded to avoid self-reference. Repository base at final review: `422d65fcf0e539b0cb27574771a30526fb9fcbff`.

| File | SHA-256 |
| --- | --- |
| `README.md` | `1d32dc66f329e5039cd3a4dca1dbaeb87c46d0bac101607f54d77196453853f4` |
| `.github/workflows/verify.yml` | `cb9d51efaacfc10544cc2000476a5fad635492d9d1269d74ee7ba13aa3fcdda1` |
| `scripts/patient_care.py` | `0c01102c9839fdd3f0b2a0cac89ec5b9a9882130ccd5798b7ecfcc5bc75e0e44` |
| `schemas/patient-care.schema.json` | `22ba370c073c34c1deb33c8a7d8210b234eaf5734c91fbfbf5a0629bd2abf64e` |
| `tests/test_patient_care.py` | `74edbf0a3765a9931d733e12feff8c36572b3e860935302aad5f466def3abeb1` |
| `config/garden-trees/medical-access.json` | `16c47aa4e0f5e75d281b7c854c13022d3e88a10d93c454615c9364e923f3a828` |
| `operations/medical-access/20261113/inputs.json` | `58b71132e0aadb73e9329ef0fa6fa1c97c2a560b115a7b2a927f09a3643f698d` |
| `operations/medical-access/20261113/journal.json` | `5c8e72849bc844d9f7e3e527a312f84977cd90176ccec7cb85c8b4f22754fc94` |
| `operations/medical-access/20261113/records.json` | `fb4574ee2217f0e2df6bde6ded4c36b9195da983c5b6fdb5c91028683ed8421f` |
| `operations/medical-access/20261113/references.json` | `b4849f10922f3220b6abcdc56d400ae1842c2290687b1e6229292b4a1c920275` |
| `operations/medical-access/20261113/scenario.json` | `79879419d4a5399bf0b82a656860a92152521404551fcdce54e321b463271fec` |
| `reports/medical-access/20261113/README.md` | `0ff3edd6a33bb6c76b91416122e29f3f39e435dd41ff5e90b2b0e4a66f6f2ee6` |
| `reports/medical-access/20261113/HANDOFF_CHAT_DIGEST.md` | `c947db4166407ef4dfb027e8e6aa0aba5876bf1cda9238f2ef1156f5c7aaa9f3` |
| `reports/medical-access/20261113/HANDOFF_INTAKE.md` | `dc1308ed03470815cd4056a3f5ffa5cb0d2cfe5715591904d5df12e24092c7a0` |
| `reports/medical-access/20261113/POLICY_COMPARISON.md` | `523167ddbbf54833287e57653ffa4b137c0e132df934414271d4b3864a2a1800` |
| `reports/medical-access/20261113/policy-sources.json` | `8bab0440d8554bbc55c79fdda73b349d0fe98523a47c5ee2ea318d3c93875d73` |
| `reports/medical-access/20261113/generated/PATIENT_CARE.json` | `321c889ee86bf0d11e26f03e508bb9cbb938140008e8867cb8e9008ff2f0a81e` |
| `reports/medical-access/20261113/generated/PATIENT_CARE.md` | `3101a156dbf082cb842680bde535db80e6e95ef51a5f4c9daa32ab1c642c3775` |
| `reports/medical-access/20261113/generated/garden/digestion/threshold/garden/MEDICAL-ACCESS-FICTIONAL-20261115.json` | `7c1b9306b6a4ca7b5137fe7083daf23659a83e34cd9cb1f8e9fc8cc47387daa5` |
| `reports/medical-access/20261113/generated/garden/digestion/threshold/garden/branches.csv` | `dfc1a0d3cb61eba3d74be2911aa238ef4fc26d4eae556b1f1e6a5595aab54e9a` |
| `reports/medical-access/20261113/generated/garden/operations/garden/runs/MEDICAL-ACCESS-FICTIONAL-20261115.json` | `933f1c9b7b7a39448a0b19b855e8ab42c47b58e8f61ebbf0e8b292be0383f8de` |
