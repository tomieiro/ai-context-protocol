# AICP / ACS — A Semantic Context Protocol for AI Agents in Software Projects

## Abstract

AI agents are already capable of reading source code, proposing changes, generating tests, and operating within real software repositories. The main issue is not access to files, but the absence of a reliable map of the system.

When there is no compact architectural context, the agent must infer most information from raw code and scattered documentation. This leads to reading excessive files, misunderstanding module boundaries, editing implementation details as if they were public contracts, ignoring invariants, skipping relevant tests, or modifying unrelated areas of the repository.

**AICP — AI Context Protocol** introduces a simple foundation for this problem: a textual, versionable, auditable, and verifiable manifest that describes the semantic context of a software project for AI agents.

**ACS — AICP Compact Syntax** is the compact, line-oriented syntax used to write that manifest.

The canonical human-readable file is:

```text
AICP.aicp
```

AICP is not intended to replace README files, source code, tests, OpenAPI, AsyncAPI, ADRs, SBOMs, static analysis, or symbol indexes. Instead, it sits above those artifacts as a **semantic context control layer**.

Its purpose is to help an AI agent understand what exists, what matters, what is safe to touch, what must be preserved, where supporting evidence lives, and how to move toward a change before modifying the system.

The core thesis is simple:

```text
AI agents should not begin by reading an entire repository.
They should begin by reading the project's semantic map,
verify that map against real evidence,
and only then open the files required for the task.
```

---

## The Problem

Most real repositories do not suffer from a lack of information. They suffer because important context is spread across too many places.

A typical production project contains:

- source code;
- tests;
- partial documentation;
- scripts;
- CI workflows;
- architectural decisions;
- API contracts;
- generated files;
- database schemas;
- dependency metadata;
- deployment conventions;
- implicit business rules;
- module ownership known mostly by the team.

When an AI agent receives a task such as “fix checkout”, “add pagination”, “change login”, or “adjust the product API”, it has to answer questions that are rarely available in one reliable place:

```text
Which module owns this behavior?
Which files are legitimate entry points?
Which internal functions are public surfaces?
Which external APIs exist?
Which invariants must not be broken?
Which tests validate this area?
Which paths should be avoided?
Which architectural decisions explain the current design?
Where should the agent go first if it wants to change this?
```

Without an explicit context layer, the agent is forced to reconstruct this information from source code and existing documentation. That approach can work in small projects, but it becomes fragile as the system grows.

The failure modes are familiar:

```text
The agent reads too much and loses focus.
The agent reads too little and misses a critical invariant.
The agent treats a private helper as a public interface.
The agent changes a module without understanding ownership.
The agent misses the tests that actually matter.
The agent touches generated or vendor files.
The agent follows a plausible path that is architecturally wrong.
```

AICP exists to reduce these navigation errors.

---

## What AICP Is

**AICP — AI Context Protocol** is a structured textual protocol for representing the operational, architectural, semantic, and navigational context of a software project.

It is designed to be:

- language-agnostic;
- model-agnostic;
- friendly to repositories and code review;
- compact enough for AI context windows;
- readable by humans;
- parseable by tools;
- auditable in Git;
- verifiable against real project evidence.

AICP describes a project as a set of semantic records.

Example:

```aicp
@aicp v=semver:0.3.0 id=store-platform kind=webapp summary="ecommerce platform with catalog checkout and admin"

@mod catalog kind=core owns=[products,categories,prices] entry=[services/api/src/catalog] risk=[data-loss,performance] test=[services/api/tests/catalog]

@contract api.catalog.list type=http method=GET path="/api/products" owner=catalog source=ref:openapi:paths./api/products

@inv only-active-products-visible scope=catalog severity=high rule="inactive products must not appear in public catalog" evidence=[services/api/src/catalog,services/api/tests/catalog/visibility.spec.ts]
```

This is not meant to be decorative documentation. It is meant to be a dense, reviewable, machine-friendly semantic map.

AICP answers a different question from normal documentation.

Documentation usually asks:

```text
How do humans understand this project?
```

