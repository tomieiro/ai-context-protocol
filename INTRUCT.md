# AICP Adoption Guide

> How to adopt AICP in a real repository and guide an AI agent to generate `AICP.aicp` safely.

This document is not the full AICP specification. It is the practical adoption guide an AI coding agent should read before producing, updating, or validating an `AICP.aicp` manifest.

AICP means **AI Context Protocol**.
ACS means **AICP Compact Syntax**.

The goal of AICP is to give AI agents a compact, auditable, versioned map of a software project: architecture, modules, flows, contracts, invariants, risks, tasks, evidence, and validation commands.

The first useful output is usually a single file:

```text
AICP.aicp
```

For large repositories, the manifest may later be split into multiple files under `.aicp/`, but the first adoption step should stay boring and small.

---

## 1. What AICP is for

AICP exists to reduce blind repository reading.

Without AICP, an AI agent usually reads too much, guesses architecture from filenames, edits unrelated files, misses invariants, and runs the wrong tests.

With AICP, the agent gets a compact semantic map before touching the code.

A good `AICP.aicp` should help an agent answer:

- What kind of project is this?
- What stack does it use?
- Which modules exist?
- What does each module own?
- Where are the real entrypoints?
- Which contracts matter?
- Which user or system flows exist?
- Which invariants must not be broken?
- Which risks are known?
- Which commands validate changes?
- Which files should be avoided?
- Which current task is active?

AICP is not documentation for humans first. It is operational context for AI agents, CLIs, IDEs, CI, and future MCP tooling.

---

## 2. What AICP is not

Do not turn AICP into a second README.

AICP is not:

- a replacement for `README.md`;
- a replacement for `AGENTS.md`;
- a replacement for tests;
- a replacement for OpenAPI;
- a replacement for AsyncAPI;
- a replacement for ADRs;
- a replacement for SBOMs;
- a full symbol index;
- a full dependency graph;
- generated prose documentation;
- a place to copy large schemas;
- a place to store secrets.

AICP should reference existing artifacts instead of duplicating them.

Examples:

```text
source=ref:openapi:paths./api/products
source=path:docs/adr/0001-modular-monolith.md
license=ref:spdx:Apache-2.0
```

---

## 3. Stable adoption path

Start with one file.

```text
AICP.aicp
```

Do not begin with a complex MCP server, schema registry, package format, or multi-file architecture. Those are useful later, but the first test is whether a compact manifest improves AI navigation and change safety.

Recommended phases:

### Phase 1 — Seed manifest

Create a small `AICP.aicp` with:

- `@aicp`
- `@stack`
- `@cmd`
- `@agent`
- `@avoid`
- main `@mod` records
- critical `@inv` records
- one active `@task`, if there is current work

### Phase 2 — Guided manifest

Add:

- `@contract`
- `@flow`
- `@risk`
- `@policy`
- `@decision`
- `@external`

Only add records that can be grounded in real files, tests, docs, schemas, or commands.

### Phase 3 — Validation

Run AICP against real repository evidence.

Validate at least:

- required fields;
- duplicate IDs;
- owner references;
- path existence;
- glob validity;
- known risk vocabulary;
- critical invariants with evidence;
- HTTP contracts with method and path;
- generated artifacts with hashes, if present.

### Phase 4 — CI integration

Add validation to CI.

The first CI gate should be permissive or guided. Strict mode should come later, after the repository and team are comfortable maintaining the manifest.

### Phase 5 — MCP integration

Only after the manifest proves useful, expose it through MCP.

The MCP server should not be the source of truth. The repository file should remain the source of truth.

Good MCP resources and tools later:

```text
resource:aicp.project
resource:aicp.modules
resource:aicp.flows
resource:aicp.contracts
resource:aicp.invariants
resource:aicp.tasks

tool:aicp.validate
tool:aicp.query
tool:aicp.pack
tool:aicp.diff
tool:aicp.explain
```

