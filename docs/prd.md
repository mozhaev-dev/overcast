# Product requirements

Status: approved on 2026-10-14. Requirements may be revised as implementation produces new evidence; record material changes explicitly.

## Origin

This draft reconstructs the Evercast/Siftwave decisions from saved project notes. The original checkout and PRD were unavailable on 2026-10-14. It preserves product boundaries, but is not a verbatim migration of the original PRD. Python implementation choices require fresh decisions.

## Problem and outcome

A single user wants to turn selected topics into researched audio episodes using an external agent, while keeping production state and artifacts durable, inspectable, and recoverable locally.

The MVP succeeds when the user can create a topic, create an episode from it, guide an agent through the defined production workflow, generate audio, and resume interrupted work without losing accepted artifacts or corrupting state.

## Users and execution model

- One local user; no authentication or multi-tenant service.
- A CLI initializes and operates an explicitly selected user workspace.
- An external agent performs research, reasoning, source evaluation, episode planning, script writing, and on-demand discussion of saved episode materials.
- A local MCP server exposes domain operations and workflow control to the agent.
- The application integrates with a TTS provider for audio generation. Provider and output format are undecided.
- The source checkout and generated user workspace are separate. Initialization writes to the selected workspace.

## MVP capabilities

### Topics and episodes

The user can create, inspect, list, and edit topics. A topic is a persistent direction for multiple episodes, as narrow or broad as the user wants. Its prompt expresses the user's interests, audience, angle, exclusions, and preferences; it can request thematic research or fresh news without introducing separate podcast types in the MVP.

The following settings are configured when creating or editing a topic:

- Episode language.
- Target episode duration, expressed in minutes. This guides script generation; it is not a guarantee of exact audio length.
- Presentation format: monologue or dialogue.

Defaults, supported values, and validation limits will be defined before implementing topic settings. Deletion semantics also remain open.

The user can create, inspect, and list episodes. The agent selects each episode's focus using the topic prompt and previous episodes. The MVP does not accept a separate user-authored episode assignment. Creation snapshots the topic's name, prompt, and effective production settings so later topic edits do not change existing episodes.

Each episode has a durable identity, workflow state, version, timestamps, and associated artifacts. Structured state and artifact metadata live in SQLite; content and audio live in the filesystem.

### Core entities and fields

These are conceptual fields, not a finalized database schema or Python class design.

| Entity | Fields and responsibilities |
| --- | --- |
| Application settings | TTS provider/model, monologue voice, dialogue speaker voices, and supported synthesis/output parameters. Credentials are stored separately. |
| Topic | `id`, `name`, `prompt`, `language`, `target_duration_minutes`, `format`, `created_at`, `updated_at`. No separate description or podcast-type field in the MVP. |
| Episode | `id`, `topic_id`, immutable topic-settings snapshot, agent-selected title/focus (initially unset), workflow state, concurrency version, timestamps, and artifact references. Record the actual synthesis settings used for generated audio. |
| Episode artifacts | Candidate/ranked sources, proposed and approved plan, research notes, script, and audio. Metadata identifies the episode, artifact kind, and revision; content is stored in the workspace. Exact contracts remain to be designed. |

Technical step instructions describe how to perform work; the topic prompt describes what the user wants. Application rules enforce mandatory approval and valid state transitions independently of prompts.

### Production workflow

The MVP has one explicit workflow:

`FindSources -> RankSources -> ProposeEpisodePlan -> AwaitPlanApproval -> ResearchAndSummarize -> WriteScript -> GenerateAudio -> Completed`

| Step | Required result |
| --- | --- |
| FindSources | Candidate sources with identifiers and retrieval references |
| RankSources | Selected sources with evaluation and selection rationale |
| ProposeEpisodePlan | A brief proposed focus and list of items to include in this episode |
| AwaitPlanApproval | User approval of the current plan; corrections return to plan preparation |
| ResearchAndSummarize | Research notes and summaries traceable to sources |
| WriteScript | An episode script grounded in accepted research |
| GenerateAudio | Audio generated from the accepted script |
| Completed | All required artifacts accepted and audio available |

These are semantic requirements; filenames, schemas, validation rules, and the precise completion protocol remain to be specified.

