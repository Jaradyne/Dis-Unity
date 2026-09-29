# Garden operational state

The [operation spine](../../docs/GARDEN_OPERATIONS.md) adds `operations/<operation-id>.json` for provider-neutral requests, contextual candidates, exact exposed context and attributed returns. Inspect the live Q18 acceptance and operation ledger under `week-one-state:digestion/threshold/garden-operations/`. The on-demand Garden workflow executes reviewed main packets; repeated default runs replay its saved acceptance.

See [the traversal contract](../../docs/GARDEN_TRAVERSAL.md). `runs/<run-id>.json` holds a complete saved run: immutable logical event history, original configuration and input, current branches, route decisions and replay hashes. Actual runtime files belong on `week-one-state`; this README and the runtime stay on main.

Every accepted command projects a branch spreadsheet and per-run material reference into `digestion/threshold/garden/`. The example under `examples/garden-traversal/worked/` is a supplied demonstration, not a live run. No Garden scheduler is enabled.
