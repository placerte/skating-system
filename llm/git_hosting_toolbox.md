---
id: BLK-TOOLBOX-GIT-HOSTING-V1
name: Git Hosting Toolbox (Gitea / GitHub)
type: toolbox
scope: mixed
version: 1.3
status: active
revised: 2026-09-25
summary: Preferred issue, label, and release workflows for Gitea (tea) and GitHub (gh) repositories.
tags: [toolbox, git, gitea, github, releases, issues]
---
# Git Hosting Toolbox (Gitea / GitHub)

This toolbox defines the **preferred processes** for working against a hosted
git forge — issues, labels, and releases — for both **Gitea** (via the `tea`
CLI) and **GitHub** (via the `gh` CLI).

The goal is that agents handle the *whole* lifecycle without being told each
step: read issues, address them, comment progress, close them when resolved,
cut releases with install scripts, and keep the label set healthy.

It is intentionally explicit about the failure modes each CLI has, so a session
does not silently do nothing.

---

## Scope and forge detection

Applies whenever a repository has a remote on a hosted forge.

Detect the forge before acting:

- `git remote -v` → a `github.com` remote means GitHub (`gh`); anything else
  (self-hosted domain) is almost certainly **Gitea** (`tea`).
- Confirm the CLI is authenticated: `gh auth status`, or `tea whoami`.
- Many self-hosted Gitea repos are **public** — reads can go through the
  unauthenticated REST API even when the CLI is flaky (see Verification).

Unless a handoff says otherwise, this toolbox is the default process.

---

## Hard rules

1. **Outward-facing writes require intent.** Creating/closing issues, posting
   comments, and publishing releases are visible under the user's identity. Do
   them when the user asked for that specific action; if the request is indirect
   (e.g. "do what the notes say"), surface the concrete drafts and confirm
   before writing.
2. **Close what you resolved.** When a change fully addresses an issue, comment
   the resolution (with the commit/release reference) *and* close it in the same
   session. Do not leave resolved issues open for the user to clean up.
3. **Releases are explicit.** Never cut a release in a routine session unless
   the user asked. When asked, follow the full sequence (below) — build, verify,
   docs, commit, publish.
4. **Verify every write.** Both CLIs have success-looking failures; confirm the
   result via the REST API or a read-back before reporting done.

---

## Labels

### Bootstrap (when a repo has none)

If the repo has no labels, create a small, universal set. Do **not**
over-populate — start minimal and add labels only when a real issue needs one.

Baseline set (code projects):

| name       | color     | description                                          |
|------------|-----------|------------------------------------------------------|
| `bug`      | `#d73a4a` | Something is broken or produces incorrect results    |
| `feature`  | `#0e8a16` | New capability or enhancement                        |
| `refactor` | `#1d76db` | Code restructuring without behavior change           |

For **document / report / prose** projects, prefer domain-appropriate labels
instead of (or in addition to) the code set, e.g. `rewrite`, `restructure`,
`fact-check`, `typo`. Pick 3-4 that match how the project actually changes.

When a new *kind* of work appears that no label fits, propose one new label
rather than forcing it into an existing one — but propose, do not spam.

### Commands

Gitea:

```bash
tea labels create --name bug --color "#d73a4a" \
  --description "Something is broken or produces incorrect results" \
  --repo <owner>/<repo> < /dev/null
```

GitHub:

```bash
gh label create bug --color d73a4a \
  --description "Something is broken or produces incorrect results" \
  --repo <owner>/<repo>
```

Verify: `curl -s https://<host>/api/v1/repos/<owner>/<repo>/labels` (Gitea) or
`gh label list --repo <owner>/<repo>`.

---

## Issue lifecycle

The expected flow for each issue:

1. **Ingest** — read the issue body *and* its comments; do not act on the title
   alone. For a public Gitea repo, read via the API without needing auth:
   `curl -s https://<host>/api/v1/repos/<owner>/<repo>/issues/<n>` and
   `.../issues/<n>/comments`.
2. **Clarify** — if the issue is ambiguous or under-specified, ask focused
   questions before editing code.
3. **Address** — implement the fix/feature on a branch or main per the project
   workflow.
4. **Comment** — post what changed and where (commit hash, release tag). Keep it
   factual and short.
5. **Close** — close the issue once the change is merged/released. Reference the
   resolving commit or release.
6. **File new issues** — when you discover a distinct bug or a requested feature
   that is out of the current scope, file it with the right label instead of
   silently expanding scope. One issue per distinct concern; cross-reference
   related ones (`#12`).