AICP asks:

```text
How should an AI agent safely navigate, modify, and validate this project?
```

---

## What ACS Is

**ACS — AICP Compact Syntax** is the textual syntax used by AICP.

ACS is intentionally line-oriented:

```text
@type id field=value field=value field=value
```

Example:

```aicp
@mod auth kind=core owns=[login,sessions,jwt] entry=[src/auth] risk=[security,permission-leak] test=[tests/auth]
```

Each line is a semantic record. The directive at the beginning defines the record type:

```text
@aicp       manifest identity
@stack      technical stack
@cmd        operational command
@agent      agent behavior policy
@avoid      forbidden or discouraged paths
@mod        architectural module
@surface    callable code surface
@contract   formal contract
@flow       behavioral flow
@inv        invariant
@resolver   navigation route for safe action
@decision   architectural decision
@task       current work state
@risk       known risk
@dep        important dependency
@artifact   generated or consumed artifact
@metric     success or validation metric
@policy     operational or technical policy
@external   external system
@env        environment
@release    release or milestone
@note       short semantic note
```

ACS supports both inferred and explicit typing.

Short human form:

```aicp
@mod catalog kind=core entry=[services/api/src/catalog]
```

Explicit typed form:

```aicp
@mod catalog kind=enum:core entry=list[path]:[services/api/src/catalog]
```

The short form is easier to write and review. The explicit form is better for generators, validators, and canonical machine packages.

---

## Design Principles

### The repository remains the source of truth

AICP is a map, not the territory.

An agent must not blindly trust the manifest. Important records should be checked against real files, tests, contracts, and other evidence in the repository.

If AICP says that `catalog` lives under `services/api/src/catalog`, but that directory does not exist, the manifest is wrong or stale. The agent should report the mismatch instead of inventing a path.

This principle is central:

```text
AICP guides the agent.
Evidence confirms the guide.
The repository remains authoritative.
```

### AICP should not duplicate specialized standards

AICP should not reimplement mature artifacts that already exist.

It should not replace:

```text
OpenAPI       for HTTP contracts
AsyncAPI      for event contracts
ADR           for architectural decisions
SBOM formats  for dependency and supply-chain metadata
SCIP / LSIF   for complete symbol graphs
LSP           for language intelligence
Tests         for behavioral validation
```

Instead, AICP should point to these artifacts when they are relevant.

Example:

```aicp
@contract api.products.list type=http method=GET path="/api/products" owner=catalog source=ref:openapi:paths./api/products
@decision adr-0001 status=accepted summary="use modular monolith first" source=path:docs/adr/0001-modular-monolith.md
@surface catalog.find_by_slug owner=catalog kind=function symbol=ref:scip:symbol.catalog.findBySlug evidence=[services/api/src/catalog/service.ts]
```

This keeps AICP small and prevents it from becoming a weaker copy of other tools.

### AICP should be compact

AI context is expensive. Large repositories contain far more information than an agent should read for most tasks.

AICP should provide a high-signal first pass:

```text
What are the modules?
What are the public contracts?
What internal surfaces matter?
What flows exist?
What invariants are critical?
What is currently being changed?
Where should the agent go first?
What should it avoid?
How should it validate the change?
```

The goal is not to describe every line of code. The goal is to reduce the search space before the agent opens files.

### AICP should be verifiable

Records should point to evidence whenever the information matters.

Good:

```aicp
@inv admin-routes-require-auth scope=admin severity=critical rule="all admin routes require authenticated admin user" evidence=[apps/admin/src,services/api/src/admin-auth,services/api/tests/admin/auth.spec.ts]
```

Weak:

```aicp
@inv admin-routes-require-auth scope=admin rule="admin must be secure"
```

The first record tells the agent where to verify the invariant. The second is too vague to guide a safe change.

### AICP should be incremental

A project should not need a perfect manifest before getting value from the protocol.

A small project can start with:

```text
AICP.aicp
```

A larger project can later split the manifest into several files:

```text
.aicp/
  project.aicp
  modules.aicp
  flows.aicp
  contracts.aicp
  surfaces.aicp
  resolvers.aicp
  invariants.aicp
  risks.aicp
  tasks.aicp
  pack/
    context.jsonl
    context.json
```

The first useful version should be small, honest, and easy to review.

---

## The Mental Model

AICP separates the software project into a few practical layers.

```text
Project identity       -> @aicp
Technical stack        -> @stack
Operational commands   -> @cmd
Agent policy           -> @agent
Architecture           -> @mod
Callable surfaces      -> @surface
External contracts     -> @contract
Behavioral flows       -> @flow
Critical rules         -> @inv
Navigation routes      -> @resolver
Current work           -> @task
Risk and policy        -> @risk, @policy
Evidence and artifacts -> @artifact, source=, evidence=
```

For early adoption, the most important directives are:

```text
@aicp
@stack
@cmd
@agent
@avoid
@mod
@surface
@contract
@flow
@inv
@resolver
@task
```

A practical agent workflow looks like this:

```text
1. Read @aicp, @stack, @agent, @avoid.
2. Identify the relevant @mod, @surface, @contract, @flow, @inv, and @task.
3. Find a matching @resolver.
4. Open only the paths declared in entry, evidence, touch, source, or resolver go fields.
5. Verify the manifest against real repository evidence.
6. Make the smallest safe change.
7. Run the declared validation commands.
8. Update AICP if the architecture, contract, surface, invariant, risk, or task state changed.
```

---

## `@resolver`: The Safe Route for AI Action

The most practical addition in AICP v0.3 is `@resolver`.

A resolver does not describe the system itself. It describes how an AI agent should navigate the system when it needs to read, edit, debug, extend, verify, refactor, or migrate a specific target.

The rule is direct:

```text
If the agent wants to change this, go there first.
```

Example:

```aicp
@resolver edit-catalog target=mod.catalog intent=edit go=[services/api/src/catalog,services/api/tests/catalog] use=[search,symbols] verify=["pnpm test -- catalog","pnpm lint"] avoid=[services/api/src/checkout]
```

This tells the agent:

```text
If you need to edit the catalog module,
start in these paths,
use search or symbol lookup if needed,
run these validations,
and do not touch checkout.
```

This is different from `@mod`.

`@mod` says what the module is:

```aicp
@mod catalog kind=core owns=[products,categories,prices] entry=[services/api/src/catalog]
```

`@resolver` says how to act safely around it:

```aicp
@resolver edit-catalog target=mod.catalog intent=edit go=[services/api/src/catalog,services/api/tests/catalog] verify=["pnpm test -- catalog"]
```

### Main fields

```text
id       local resolver identifier
target   thing being resolved: module, surface, contract, flow, invariant, task, path, glob, or ref
intent   read, edit, debug, extend, verify, refactor, migrate
go       files, directories, refs, or symbols the agent should inspect first
use      auxiliary mechanisms such as search, symbols, lsp, scip, grep, tests, docs
verify   commands, tests, or checks to run after the change
avoid    paths, modules, contracts, or scopes the agent should not touch
note     short human guidance
```

Example for an API change:

```aicp
@resolver edit-product-detail-api target=api.catalog.detail intent=edit go=[services/api/src/catalog,docs/openapi.yaml,services/api/tests/catalog] use=[openapi,search,symbols] verify=["pnpm test -- catalog","aicp validate"] avoid=[services/api/src/checkout]
```

Example for a bug investigation:

```aicp
@resolver debug-checkout-payment target=flow.checkout-brl intent=debug go=[services/api/src/checkout,services/api/tests/checkout,docs/adr/0002-payment-gateway.md] use=[search,symbols,tests] verify=["pnpm test -- checkout"] avoid=[apps/admin]
```

Example for an invariant:

```aicp
@resolver verify-admin-auth target=inv.admin-routes-require-auth intent=verify go=[apps/admin/src,services/api/src/admin-auth,services/api/tests/admin] use=[search,tests] verify=["pnpm test -- admin"] note="Do not weaken admin authentication while editing admin routes."
```

