# Postwar, DHS and ICE: recorded research materials

**RC-006 intake for Jared and Digest.** Reports are in [Military Conscience and Institutional Safeguards](../../../../reports/military-conscience-and-institutional-safeguards/README.md). This preserves12 direct public-document HTTP exchanges:10 successful responses and2 HTTP406 error responses. Requests and responses were captured through `scripts/api_records.py`; credentials/authentication cookies are redacted.

Received bodies are stored losslessly beside their exchange metadata. Each JSON points to its body file and records length, encoding and SHA-256. No failed response is presented as a successfully retrieved court docket. The court dockets were readable separately through parsed platform web output.

| Record | HTTP | Bytes | Source IDs | Exchange / received body |
|---|---|---|---|
| API-aaup-court-documents-0001 | 200 | 630,835 | R08 | [metadata](retrievals/aaup-court-documents/api/0001.json) / [body](retrievals/aaup-court-documents/api/0001.pdf) |
| API-aaup-court-documents-0002 | 200 | 96,552 | R10 | [metadata](retrievals/aaup-court-documents/api/0002.json) / [body](retrievals/aaup-court-documents/api/0002.pdf) |
| API-aaup-court-documents-0003 | 200 | 271,950 | R09 | [metadata](retrievals/aaup-court-documents/api/0003.json) / [body](retrievals/aaup-court-documents/api/0003.pdf) |
| API-additional-public-documents-0001 | 200 | 566,228 | I04 | [metadata](retrievals/additional-public-documents/api/0001.json) / [body](retrievals/additional-public-documents/api/0001.pdf) |
| API-additional-public-documents-0002 | 200 | 14,011 | C04 | [metadata](retrievals/additional-public-documents/api/0002.json) / [body](retrievals/additional-public-documents/api/0002.txt) |
| API-additional-public-documents-0003 | 200 | 94,012 | C05 | [metadata](retrievals/additional-public-documents/api/0003.json) / [body](retrievals/additional-public-documents/api/0003.txt) |
| API-adjacent-agencies-0001 | 200 | 268,862 | A04 | [metadata](retrievals/adjacent-agencies/api/0001.json) / [body](retrievals/adjacent-agencies/api/0001.pdf) |
| API-adjacent-agencies-0002 | 200 | 499,761 | A06 | [metadata](retrievals/adjacent-agencies/api/0002.json) / [body](retrievals/adjacent-agencies/api/0002.pdf) |
| API-court-dockets-0001 | 406 | 995 | R03 | [metadata](retrievals/court-dockets/api/0001.json) / [body](retrievals/court-dockets/api/0001.txt) |
| API-court-dockets-0002 | 406 | 995 | R06 | [metadata](retrievals/court-dockets/api/0002.json) / [body](retrievals/court-dockets/api/0002.txt) |
| API-gao-public-documents-0001 | 200 | 1,908,421 | See request URL | [metadata](retrievals/gao-public-documents/api/0001.json) / [body](retrievals/gao-public-documents/api/0001.pdf) |
| API-gao-public-documents-0002 | 200 | 1,026,899 | C02 | [metadata](retrievals/gao-public-documents/api/0002.json) / [body](retrievals/gao-public-documents/api/0002.pdf) |

[Machine-readable material manifest](packet.json) contains exact URLs, times and hashes. [Assembly manifest](assembly_manifest.json) pins source/event inputs. Government statutes, audits, court opinions and the procurement document are retained with attribution; no full copyrighted news articles are included.

## Recording limits

Built-in web and GitHub connectors expose their own parsed or normalized outputs, not the full upstream HTTP exchanges or provider billing. Source catalogs, checkpoints and Git history identify the observable work, but do not reconstruct missing transport fields. Earlier interrupted query-log fragments are not presented as a complete log. This packet contains no OpenRouter or other inference-provider request, and no invented cost receipt.

The PDFs were text-inspected at relevant passages. Selected images were visually checked for the GAO timeline, AAUP judgment/stay, and Park Police signature date. The glove acquisition PDF is distinct from the inaccessible original military assessment. Provenance and review scope are in [METHOD_AND_REVIEW.md](../../../../reports/military-conscience-and-institutional-safeguards/METHOD_AND_REVIEW.md).

Publication makes these materials reviewable. It does not activate a Bee or admit research to RC-004.