---

## 4. Required behavior for the AI agent

When asked to generate `AICP.aicp`, the agent must inspect the repository before writing the manifest.

The agent must not invent architecture.

The agent may infer, but every important inference should be backed by evidence.

Required agent behavior:

1. Read repository root files first.
2. Identify package managers, runtimes, frameworks, build tools, and test commands.
3. Inspect existing documentation.
4. Inspect source tree shape.
5. Identify likely modules by ownership and boundaries, not only by folder names.
6. Identify contracts from routes, schemas, OpenAPI, AsyncAPI, GraphQL, queues, database models, CLIs, cron jobs, or external integrations.
7. Identify critical flows from actual entrypoints.
8. Identify invariants from tests, auth logic, validation logic, transaction boundaries, payment flows, permission checks, and business rules.
9. Record evidence paths for important claims.
10. Prefer a smaller accurate manifest over a large speculative manifest.
11. Mark uncertainty explicitly when needed.
12. Never include secrets.
13. Never copy large external specifications into AICP.
14. Use relative paths from repository root.
15. If a future file is intentional, prefix it with `future:`.
16. If an external artifact is intentional, prefix it with `external:` or use `uri:` / `ref:`.
17. Respect `@avoid` records.
18. Update AICP when architectural boundaries, contracts, invariants, risks, dependencies, or active tasks change.

---

## 5. Repository inspection order

The agent should inspect the repository in this order.

### 5.1 Root files

Look for:

```text
README.md
AGENTS.md
package.json
pnpm-lock.yaml
package-lock.json
yarn.lock
Cargo.toml
go.mod
pyproject.toml
requirements.txt
pom.xml
build.gradle
Dockerfile
docker-compose.yml
compose.yml
Makefile
Taskfile.yml
justfile
.env.example
```

From these files, infer:

- project kind;
- language;
- runtime;
- package manager;
- commands;
- infrastructure;
- test tooling;
- generated or vendor directories to avoid.

### 5.2 Documentation

Look for:

```text
docs/**
docs/adr/**
architecture/**
openapi.yaml
openapi.json
asyncapi.yaml
asyncapi.json
schema/**
```

Use these to ground:

- `@decision`
- `@contract`
- `@external`
- `@policy`
- `@risk`

### 5.3 Source tree

Look for real entrypoints:

```text
src/**
app/**
apps/**
services/**
packages/**
cmd/**
internal/**
lib/**
server/**
client/**
frontend/**
backend/**
```

Do not assume every folder is a module. A module is a stable ownership boundary.

### 5.4 Tests

Look for:

```text
test/**
tests/**
__tests__/**
spec/**
*.spec.*
*.test.*
```

Use tests as evidence for:

- invariants;
- module behavior;
- flows;
- contracts;
- risk mitigation.

### 5.5 Generated, vendor, and build output

Usually avoid:

```text
node_modules/**
dist/**
build/**
.next/**
out/**
coverage/**
generated/**
vendor/**
target/**
.pytest_cache/**
```

Represent these with `@avoid`.

---

## 6. Minimum useful `AICP.aicp`

A minimal manifest should look like this:

```text
@aicp v=0.2.0 id=my-project kind=webapp summary="short project summary"
@stack lang=[ts] runtime=[node] package=[package.json]

@cmd setup "pnpm install"
@cmd dev "pnpm dev"
@cmd test "pnpm test"
@cmd lint "pnpm lint"

@agent read=[@aicp,@stack,@mod,@inv,@task] verify=true update_on_arch_change=true mode=guided
@avoid paths=[node_modules/**,dist/**,.next/**,coverage/**]

@mod app kind=core owns=[main-flow] entry=[src] risk=[public-api] test=[tests]

@inv no-secret-commit scope=global severity=critical rule="secrets must not be committed" evidence=[.env.example]

@task initial-aicp owner=app status=active goal="create initial AICP manifest and validate usefulness" touch=[AICP.aicp] validate=["pnpm test","pnpm lint"]
```