`@resolver` is intentionally not an executable tool declaration. It is a navigational instruction.

That distinction matters. Tools can change. The semantic route should remain useful.

---

## `@surface`: Callable Internal Surfaces

AICP should represent public APIs, but many software systems also have internal public surfaces.

These include functions, classes, methods, services, repositories, hooks, components, and SDK-like entry points that other parts of the system depend on.

AICP should not list every function. That would turn the manifest into a poor symbol index.

Instead, AICP should list only the surfaces that matter architecturally.

Example:

```aicp
@surface catalog.find_by_slug owner=catalog kind=function visibility=module-public symbol=ref:scip:symbol.catalog.findBySlug input=ProductSlug returns=ProductDetail evidence=[services/api/src/catalog/service.ts] risk=[public-api]
```

This tells the agent that `catalog.findBySlug` is not just an implementation detail. It is a callable surface used across a boundary.

Good candidates for `@surface` include:

```text
service methods used by other modules
repository interfaces used outside one file
public SDK functions
framework hooks used by multiple features
shared components with stable props
authorization middleware
payment gateway adapters
queue handlers
CLI command handlers
```

Poor candidates for `@surface` include:

```text
private helpers
formatting utilities
small mappers
local parsing functions
one-file implementation details
generated functions
```

The rule is straightforward:

```text
If another module, application, integration, or agent depends on it as a stable boundary, declare it.
If it is a replaceable internal detail, do not declare it.
```

`@surface` pairs naturally with `@resolver`.

```aicp
@surface checkout.create_payment_intent owner=checkout kind=function visibility=module-public symbol=ref:scip:symbol.checkout.createPaymentIntent input=Cart returns=PaymentIntent risk=[payment-failure] evidence=[services/api/src/checkout/payment.ts]

@resolver edit-payment-intent target=surface.checkout.create_payment_intent intent=edit go=[services/api/src/checkout/payment.ts,services/api/tests/checkout/payment.spec.ts] use=[search,symbols] verify=["pnpm test -- checkout"] avoid=[apps/admin]
```

The surface says what exists. The resolver says how to change it safely.

---

## Contracts, Flows, and Invariants

### Contracts

`@contract` describes formal interfaces.

These include HTTP APIs, GraphQL operations, gRPC services, events, queues, database collections, CLI commands, SDKs, files, cron jobs, and external APIs.

Example:

```aicp
@contract api.checkout.create type=http method=POST path="/api/checkout" auth=optional owner=checkout returns=CheckoutSession source=ref:openapi:paths./api/checkout risk=[payment-failure]
```

A contract should usually point to a formal source, such as an OpenAPI file, AsyncAPI file, schema, or concrete implementation path.

### Flows

`@flow` describes behavior across modules and contracts.

Example:

```aicp
@flow checkout-brl trigger="POST /checkout currency=BRL" path=[checkout.validate_cart,checkout.create_payment_intent,checkout.redirect_gateway] fail={invalid_cart:400,gateway_down:503} inv=[no-order-without-payment-intent,supported-currency-required]
```

A flow helps the agent understand the chain of behavior before editing a single file.

### Invariants

`@inv` describes critical rules that must remain true.

Example:

```aicp
@inv no-order-without-payment-intent scope=checkout severity=critical rule="order cannot be confirmed without payment reference" evidence=[services/api/src/checkout,services/api/tests/checkout/payment.spec.ts]
```

Invariants are among the most important records in the file. They protect business rules, security constraints, data integrity, compliance boundaries, and operational assumptions.

A severe invariant without evidence is weak. A critical invariant should point to code, tests, policies, or contracts that verify it.

---

## Minimal Example

A small repository can start with a single `AICP.aicp` file:

```aicp
@aicp v=0.3.0 id=my-project kind=webapp summary="small web application"

@stack lang=[ts] runtime=[node,postgres,docker]

@cmd setup "pnpm install"
@cmd test "pnpm test"
@cmd lint "pnpm lint"

@agent read=[@aicp,@stack,@mod,@surface,@contract,@inv,@resolver,@task] verify=true update_on_arch_change=true mode=guided

@avoid paths=[node_modules/**,dist/**,.next/**,generated/**]

@mod auth kind=core owns=[login,sessions] entry=[src/auth] risk=[security] test=[tests/auth]
@mod api kind=core owns=[http-routes] entry=[src/api] deps=[auth] risk=[public-api] test=[tests/api]

@surface auth.create_session owner=auth kind=function visibility=module-public symbol=string:"auth.createSession" input=User returns=Session evidence=[src/auth/session.ts] risk=[security]

@contract api.login type=http method=POST path="/login" auth=optional owner=auth returns=Session

@flow user-login trigger="POST /login" path=[auth.validate_credentials,auth.create_session] fail={invalid_credentials:401} inv=[valid-user-required]

@inv valid-user-required scope=auth severity=high rule="session requires valid user" evidence=[src/auth,tests/auth]

@resolver edit-auth target=mod.auth intent=edit go=[src/auth,tests/auth] use=[search,symbols] verify=["pnpm test -- auth","pnpm lint"] avoid=[src/billing]
```

This is enough for a first experiment.

The agent now knows:

```text
what the project is;
which modules exist;
where auth lives;
which function is an internal public surface;
which HTTP contract exists;
which flow matters;
which invariant must hold;
where to go before editing auth;
which validation commands to run.
```

---

## How an Agent Should Use AICP

### 1. Read the manifest first

The agent should begin with `AICP.aicp`, not with arbitrary repository traversal.

It should read at least:

```text
@aicp
@stack
@agent
@avoid
@mod
@surface
@contract
@flow
@inv
@resolver
@task
```

### 2. Identify the target of the change

The agent should map the user request to a relevant module, surface, contract, flow, invariant, task, or resolver.

Example:

```text
"Change product listing pagination"
```

Likely targets:

```text
mod.catalog
contract.api.catalog.list
flow.browse-product
resolver.edit-catalog
```

### 3. Find a compatible resolver

If a `@resolver` exists for the target and intent, the agent should follow it.

Example:

```aicp
@resolver edit-catalog target=mod.catalog intent=edit go=[services/api/src/catalog,services/api/tests/catalog] verify=["pnpm test -- catalog"]
```

The resolver should limit the first files opened.

### 4. Verify evidence

Before trusting a record, the agent should confirm that declared paths, sources, tests, and symbols exist.

If evidence is missing, the agent should not invent it. It should either inspect the repository directly or report that the manifest is stale.

### 5. Edit the smallest safe scope

The agent should avoid broad rewrites unless the task explicitly requires them.

The stable default is:

```text
smallest vertical change;
limited files;
known owner;
known tests;
known invariant impact;
clear rollback path.
```

### 6. Validate

The agent should run, or at least recommend, the commands declared by `@cmd`, `@resolver.verify`, `@task.validate`, or relevant policies.

### 7. Update the manifest if needed

If the change affects architecture, contracts, surfaces, invariants, risks, dependencies, or active tasks, the agent should update `AICP.aicp` in the same change.

A stale context file is worse than no context file because it can lead the agent with confidence in the wrong direction.

---

## Validation Modes

AICP should support multiple validation modes.

### Permissive

Useful during early adoption.

Behavior:

```text
allow unresolved references;
allow future paths;
warn on unknown enums;
allow short versions such as 0.3;
focus on syntax and basic structure.
```

### Guided

Useful for active development.

Behavior:

```text
error on missing local paths;
warn on unresolved external refs;
warn on unknown enums;
require primary modules and invariants;
validate owners;
validate resolver targets where possible.
```

### Strict

Useful for CI and mature repositories.

Behavior:

```text
error on unresolved references;
error on missing paths;
error on unknown enums;
error on duplicate set values;
require evidence for critical invariants;
require canonical semantic versions;
require resolver targets to exist;
require artifact hashes to match real files.
```

---

## Success Metrics

AICP should be measured by operational outcomes, not by how complete the manifest appears.

Useful metrics include:

```text
tokens saved before first useful edit;
percentage of irrelevant files avoided;
accuracy of module selection;
accuracy of test selection;
number of stale context records detected;
number of architecture-impacting changes that updated AICP;
reduction in agent edits outside the requested scope;
reduction in regressions caused by missed invariants;
time to identify the correct owner of a change;
time to locate the correct validation command.
```

The protocol succeeds if it helps agents make smaller, safer, better-targeted changes.

AICP should not be judged by whether it perfectly describes the entire repository. It should be judged by whether it improves navigation, verification, and change safety.

---

## Recommended Adoption Path

### Step 1 — Create a minimal `AICP.aicp`

Start with:

```text
@aicp
@stack
@cmd
@agent
@avoid
@mod
@inv
@resolver
```

Do not model everything.

Model the areas where agent mistakes would be expensive.

### Step 2 — Test with an AI agent

Ask an agent to generate or update the manifest from the repository.

Then check:

```text
Did it invent modules?
Did it invent paths?
Did it confuse internal helpers with public surfaces?
Did it identify the right tests?
Did it preserve important invariants?
Did it use resolver routes correctly?
```

The first goal is not perfection. The first goal is to see whether the protocol improves agent behavior.

### Step 3 — Use it on small real tasks

Choose safe tasks:

```text
add a field;
change a simple endpoint;
adjust a UI flow;
add a test;
rename a module-local concept;
update a documented contract.
```

Observe whether AICP reduces unnecessary file reads and unrelated edits.

### Step 4 — Add contracts and surfaces

Once the basic module map works, add:

```text
@contract for formal APIs;
@surface for internal public boundaries;
@flow for important behavior chains;
@resolver for safe edit/debug/verify routes.
```

This is where the protocol starts to become genuinely useful.

### Step 5 — Validate in CI

Eventually, run validation as part of CI:

```text
aicp validate --mode guided
```

Later:

```text
aicp validate --mode strict
```

The key policy is:

```text
If a change affects architecture, contracts, surfaces, invariants, risks, or active tasks, update AICP.
```

---

## What AICP Should Not Become

AICP should not become:

```text
a second README;
a replacement for tests;
a replacement for OpenAPI;
a replacement for ADRs;
a replacement for static analysis;
a full symbol index;
a generated dump of every function;
a build system;
a programming language;
a tool execution framework;
a large prose document that no one reviews;
a stale architecture diagram in text form.
```

The most dangerous failure mode is over-modeling.

If AICP tries to describe everything, it will become noisy, stale, and ignored.

The stable rule is:

```text
Describe what helps an AI agent navigate, change, and validate safely.
Reference everything else.
```

---

## Larger Example

