# Reflection and shared notes integration — 24 September 2026

Base: `0983c7a44c7e31de953d7bd7e1d6cc68ab225d60`. Actor: Work Aiden in the current interactive session. User direction: reflection throughout the system, a distinct mailbox attended by the governor, collaboration among all thought partners, and an open notes space for participants who know the address.

## Implemented

- `scripts/reflections.py`: attributed, content-addressed contributions and append-only governor responses in `operations/reflections/mailbox.json`; atomic writes, idempotent retries, page visibility and checkpoint/attempt recovery.
- Worker v0.3: reflection requested in the same response, run/parent/level references, saved output before projection, honest missing-coverage notes and explicit mock provenance.
- `agents/governor.json` and `scripts/governor.py`: on-demand review packet. The reviewer chooses a response and can invite Chat, Work, the human or other partners. Original notes and later reconsiderations remain available. No response automatically executes its suggestions.
- Agent template, continuing instructions and Chat/Work handoffs include the practice. GitHub worker artifacts preserve the mailbox with attempt records.
- First Work reflection and an attributed Work review in the governor role begin the practice. They are not output from an independently running governor model.
- **Dis-Unity Open Notes** created in Google Sheets with a simple Notes tab, welcome, contributor/date/topic/note/reference columns and one discussion question. Its address is not placed in this public repository. Creation and contents verified; public link editing awaits Google browser authentication because the connector supports named-user/domain sharing but not anyone-with-link editing.

## Verification and limits

All 32 Python tests passed. Canonical validation passed with the same RC-004 digest. The native notes sheet was read back, exported and visually checked; the browser itself is not signed in, so Google-rendered verification and anyone-with-link editing remain unverified.

The new tests cover all 50 distinct application subcalls retaining parent references, repeat projection without duplicates, all-or-nothing invalid batches, preserved originals through changed governor decisions, actual runtime provenance overriding authored claims, recovery from the saved attempt after projection failure, and review without consuming or executing notes.

No empirical records, closed RC-004 artifacts or evidence cutoff change. No live provider, recurrent schedule, external message, resource commitment or automatic notes importer is enabled. A role definition is not a running process. The reflection interface supports application-level call trees; it cannot observe internal model neurons or hidden reasoning. Across separate machines, stage artifacts/PRs for coordinated merging; the local lock is not distributed consensus.

PR #5 (`chat-aiden/provider-policy-human-window-20260922`, head `485dcc28acd6431817cf6308daeec2e00f14479c`) has been inspected. It contains the later role-fit/free-provider clarification, the no-Groq rule, reported credential availability and proposed quiet-window behavior. That packet remains staged; this change does not activate or implement its adapters or schedules.

Next: finish notes access after authentication; have Chat develop reflection practice from actual experience; separately integrate the already-received provider clarification and one verified, bounded adapter. Keep rough shared notes easy to contribute, and preserve evidence admission separately.