## Goal, milestone, and parent-issue workflow

<!-- GitHub issue #22: define goal coverage with milestones and sub-issues. -->

Use milestones and parent issues together when several issues deliver one
coherent outcome. They serve different purposes:

- the **milestone** defines the goal, scope boundary, optional due date, and
  overall completion target;
- the **parent issue** defines the feature or workstream, its checkable
  definition of done, and the hierarchy of deliverables;
- **sub-issues** are independently actionable pieces of work; and
- **blocked-by relationships** encode the actual critical path rather than
  relying only on prose such as "Phase 2."

A milestone should describe an outcome, not merely name a topic. Its
description should state:

1. the user- or project-level result;
2. explicit completion criteria;
3. important scope exclusions or constraints; and
4. the parent issue that owns the detailed work breakdown.

The parent issue should map every completion criterion to one or more
sub-issues. Before starting and again before closing the milestone, perform a
coverage audit:

1. list each milestone criterion;
2. identify the issue or completed evidence that satisfies it;
3. file a new issue for every uncovered requirement, or explicitly remove the
   requirement from scope with rationale;
4. identify issues that do not contribute to any criterion and remove them
   from the milestone or mark them as optional; and
5. verify that blockers and sub-issue relationships match the intended order.

Issues may belong to both a milestone and a parent. An issue belongs to only
one milestone at a time, so use milestones for concrete targets rather than as
general-purpose topic tags. Use labels for work type and GitHub Projects when
cross-milestone roadmap fields such as priority, owner, or status are needed.

GitHub CLI has no top-level `gh milestone` command. Create and inspect
milestones through the API, then use ordinary issue commands to assign work:

```bash
gh api repos/{owner}/{repo}/milestones \
  -f title="Source ingestion v1" \
  -f description="Goal and completion criteria"

gh issue create --repo <owner>/<repo> \
  --milestone "Source ingestion v1" \
  --title "Goal: build the source-ingestion workflow" \
  --body-file parent.md

gh issue edit <parent> --repo <owner>/<repo> \
  --add-sub-issue <child1>,<child2>,<child3>

gh issue edit <child2> --repo <owner>/<repo> \
  --add-blocked-by <child1>

gh issue edit <child1> <child2> <child3> --repo <owner>/<repo> \
  --milestone "Source ingestion v1"
```

Read back the milestone, parent, sub-issues, and dependency relationships after
every structural write. Do not close the parent or milestone merely because all
listed issues are closed; repeat the coverage audit against the stated outcome.

<!-- GitHub issue placerte/trading#4: require source-to-issue references. -->

### Source cross-references

When an issue changes source code or document source (`.py`, `.typ`, etc.), add
a brief comment near the primary implementation that identifies the issue.
Use the forge name and issue number, for example:

```python
# GitHub issue #12: reject orders when market data is stale.
```

```typst
// GitHub issue #12: document the evolving project constraints.
```

The reference exists for traceability, not narration:

- place it at the smallest stable implementation boundary that represents the
  issue;
- use the full issue URL when a bare number could refer to more than one forge
  or repository;
- do not repeat it on every changed line;
- do not add it to generated files, vendored dependencies, or third-party
  source; and
- keep a tracker or documentation implementation link as well when the project
  uses one.

### Commands

Gitea (each write on its own shell line, each with `< /dev/null`):

```bash
tea issues create --repo <owner>/<repo> --labels bug \
  --title "<concise title>" --description "<markdown body>" < /dev/null

tea comment <n> "<markdown body>" --repo <owner>/<repo> < /dev/null

tea issues close <n> --repo <owner>/<repo> < /dev/null
```

GitHub:

```bash
gh issue create --repo <owner>/<repo> --label bug \
  --title "<concise title>" --body "<markdown body>"

gh issue comment <n> --repo <owner>/<repo> --body "<markdown body>"

gh issue close <n> --repo <owner>/<repo> --comment "<resolution note>"
```

### Writing a good issue

- **Title**: one line, states the symptom or the ask.
- **Bug body**: reproduction (exact command), observed vs expected, evidence
  (paths, counts, screenshots), and — when known — a root-cause pointer
  (`file.py:line`) and a suggested fix. A bug you diagnosed while filing is far
  more valuable with the diagnosis attached.
- **Feature body**: the user-facing behavior, the trigger/CLI surface, the
  none/one/many cases where relevant, and any dependency on other issues.