```aicp
@aicp v=semver:0.3.0 id=realtextil-ecommerce kind=webapp summary="ecommerce replacing institutional portfolio" updated_at=datetime:2026-05-25T10:30:00-03:00

@stack lang=[ts,js] runtime=[node,postgres,redis,docker] infra=[docker-compose,nginx] package=[package.json] lock=[pnpm-lock.yaml]

@cmd setup "pnpm install"
@cmd dev "docker compose up"
@cmd test "pnpm test"
@cmd lint "pnpm lint"
@cmd typecheck "pnpm typecheck"
@cmd validate "aicp validate --mode guided"

@agent read=[@aicp,@stack,@mod,@surface,@contract,@flow,@inv,@resolver,@task] verify=true update_on_arch_change=true max_context_ratio=0.05 mode=guided

@avoid paths=[generated/**,vendor/**,node_modules/**,.next/**,dist/**]

@mod storefront kind=ui owns=[home,catalog,product-page,portfolio-content] entry=[apps/web/src/storefront] deps=[api.catalog.list,api.checkout.create] risk=[public-api,performance] test=[apps/web/tests/storefront]

@mod catalog kind=core owns=[products,categories,prices,stock] entry=[services/api/src/catalog] deps=[db.products,db.categories] risk=[data-loss,performance] test=[services/api/tests/catalog]

@mod checkout kind=core owns=[cart,payment-intent,order-confirmation] entry=[services/api/src/checkout] deps=[db.orders,external.payment-gateway] risk=[security,compliance,data-loss,payment-failure] test=[services/api/tests/checkout]

@surface catalog.find_by_slug owner=catalog kind=function visibility=module-public symbol=string:"catalog.findBySlug" input=ProductSlug returns=ProductDetail evidence=[services/api/src/catalog/service.ts] risk=[public-api]

@surface checkout.create_payment_intent owner=checkout kind=function visibility=module-public symbol=string:"checkout.createPaymentIntent" input=Cart returns=PaymentIntent evidence=[services/api/src/checkout/payment.ts] risk=[payment-failure]

@contract api.catalog.list type=http method=GET path="/api/products" auth=optional owner=catalog returns=ProductSummary[] source=ref:openapi:paths./api/products

@contract api.checkout.create type=http method=POST path="/api/checkout" auth=optional owner=checkout returns=CheckoutSession source=ref:openapi:paths./api/checkout

@flow checkout-brl trigger="POST /checkout currency=BRL" path=[checkout.validate_cart,checkout.create_payment_intent,checkout.redirect_gateway] fail={invalid_cart:400,gateway_down:503} inv=[no-order-without-payment-intent,supported-currency-required]

@inv no-order-without-payment-intent scope=checkout severity=critical rule="order cannot be confirmed without payment reference" evidence=[services/api/src/checkout,services/api/tests/checkout/payment.spec.ts]

@inv supported-currency-required scope=checkout severity=high rule="checkout currency must be BRL or USD" evidence=[services/api/src/checkout/currency.ts]

@resolver edit-catalog target=mod.catalog intent=edit go=[services/api/src/catalog,services/api/tests/catalog,docs/openapi.yaml] use=[search,symbols,openapi] verify=["pnpm test -- catalog","pnpm lint","aicp validate --mode guided"] avoid=[services/api/src/checkout]

@resolver edit-payment-intent target=surface.checkout.create_payment_intent intent=edit go=[services/api/src/checkout/payment.ts,services/api/tests/checkout/payment.spec.ts] use=[search,symbols,tests] verify=["pnpm test -- checkout"] avoid=[apps/admin]

@resolver debug-checkout target=flow.checkout-brl intent=debug go=[services/api/src/checkout,services/api/tests/checkout,docs/adr/0002-payment-gateway.md] use=[search,symbols,tests] verify=["pnpm test -- checkout"]

@risk payment-failure level=high scope=[checkout] mitigation="treat gateway status as source of truth" evidence=[services/api/src/checkout]

@task ecommerce-v1 owner=storefront status=active goal="replace portfolio with ecommerce catalog checkout and whatsapp redirection" touch=[apps/web,services/api,docs/adr] avoid=[legacy/**] validate=["pnpm test","pnpm lint","docker compose up"] due=date:2026-06-30 risk=[payment-failure,stale-context]
```

This example is intentionally compact. It does not describe every file, function, or test. It describes what an agent needs first.

---

## Conclusion

AICP is a protocol for making AI-assisted software work safer, smaller, and easier to verify.

It starts from a conservative engineering assumption:

```text
An AI agent should not be trusted because it is fluent.
It should be constrained, guided, and verified.
```

The repository remains the source of truth. Tests remain the validation mechanism. Existing standards remain responsible for their own domains. AICP adds the missing semantic map between human architecture and agent action.

The most important records are not the most complex ones. They are the records that prevent wrong navigation:

```text
@mod       where ownership lives
@surface   what internal code is safe to call as a boundary
@contract  what formal interfaces exist
@flow      how behavior crosses boundaries
@inv       what must not be broken
@resolver  where the agent should go when it wants to act
```

The first useful version of AICP does not need to be complete. It only needs to be honest, compact, and verifiable.

A good `AICP.aicp` should let an agent answer one question before it edits anything:

```text
If I need to change this part of the system, where should I go, what must I preserve, and how will I know I did not break it?
```

That is the protocol's purpose.
