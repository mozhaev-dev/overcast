# Learning and delivery plan

## Working method

Each increment introduces a small user-visible capability or validates a concrete architectural risk. The mentor explains the goal and relevant Python concepts; the user writes code; review and verification establish the next checkpoint.

Python topics are introduced when needed: names and object identity, mutability, scope and closures, exceptions, context managers, iterators, type annotations, dataclasses/enums, imports and packaging, and asynchronous execution. This is not a syntax course before building the product.

## Delivery sequence

1. Approve product scope and define the first episode's expected output.
2. Select and initialize the Python toolchain together: package layout, environment/lockfile, formatter/linter, type checker, tests, and basic CI.
3. Validate a minimal MCP round trip with the chosen external agent before investing in integration.
4. Build the first persistent slice: initialize workspace, create and retrieve a topic; introduce schema migrations and storage integration tests.
5. Create and retrieve episodes with topic snapshots, artifact directories, and recoverable filesystem failures.
6. Implement explicit workflow state, artifact contracts, and concurrency protection incrementally.
7. Implement plan proposal and user approval, then research/script steps with external-agent skills and traceable outputs. Expose saved materials for on-demand discussion.
8. Integrate TTS with explicit failure, retry, and credential handling.
9. Complete audit/repair and end-to-end recovery checks, then validate a real episode for daily use.

The sequence may change when evidence exposes a risk. Do not assign several implementation steps at once.

## Current checkpoint

PRD approved; packaged application and local quality tools initialized. See PROGRESS.md for the current user-owned assignment. Add basic CI once a meaningful test exists.
