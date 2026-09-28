# Digestion threshold

API material arrives here for Digest Aiden and other authorized thought partners. Capture and delivery do not imply that anyone has digested or reviewed it. The Governor remains paused.

- [Live CSV ledger](https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/digestion/threshold/api/interactions.csv)
- [Live per-run material packets](https://github.com/Jaradyne/Dis-Unity/tree/week-one-state/digestion/threshold/api/runs)
- [Existing digestion discussion](../../handoffs/chat_aiden/2026-09-27_digest-threshold/INTEGRATION_AFTER_DIGESTION.md)

Jared requested full API records on September 27, 2026 Pacific. GitHub renders CSV files as tables; the ledger can also be downloaded into Excel or Sheets. Each new row represents an HTTP attempt, including its checkpoint before sending. It links to a JSON record containing the method, URL, application request headers and body, returned status and headers, complete received body, timestamps and any transport error. Bodies retain their original UTF-8 text or base64 bytes, with a hash of the saved body. Provider-returned fields are retained even if the operational parser does not use them. Credentials, bearer tokens and authentication cookies are redacted.

The recorder covers the repository's enabled OpenRouter completion calls, catalog and key checks, generation/content lookups, Week One EIA/NWS requests and standalone public scout retrievals. Chat/Work platform connector calls and Git transport are outside this repository runtime. New runtime adapters must use the recorder. It does not request private model internals that an API has not returned.

The existing response-size limits remain. Oversized responses, interrupted reads, timeouts and absent responses are explicitly marked incomplete; the record never claims to have bytes that did not arrive. Application headers are recorded, not a packet capture of TLS or HTTP framing. Redirects remain blocked and their available response material is retained.

Historical rows are labelled `legacy_partial`. They index the original prompt, filtered response, outcome and source materials that still exist. They are run summaries, not an invented count of historical HTTP calls. Missing raw fields remain missing. Blank cost means unknown; zero is retained only when reported. The retired September 24 generation keeps its recorded operator disposition.

Each run has a threshold packet containing file paths, GitHub links and hashes for its saved materials. Full bodies live once under `operations/week-one/runs/<run-id>/api/`; the threshold points to them. Runtime output and the ledger are saved on `week-one-state`; reviewed code and this contract stay on `main`. Journaling and indexing are deterministic and make no new inference call.

GitHub CSV rendering: [official documentation](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-csv-and-tsv-data).