Small and correct beats large and fictional.

---

## 7. Recommended records

### 7.1 `@aicp`

Defines the manifest identity.

```text
@aicp v=0.2.0 id=my-project kind=webapp summary="short project summary"
```

Required fields:

```text
v
id
kind
```

Use `summary` when possible.

---

### 7.2 `@stack`

Defines the technical stack.

```text
@stack lang=[ts,js] runtime=[node,postgres,redis,docker] infra=[docker-compose] package=[package.json] lock=[pnpm-lock.yaml]
```

Keep it factual. Use files as evidence where possible.

---

### 7.3 `@cmd`

Defines commands an agent or CI can run.

```text
@cmd setup "pnpm install"
@cmd dev "pnpm dev"
@cmd test "pnpm test"
@cmd lint "pnpm lint"
@cmd typecheck "pnpm typecheck"
@cmd build "pnpm build"
```

Only include commands that exist or are clearly defined by project files.

---

### 7.4 `@agent`

Defines how agents should read and maintain the manifest.

```text
@agent read=[@aicp,@stack,@mod,@inv,@task] verify=true update_on_arch_change=true max_context_ratio=0.05 mode=guided
```

Use `verify=true` by default.

The agent must validate AICP claims against real files before editing.

---

### 7.5 `@avoid`

Defines paths or modules that agents should avoid unless directly relevant.

```text
@avoid paths=[node_modules/**,dist/**,.next/**,coverage/**,generated/**,vendor/**]
```

This is one of the most useful early records because it prevents context waste.

---

### 7.6 `@mod`

Defines an architectural module.

```text
@mod auth kind=core owns=[login,sessions] entry=[src/auth] deps=[db.users] risk=[security,permission-leak] test=[tests/auth] evidence=[src/auth]
```

A module should have:

```text
kind
owns
entry
```

Good module boundaries are based on ownership, not folder aesthetics.

Avoid creating a module for every directory.

---

### 7.7 `@contract`

Defines a formal contract.

```text
@contract api.login type=http method=POST path="/login" auth=optional owner=auth returns=Session source=ref:openapi:paths./login
```

Use for:

- HTTP routes;
- GraphQL operations;
- gRPC services;
- events;
- queues;
- database tables or collections;
- files;
- object storage;
- external APIs;
- CLIs;
- cron jobs.

Do not duplicate OpenAPI or AsyncAPI. Reference them.

---

### 7.8 `@flow`

Defines an important behavior path.

```text
@flow user-login trigger="POST /login" path=[auth.validate_credentials,auth.create_session] fail={invalid_credentials:401} inv=[valid-user-required]
```

Use for user-visible or system-critical flows.

Avoid documenting every internal function call.

---

### 7.9 `@inv`

Defines an invariant: a rule that must not be broken.

```text
@inv valid-user-required scope=auth severity=critical rule="session requires valid user" evidence=[src/auth,tests/auth]
```

This is one of the most important AICP records.

Good invariants often come from:

- authentication;
- authorization;
- payment rules;
- transactional integrity;
- privacy boundaries;
- data retention;
- idempotency;
- state machines;
- external system trust boundaries.

Critical invariants should have evidence or enforcement.

---

### 7.10 `@task`

Defines active work.

```text
@task add-checkout owner=checkout status=active goal="add checkout flow" touch=[src/checkout,tests/checkout] avoid=[auth] validate=["pnpm test -- checkout","pnpm lint"] risk=[payment-failure]
```

Use `@task` to keep the agent focused.

AICP may have no active task, but if there is one, it should be explicit.

---

## 8. Evidence rules

AICP should be trusted only after verification.

Fields such as `entry`, `test`, `evidence`, `source`, `touch`, and `validate` are how the manifest stays grounded.

Use evidence like:

```text
evidence=[src/auth/service.ts,tests/auth/login.spec.ts]
source=path:docs/adr/0001-modular-monolith.md
source=ref:openapi:paths./api/products
validate=["pnpm test -- auth","pnpm lint"]
```

Bad AICP:

```text
@mod billing kind=core owns=[payments] entry=[src/billing]
```

If `src/billing` does not exist and there is no planned billing module, this is fiction.

Acceptable future AICP:

```text
@mod billing kind=core owns=[payments] entry=[future:src/billing] status=planned
```

---

## 9. Type style for the first version

For first adoption, prefer readable inferred syntax.

Good:

```text
@mod auth kind=core owns=[login,sessions] entry=[src/auth] risk=[security]
```

Use explicit types only when ambiguity matters.

Good when ambiguity exists:

```text
source=ref:openapi:paths./api/products
updated_at=datetime:2026-05-25T10:30:00-03:00
version=semver:1.2.3
entry=list[path]:[src/auth]
```

Do not make the first manifest noisy with full typing everywhere unless the goal is parser conformance testing.

---

## 10. Quality bar for generated AICP

A generated `AICP.aicp` is acceptable when:

- it has exactly one `@aicp` record;
- every major module has `kind`, `owns`, and `entry`;
- important claims point to real files or known refs;
- commands are grounded in package/build files;
- generated/vendor/build paths are avoided;
- critical invariants are explicit;
- contracts reference existing specs when available;
- active tasks are narrow and actionable;
- unknowns are not presented as facts;
- the file is short enough for an agent to read before editing.

A generated `AICP.aicp` is not acceptable when:

- it invents modules;
- it guesses APIs without inspecting routes or specs;
- it lists every folder as a module;
- it copies large schemas;
- it includes secrets;
- it has no evidence for critical rules;
- it turns into prose documentation;
- it ignores tests;
- it ignores existing ADRs or API specs;
- it cannot be maintained by humans.

---

## 11. Suggested AI prompt to generate `AICP.aicp`

Use this prompt when testing AICP generation:

```md
You are generating an AICP manifest for this repository.

Read this adoption guide first.

Create a single `AICP.aicp` file using ACS v0.2.

Rules:

1. Do not invent architecture.
2. Inspect root files, docs, source entrypoints, routes, tests, and build files.
3. Prefer a small accurate manifest over a large speculative one.
4. Use relative paths from the repository root.
5. Add `@avoid` for generated, vendor, dependency, cache, and build-output directories.
6. Add `@cmd` only for commands supported by project files.
7. Add `@mod` only for stable ownership boundaries.
8. Add `@contract` only when grounded in routes, schemas, specs, database models, queues, CLIs, cron jobs, or external integrations.
9. Add `@flow` only for important user-visible or system-critical behavior.
10. Add `@inv` for rules that must not break.
11. Add `evidence`, `source`, `test`, or `validate` wherever possible.
12. Mark planned or future paths explicitly with `future:`.
13. Never include secrets.
14. After generating the file, provide a short report listing assumptions, uncertain areas, and recommended validation commands.

Output only:

1. The proposed `AICP.aicp` content.
2. A short validation report.
```

---

## 12. Suggested `AGENTS.md` addition

Add this to `AGENTS.md` when adopting AICP:

```md
# AICP usage

Before changing this repository:

1. Read `AICP.aicp`.
2. Identify the relevant `@mod`, `@flow`, `@contract`, `@inv`, and `@task`.
3. Open only files listed in `entry`, `evidence`, `touch`, related contracts, or related tests unless more context is required.
4. Do not edit paths listed in `@avoid` unless explicitly necessary.
5. Validate AICP claims against real repository files before editing.
6. Run the relevant commands declared in `@cmd` before finalizing.
7. If the change affects architecture, contracts, module boundaries, invariants, dependencies, risks, or active tasks, update `AICP.aicp` in the same change.
```

---

## 13. Validation checklist

After generating `AICP.aicp`, review it with this checklist.

### Structure