- Apply exactly one primary label (`bug`/`feature`/`refactor`); add secondary
  labels only if they carry real signal.

---

## Releases

Releasing is **only** on explicit user request. When asked, run the full
sequence and do not skip verification.

### Sequence (required)

1. **Bump version** in the project manifest (`pyproject.toml`, `package.json`,
   …). For Python + `uv`, re-lock **offline** to avoid flaky re-resolves:
   `uv lock --offline && uv sync --offline`.
2. **Update CHANGELOG** (Keep a Changelog + SemVer) and any README status/
   version line.
3. **Build** the artifact(s). For a distributable app, build the binary
   (e.g. `uv run --offline pyinstaller <spec> --noconfirm`).
4. **Verify** the artifact exists and reports the new version
   (`./dist/<bin> --version`).
5. **Review docs** — a released app must document at minimum install + usage.
6. **Commit and push** (branch per project policy; releases usually target the
   default branch).
7. **Publish** the release with assets, then **verify via the API**.

### Install scripts

When the deliverable is a user-installable app, ship an `install.sh` one-liner
alongside the binary so users need neither the language runtime nor a package
manager:

- `install.sh` resolves the platform asset from the "latest" release API and
  installs it to a PATH location.
- Provide a self-update path (`<tool> update`) that checks the latest release,
  compares versions, and self-replaces the binary.
- Attach both the platform binary and `install.sh` as release assets so the
  documented one-line installation flow works.

For a public release, document the familiar unauthenticated form:

```bash
curl -fsSL https://<host>/<owner>/<repo>/releases/latest/download/install.sh | sh
```

Private GitHub release assets require authentication. Do not put a token in a
documented `curl` command or URL. Reuse the authenticated GitHub CLI instead:

```bash
gh release download --repo <owner>/<repo> --pattern install.sh --output - | sh
```

This streams the `install.sh` asset from the latest accessible release to the
shell. State that `gh auth login` is a prerequisite, and test the documented
command against the published release rather than only testing a local script.

### Commands

Gitea:

```bash
tea release create --tag vX.Y.Z --target main --title vX.Y.Z \
  --note-file NOTES.md \
  --asset <tool>-linux-x86_64 --asset install.sh \
  --repo <owner>/<repo> < /dev/null
```

GitHub:

```bash
gh release create vX.Y.Z --title vX.Y.Z --notes-file NOTES.md \
  --repo <owner>/<repo> \
  <tool>-linux-x86_64 install.sh
```

Verify (Gitea, public): `curl -s https://<host>/api/v1/repos/<owner>/<repo>/releases/latest`
and confirm the tag and asset list. (GitHub: `gh release view vX.Y.Z`.)

---

## CLI gotchas

### `tea` (Gitea) — captured from real sessions

- **Write commands hang on stdin.** Always append `< /dev/null` (and consider a
  `timeout`) to any `tea` write (`issues create`, `comment`, `labels create`,
  `release create`, `issues close`).
- **One write per shell invocation.** Batching several `tea` writes in a single
  shell call can silently create nothing. Run each write as its own command and
  verify.
- **Exit code lies.** `tea release create` (and some others) can exit non-zero on
  success — and look successful on failure. **Never trust the exit code**;
  verify via the REST API.
- **Shell-var flag mangling.** Passing `--repo "$VAR"` style flags has been seen
  to mangle; pass flag values as literals.
- **Body quoting.** Use single quotes around markdown bodies so backticks are
  literal (double quotes trigger command substitution on backticks); avoid
  apostrophes inside single-quoted bodies.
- **Reads without auth.** Public repos: read/verify with unauthenticated
  `curl https://<host>/api/v1/repos/<owner>/<repo>/...` instead of fighting the
  CLI.

### `gh` (GitHub)

- Generally reliable; exit codes are trustworthy.
- Use `--body-file` / `--notes-file` for multi-line content to sidestep shell
  quoting entirely.
- `gh` respects `GH_TOKEN`/keyring auth; confirm with `gh auth status` in
  headless/cron contexts where interactive auth may be absent.

---

## Definition of done

An issue-driven session is complete when:

- Every issue you resolved is commented **and** closed with a reference.
- Every new bug/feature you surfaced is filed with the correct label.
- The label set covers the work (missing baseline labels were created).
- If a release was requested: built, verified, documented, published, and the
  release was confirmed via the API — not just the CLI exit code.