Persist the proposed plan and approval state. Do not proceed to research or script writing until the user approves the current plan. Corrections revise the proposal and require renewed approval. Restarting the application must preserve the pending proposal and waiting state. Approval is a user decision; an agent cannot infer or grant it from source content or the topic prompt. Preliminary source evaluation is allowed before approval.

Agent Skills explain how to perform each step. MCP reports state and required outputs, accepts validated results, and enforces allowed transitions. Skills are ordinary local files under the generated workspace's `.agents/skills`; MCP does not serve as a skill-text registry.

Invalid or stale transitions must fail without changing accepted state. Concurrent attempts to update an episode must not silently overwrite each other. The version/concurrency contract will be specified before workflow implementation.

### Discussion after listening

The user can ask the external agent to discuss a selected episode using its saved script, approved plan, sources, and research notes. The script explains what was heard; source material supports deeper questions. There is no mandatory `CreateDiscussionContext` step or separately generated context artifact in the MVP. The application provides access to existing materials on demand; a compact derived context can be introduced later if their size warrants it.

### Recovery and inspection

The user can inspect state, artifacts, and actionable failures, and resume incomplete episodes.

SQLite and filesystem writes cannot share a transaction. If episode directory creation fails after the database record is committed, retain the record and report the inconsistency for repair.

- `audit`: read-only inspection of database/filesystem inconsistencies.
- `repair`: conservative recovery of known missing infrastructure; no deletion of unknown or user-authored files.
- `purge`: explicitly requested destructive cleanup, with its scope made clear.
- Targeted preflight checks prerequisites needed for the requested operation.

## Quality requirements

- Validate inputs and keep artifact paths inside the selected workspace.
- Use atomic replacement for artifact writes where appropriate and define recovery for partial operations.
- Version and test database migrations; reject databases newer than the application's supported schema.
- Define retry and idempotency behavior for state-changing operations and TTS requests, including ambiguous provider failures.
- Treat retrieved content as untrusted data; it must not authorize domain operations or override workflow instructions.
- Keep credentials out of tracked files and provide actionable errors without exposing secrets.
- Keep MCP protocol output separate from diagnostic logging.
- Test domain rules, persistence/migrations, filesystem failure recovery, and CLI/MCP boundaries with meaningful integration tests.
- Verify a minimal real agent/MCP round trip before building the full agent workflow.

## Out of scope

- Internal LLM orchestration or a general workflow engine.
- Web UI, hosted API, deployment platform, user accounts, and multi-tenancy.
- Scheduler, distributed workers, and a job queue.
- Podcast publishing/distribution and migration of old Rust workspace data unless separately requested.

## Acceptance scenarios

1. Initialize a new workspace, create a topic, and create an episode with a settings snapshot and artifact directory.
2. Restart the application and retrieve the same episode and current state.
3. Complete one episode through the external agent/MCP workflow and obtain playable audio; retrieve its saved materials for discussion with the agent.
4. Reject an invalid transition, missing required artifact, or stale update without advancing the episode.
5. Simulate a filesystem failure after episode creation; retain the record, detect the mismatch through audit, and recover through repair.
6. Upgrade a supported older database safely and reject an unsupported newer schema.
7. Correct a proposed episode plan, restart while awaiting approval, and approve the revised plan before production proceeds.
8. Edit a topic or application voice settings without rewriting existing episode snapshots or recorded synthesis settings.

## Decisions required

- Confirm reconstructed scope and provisional product name.
- Define topic-setting defaults and validation, script format, and application-level voice configuration.
- Choose source discovery/retrieval responsibilities and source-quality criteria.
- Choose initial TTS provider and credential/cost constraints.
- Confirm the initial agent client and how explicit user plan approval is delivered to the application.
- Specify topic settings, artifact contracts, retry/rewind behavior, and deletion semantics in focused increments.

## Python adaptation

Preserve domain behavior rather than translating Rust modules one-for-one. Start with a Python package, CLI, SQLite persistence, and an MCP adapter. Keep domain rules independent of transport and external providers.

Python version, package manager, typing checker, CLI/MCP libraries, persistence approach, and synchronous/asynchronous boundaries will be selected after PRD approval using current official documentation. Rust libraries and custom migration mechanisms are not automatically carried over.
