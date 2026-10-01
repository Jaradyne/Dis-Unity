# API materials for digestion

[Open the CSV ledger](interactions.csv) · [Per-run material packets](runs/)

43 recorded HTTP exchanges; 20 historical run summaries with partial coverage; 2 operation records without HTTP exchanges. Historical summaries are not a count of API calls.

Each new exchange preserves the method, URL, request headers/body, status, response headers/body and transport errors before parsing. Credentials and authentication cookies are redacted. Bodies exceeding existing transport bounds, interrupted reads and missing responses are explicitly marked incomplete. Unknown cost stays blank; zero means a reported zero. Full provider-returned fields are retained in the exchange record; the smaller operational response is a separate projection.

Packets link and hash all saved run materials. Delivery means available for digestion, not already digested. Governor review remains paused. No extra inference is created by recording or indexing.
