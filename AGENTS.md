# AICP rule

This repository uses AICP — AI Context Protocol — as the semantic map for AI agents.

Before any repository action:

1. Look for `AICP.aicp` and `.aicp/`.
2. Read AICP before editing code.
3. Read architecture before acting.
4. Verify AICP against real repository files.
5. Use the repository as the source of truth when AICP is stale or wrong.

Repeat: always read AICP before acting. Always read architecture before acting.

## If AICP exists

Before changing files:

1. Identify the relevant records:

   * `@mod`
   * `@surface`
   * `@contract`
   * `@flow`
   * `@inv`
   * `@resolver`
   * `@task`
   * `@avoid`
2. Map the user request to the smallest relevant target.
3. Prefer the matching `@resolver`.
4. Open first only paths listed in `entry`, `go`, `evidence`, `source`, `touch`, or `test`.
5. Respect `@avoid` unless the task explicitly requires otherwise.
6. Preserve all related `@inv` rules.
7. Run the relevant commands from `@cmd`, `@resolver.verify`, or `@task.validate`.

Do not scan the whole repository first when AICP already gives a route.

## If AICP does not exist

Create a minimal `AICP.aicp` before code changes, unless the user explicitly forbids it.

Inspect only enough to build a small truthful map:

* root files: `README.md`, package/build files, lock files, Docker/compose files, Makefile/Taskfile/justfile, `.env.example`;
* docs: `docs/**`, ADRs, architecture files, OpenAPI/AsyncAPI, schemas;
* source entrypoints: `src/**`, `app/**`, `apps/**`, `services/**`, `packages/**`, `cmd/**`, `internal/**`, `lib/**`;
* tests: `test/**`, `tests/**`, `__tests__/**`, `*.spec.*`, `*.test.*`.

Keep the first manifest small. Do not invent architecture.

Minimum useful records:

```aicp
@aicp v=0.3.0 id=<project-id> kind=<project-kind> summary="<short factual summary>"
@stack lang=[<languages>] runtime=[<runtimes>] package=[<package-files>]
@cmd test "<test command>"
@agent read=[@aicp,@stack,@mod,@surface,@contract,@flow,@inv,@resolver,@task] verify=true update_on_arch_change=true mode=guided
@avoid paths=[node_modules/**,dist/**,build/**,.next/**,coverage/**,generated/**,vendor/**,target/**]
@mod <module-id> kind=core owns=[<owned-behaviors>] entry=[<real-path>] test=[<test-path>]
@inv no-secret-commit scope=global severity=critical rule="secrets must not be committed" evidence=[.env.example]
@resolver edit-<module-id> target=mod.<module-id> intent=edit go=[<module-path>,<test-path>] verify=["<test command>"]
```

## Editing policy

Use conservative changes:

* smallest safe change;
* existing patterns before new abstractions;
* no unrelated rewrites;
* no generated/vendor/dependency/build-output edits unless required;
* no secrets;
* no guessed modules, APIs, commands, paths, tests, or contracts;
* no weakening of invariants.

If AICP conflicts with real files, trust the files and report/update the stale AICP record.

## When to update AICP

Update `AICP.aicp` in the same change if you modify:

* architecture;
* module ownership;
* public or module-public surfaces;
* contracts;
* important flows;
* invariants;
* risks or policies;
* dependencies;
* validation commands;
* active tasks;
* external integrations.

A stale AICP is worse than no AICP.

## Final checklist

Before finishing, confirm:

```text
Read AICP?
Read architecture?
Mapped the request to the right target?
Followed the resolver if available?
Verified paths against real files?
Respected @avoid?
Preserved invariants?
Ran or listed validation commands?
Updated AICP if the semantic map changed?
```
