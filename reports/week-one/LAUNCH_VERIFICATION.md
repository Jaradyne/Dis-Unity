# Week One launch verification

24 September 2026, Work Aiden.

- Runtime commit: `f3354d536514a79366c4b29b2a3a2897613af423`; exact locally reviewed tree `1c55f5e2268e26682b07a771ac8a341cd144f0e9`.
- PR #5 `c83fcf061002720d2216a3b50e4ee8664b4588b3` and PR #6 `2650af478ca38389df4d5e075ff5a8f95910eea5` were read, preserved and merged. GitHub reports both merged/closed.
- Week One workflow ID 365842667 is active, with two UTC wake times and a seven-day runtime gate.
- First live run: 35971438628, success. Separate integrity run 35971438680 and mock worker smoke 35971438650 succeeded.
- EIA diesel: one item returned; EIA Today in Energy: 18 returned, four selected; NWS California: one active alert selected. Six records saved.
- The exact Q-RESEARCH-Q01 request was committed before the provider step. The BYOK preflight returned HTTP 401; no completion POST was made. An auth/configuration result and runtime reflection are durable. Provider eligibility remains unverified; ordinary source operation continues.
- Recovery/provider tests: 10 new tests pass; total existing plus new: 42. A temporary local Git remote exercise verified successful checkpoint publication and rejection of a stale snapshot after another writer's commit.
- Operational outputs reside on `week-one-state`; reviewed code on `main`. Canonical RC-004 was unchanged (52 signals, 26 links, 109 sources).
- A seven-occurrence ChatGPT Week One Governor task was created and confirmed enabled. An immediate run was requested successfully at about 07:52 UTC after the thought-partner import and handoff were published. This confirms dispatch, not completion; a dated staging packet or task response must establish completion.

Follow-up deployment: `e1736dcce786ea0b7d351d6bd3730060592f012d` installs the task mailbox importer. Hosted run 35971974980 and integrity run 35971974949 both succeeded. The preserved provider brake was respected while public sensing continued.

Research context: [first Work review](2026-09-24_FIRST_REVIEW.md), [source ledger](2026-09-24_SOURCE_LEDGER.json). Follow [WEEK_ONE_HANDOFF.md](../../WEEK_ONE_HANDOFF.md) for exact paths and restart boundaries.
