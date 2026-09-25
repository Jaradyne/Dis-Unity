# Work review: the first Garden integration

**Later same-day decision:** Jared accepted the Collector/residual specialist recommendation and clarified the ten-node grammar, stable teleports and word-instance Chair. [The integration note](../../../operations/INTEGRATION_2026-09-25.md) records the implementation. The discussion below is preserved as the earlier review, including proposals that have since been decided.

Status: design review for discussion with Jared. This adds a worked example and an integration sequence to draft PR #13. No architecture choice is recorded as Jared's decision.

Reviewed on 25 September 2026 by Work Aiden in this ChatGPT/Codex session. Exact model identity is unknown.

- Main: `b27ff7a6dbdfb23ea3e98bcd63c6e9f9ac209856`.
- Live state: `4351e8b62d1887df9a81fb7692e36650225b0258`.
- Chat's original PR #13 head: `2f685fe07323c828f3982306b3a371477c46d90d`.
- [Drive workbook](https://docs.google.com/spreadsheets/d/1eWdwwC9SZ46iM_fnH7BHvUv2OCQicy0c/edit): uploaded Excel, modified 25 September at 01:32:07 UTC. Original SHA-256: `921dd0f5cec613c7b7488ffb113044c85eee861ae6696bf33f42f322b1f4d8bc`.

## Design to take forward

Use the Garden as a readable view of a small, traceable reasoning path. Keep existing Questions, source records, attempts and reflections as the records it points into. Start with one existing Question and the initiating path; let real residuals justify specialized destinations.

The first distinction to make explicit is **a tree step versus an arrival passing through it**. `MIRROR-0005` is a reusable step. A particular comparison needs its own arrival/pass identity, Question ID and epoch, source references, and result at that step. Otherwise five design rows labelled Active can look like five operating research nodes. A workbook row should never silently create a second answer registry.

One root is the shared entry convention. Teleports and returns make the underlying structure a graph, presented as readable trees. Preserve the source node, reason for transfer and return path. A single root should not require one permanently available machine or coordinator.

For an executable version, AND means all required conditions are supported; OR means at least one alternative is supported. Unknown remains distinct from false. `AND/OR` needs explicit named condition groups before execution. A missing measurement cannot become zero, and an unavailable original cannot become a language mismatch.

## What the workbook currently establishes

All eight tabs were read. The original file and its cell formulas were inspected without editing or recalculating it.

| Observation | Integration consequence |
| --- | --- |
| Garden Gate lists ten steps, but Nodes defines five. FUNC-0004, CROSS-0006, RESID-0007, EXIT-0009 and RETURN-0010 have no node rows. | Complete the ten step definitions once, then make both views use the same definitions. |
| Edges includes undefined local destinations and `SPECIALIZED:*`; EXIT and RETURN are absent from its route. | Require real local IDs. Keep an unchosen teleport as a proposal, never a runnable wildcard. Include an ordinary explained/stop route and explicit bounded return. |
| Several Edges relation labels differ from the Data Lists vocabulary. | Agree on the small relation vocabulary before adding a validator or importer. |
| Garden Gate E9 uses `COUNTA(Bosses!G:G)-1`, counting the proposed power and the future TEMPLATE text. | The displayed 2 is not two earned powers. Separate proposed powers from an earned-power record tied to an actual play result. |
| Expected Flow, profiles, specialist lanes and Markov Chair are templates/proposals. | Preserve that status. No record here establishes a running engine, specialist, simulation or public website. |
| Drive reports an uploaded Excel file with `shared: false`. | Native conversion and public read-only access remain unfinished. Preserve the source workbook and verify the eventual public view before calling it public. |

## A small first integration

[GARDEN_SAMPLE_Q18.json](GARDEN_SAMPLE_Q18.json) walks an existing open Question through all ten named steps. It uses the September 25 staged Governor packet as input, with its limitations intact. It is an interface example, not new research or admission of that answer.

Readable version: **A delivered electric vessel is a useful milestone. What freight has it actually completed reliably?** The ordinary control is that delivery of a diesel vessel also does not establish reliable service. The residual is missing operating evidence, not an invented contradiction. The useful destination is one bounded route-performance check under the existing Q18.

| Component | First integration contract |
| --- | --- |
| Garden pass | Stable pass ID; Question ID/epoch; template version; source and parent references; step results; unresolved fields; bounded outputs. Existing record IDs retain ownership. |
| Projection | Render the same pass into a small readable view with links. Human edits are attributed proposals for Work to review, not silent writes to live state. No extra ledger for Jared. |
| Crosscheck/Mirror template | Compare like product, direction, period, units, genre and revisions; retain a normal control; distinguish explained difference, untested comparison and surviving residual. |
| Expected Flow snapshot | Version/as-of time, route/function, source-supported drivers and constraints, expected interval, observed interval, comparison window, calibration and unknowns. Unsupported intervals stay absent. |
| Governor input | Bounded frontier, flow snapshot or explicit absence, relevant reflections, Meaning Tower selections, word flowers, and actual boss/power state. Read once at a meaningful cycle or teleport boundary. |
| Governor response | Actual actor/runtime provenance; input snapshot references; disposition; brief shareable reflection; optional invitations. Silence and "good job" are complete responses. Suggestions do not execute themselves. |
| Re-entry | Preserve original answer and lineage. A peculiar answer may propose a new arrival or linked Question; deduplicate unchanged input and cap depth/work per pass. No automatic reopen or endless loop. |

The Governor's inverted path works backward from an outcome or residual toward the assumptions, dependencies and meanings that produced it. The Expected Flow Engine remains separately inspectable. The current Governor helper prepares a review; it does not establish the distinct actor requested in this handoff. A later bounded actor run needs its own execution record and tested input/output boundary.

Markov Chair can later record a seed, association-graph version, weights, step limit and visited path. Its output goes to an imagination tray. A human or Governor can deliberately adopt an association as a question; it never becomes evidence or permission by being generated.

Keep Clinical Capacity & Judgment, drone industrial substrate, graphene grade/use, country profiles, shock scenarios, revealed priorities and adaptive load as the proposed lanes already in Chat's packet. Begin each only with a narrow question and stopping point. A standing capability profile, a conditional shock scenario and an observed institutional choice are different records. Stable service with mounting effort can be labelled only with evidence about that effort; it is not a composite collapse score.

## Bee decision for Jared

| Choice | Useful property | Cost or limitation |
| --- | --- | --- |
| Reusable Crosscheck Bee | One place to accumulate comparison craft across domains. | Adds a handoff. Independence exists only when a genuinely separate review runs. |
| Collector mode/lens | Ordinary explanations and controls happen close to collection. | Does not provide independent review of that Collector's interpretation. |
| Specialist born on residual | Concentrates attention on consequential uncertainty that survives the initial pass. | Needs a clear birth trigger, budget, stop condition and return path. |

Work's recommendation for discussion: teach every Collector the basic lens, then use the existing birth-request boundary for a consequential residual it cannot resolve. Consider a standing Crosscheck Bee if repeated cases show that shared specialist memory is useful. This recommendation is not yet an accepted architecture decision.

Question to Jared: **Would you like crosschecking to live first inside every Collector, in a standing Crosscheck Bee, or in a specialist called only after a residual survives?**

## Recovery repair to implement next

The latest Week One workflow, [36048555357](https://github.com/Jaradyne/Dis-Unity/actions/runs/36048555357), completed successfully on 24 September. Its saved result is deferred/cooldown, with all three public surfaces retrieved. There is no outcome.json for that deferred run. The latest saved outcome is the earlier `gh-35981423237-2` audit_pending result at 09:29:08 UTC, with a twelve-hour cooldown and audit_tries = 2. The cooldown has elapsed at this review. No rerun was made.

There is a concrete mismatch: `prepare()` selects saved-generation recovery only when audit_tries < 2, while `finalize()` brakes audit_pending at audit_tries >= 3 and the handoff promises three tries. At the live count of 2, another eligible slot can bypass the unfinished saved generation and reserve a fresh POST. This is a code-path finding, not a claim that the bypass has already occurred.

Proposed bounded patch:

1. Use one three-try limit for both selection and terminal handling. Give saved-generation recovery priority. Exhaustion or interruption at the limit must require review rather than fall through to fresh inference.
2. Add a validated audit/content-recovery delay setting. One hour is a proposed Week One value; the old twelve-hour value remains the compatibility default. It affects transient saved-generation GET recovery only. Keep quota waits and authentication/policy brakes intact. It does not add wakeups or rewrite existing cooldown history.
3. Preserve original prompt, generation identity, recovery lineage and zero new POST reservations on recovery. Leave the end date, zero-spend route and NO GROQ unchanged.
4. Verify the live-shaped two-try case reaches the third GET-only attempt; a third unsuccessful/interrupted attempt cannot fall through to a POST; quota/auth brakes survive; invalid timing configuration is rejected; and window/disabled gates still apply. Use synthetic transports, never a credentialed test call.

The patch is specified here for integration after the design discussion; this review commit changes no runtime or configuration.

## A second integration defect found during review

The September 25 staged Governor response names `REFL-EE5CFC158BA9BEB56DBE05`, which is absent from the live mailbox. The related translation/reflection entry is `REFL-EE5CFC158BA9B9D16A9E7BDB`. The response validator rejects unknown IDs. As written, the next importer can post the packet's reflection but reject its response and mark the packet needs_review.

Preserve the original packet. Confirm the intended attribution and add an explicit correction with provenance as part of the reviewed import repair. Do not bypass reference validation or edit the live mailbox manually. This worked example uses only IDs verified in the live mailbox.

## What is alive, and what is next

Public sensing, saved attempts/outcomes, runtime reflections and the mailbox are operating. Dated Chat Governor packets exist; the September 24 reflection/response is present in live state. The API Answer Bee has not yet produced an admitted audited answer in the inspected runs. The distinct repo Governor, Garden execution, Expected Flow Engine, Markov Chair and earned boss powers remain proposals.

Next question for Chat Aiden: **Using one real Week One case, show one difference that ordinary controls explain and one residual worth keeping. What exactly changes at the handoff, and when is silence the best Governor response?** Keep the answer small enough to test the chosen Bee arrangement.

Verification in this review: current Git refs and PR status; latest Actions result; manifest/outcome/source/HUMAN_NOTE records; open Q18 and live reflection IDs; all eight workbook tabs; XML formulas and graph references; current recovery/importer code paths. No new empirical research, model call, workbook edit, live-state write, or runtime test is claimed.