- [ ] Exactly one `@aicp` exists.
- [ ] Project `id` is stable and lowercase.
- [ ] Project `kind` is reasonable.
- [ ] `@stack` matches real files.
- [ ] `@cmd` commands are real.
- [ ] `@avoid` covers dependency, build, generated, and cache directories.

### Modules

- [ ] Each `@mod` represents a real ownership boundary.
- [ ] Each `@mod` has `kind`, `owns`, and `entry`.
- [ ] Each `entry` path exists unless marked `future:`.
- [ ] Tests are linked where available.
- [ ] Risks are specific, not decorative.

### Contracts

- [ ] HTTP contracts have `method` and `path`, unless sourced from OpenAPI.
- [ ] Event contracts reference a channel, topic, or AsyncAPI source.
- [ ] Database contracts reflect real models, migrations, or schemas.
- [ ] External APIs are represented with `@external` or `@contract`.

### Flows

- [ ] Flows are important enough to guide an agent.
- [ ] Flows have clear triggers.
- [ ] Flow paths use module-level operations, not noisy low-level calls.
- [ ] Failure cases are included where known.
- [ ] Relevant invariants are attached.

### Invariants

- [ ] Critical business/security rules are represented.
- [ ] Critical invariants have evidence or enforcement.
- [ ] Invariants are written as rules, not vague aspirations.

### Maintenance

- [ ] The manifest is short enough to read at the start of a task.
- [ ] It avoids duplicating large specs.
- [ ] It can be updated by a developer in a normal PR.
- [ ] It improves navigation instead of becoming another stale document.

---

## 14. Experiment design

To validate whether AICP works, compare AI behavior with and without `AICP.aicp`.

Run the same repository tasks in two modes:

```text
Mode A: no AICP
Mode B: with AICP
```

Measure:

- number of files read;
- number of irrelevant files read;
- whether the correct files were edited;
- whether the correct tests were selected;
- whether critical invariants were preserved;
- whether generated diffs were smaller;
- whether the agent asked fewer unnecessary questions;
- whether the agent updated context after architectural changes;
- whether reviewers found fewer wrong assumptions.

Good early success criteria:

```text
- fewer irrelevant files read;
- better test selection;
- fewer edits outside task scope;
- explicit preservation of invariants;
- easier reviewer understanding of agent decisions.
```

Do not judge AICP only by token reduction. Token reduction is useful, but correctness and safer edits matter more.

---

## 15. MCP direction

The future MCP should expose AICP as structured repository context.

The repository file remains canonical:

```text
AICP.aicp
```

The MCP server may provide indexed views and tools.

Recommended resources:

```text
aicp://project
aicp://stack
aicp://commands
aicp://modules
aicp://flows
aicp://contracts
aicp://invariants
aicp://tasks
aicp://risks
aicp://policies
```

Recommended tools:

```text
aicp.validate
aicp.scan
aicp.query
aicp.explain
aicp.diff
aicp.pack
```

The MCP server should not make unsupported claims. It should parse, validate, query, and expose the manifest. Repository scanning can suggest records, but suggestions must be marked as suggestions until accepted into `AICP.aicp`.

Stable MCP behavior:

- read-only by default;
- explicit tool for proposed manifest updates;
- no silent rewriting of `AICP.aicp`;
- validation before write;
- diff output for human review;
- clear distinction between confirmed records and inferred suggestions.

---

## 16. Stable default

For the first real test, do this:

1. Put this guide in the repository as `docs/aicp-adoption.md` or `AICP_ADOPTION.md`.
2. Ask an AI agent to read it.
3. Ask the agent to inspect the repository.
4. Ask the agent to produce a small `AICP.aicp`.
5. Review every record for evidence.
6. Run one or two real coding tasks with and without AICP.
7. Compare navigation, edits, tests, and wrong assumptions.
8. Only then build the MCP layer.

AICP should earn its complexity by improving real agent behavior.
