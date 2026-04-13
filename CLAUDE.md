## Git Workflow

After every change (feature, fix, refactor, docs update), **commit and push to `main`** immediately. Do not batch changes or wait to be asked.

**Session-scoped commits:** Multiple Claude sessions may be working on different parts of the project concurrently. Only `git add` files that **this session** created or modified — never use `git add -A`, `git add .`, or stage files you didn't touch. If a file you need to commit has been modified by another session (unexpected diff), flag it to the user before staging. This prevents one session's commit from accidentally including another session's in-progress work.

---

## Code Principles

### Top-level imports

All imports must be at the top of the file, never inline inside functions or methods. Inline imports hide dependencies, make it unclear what a module requires, and make errors surface at runtime instead of import time. The only exception is guarding an optional dependency that may not be installed — and even then, prefer failing fast at import.

### Separation of concerns

Shared types, constants, and contracts must live in their own module — never inside a specific implementation file. If multiple implementations need the same interface (e.g. `QAResponse`, `Citation`, `SYSTEM_PROMPT`), extract it so each implementation depends on the shared contract, not on each other. A false dependency between siblings (e.g. `generate_claude` importing from `generate_openai`) makes the code fragile — changing one breaks the other for no good reason.

---

## Documentation Principles

You are extremely disciplined about keeping documentation in perfect sync with the code. For **every single task, feature, refactor, or plan** you create or suggest:

1. **Discovery Phase** (always do this first)
   - Explore and read all existing documentation:
     - README.md
     - docs/ folder (and any \*.md files)
     - Relevant inline docstrings / comments
     - This CLAUDE.md file itself
   - Identify what is relevant, outdated, or missing for the proposed changes.

2. **Planning Requirement**
   - Every plan you propose MUST contain a dedicated section called "**Documentation Updates**".
   - In that section explicitly list:
     - Which existing documents are impacted
     - What will be updated or newly created
     - Specific changes (e.g. "Add new endpoint X to API reference in docs/api.md", "Update architecture overview in README.md with new diagram description", "Create new migration guide for breaking change Y")

3. **Execution**
   - After code changes are complete, immediately update/create all affected documentation.
   - Documentation changes must be part of the same changeset when possible.
   - Never mark a task as "done" or propose final code until docs are current and consistent.

Stale or missing documentation is not acceptable. Treat docs as production code.

Development setup, API reference, and operational commands are in `README.md` — not here.
