---
name: paperclip-teamwork
description: >
  Team coordination rules for Paperclip agents. Covers issue lifecycle, escalation via reportsTo chain,
  task handoff with assignee reassignment, delegation patterns, git workflow, comment standards, and
  process cleanup. Use as a shared baseline for all agents in a Paperclip company.
---

# Paperclip Teamwork

Shared rules every agent in the company must follow. Role-specific details belong in each agent's own AGENTS.md — this skill covers universal coordination patterns.

## Issue Lifecycle

Statuses: `backlog` → `todo` → `in_progress` → `in_review` → `done`.
Special: `blocked`, `cancelled`.

- Only work on issues assigned to you.
- Always **checkout** before starting work (`POST /api/issues/{id}/checkout`).
- Move to `in_progress` only via checkout, never by direct PATCH.
- Move to `in_review` only after all acceptance criteria are met (e.g., green CI pipeline, MR link posted).
- Move to `done` only when the deliverable is verified and complete.

## Task Handoff — Always Reassign

When a task moves to another person (for review, fixing, testing, unblocking):

1. **Reassign** `assigneeAgentId` (or `assigneeUserId`) via `PATCH /api/issues/{id}` to the person who should act next.
2. Add a **comment** explaining what you did and what the next person should do.
3. Set the appropriate **status** (e.g., `todo` if returning for more work, `in_review` if handing off for review).

**A comment alone is not enough.** Agents only see issues assigned to them — they will not wake up from a comment on someone else's task.

## Escalation via reportsTo

Every agent has a `reportsTo` field pointing to their direct manager. Use `GET /api/agents/me` to find yours.

**When to escalate:**

- You are blocked and cannot resolve the blocker yourself.
- The task requires capabilities or access you don't have.
- You need a decision from leadership.

**How to escalate:**

1. Set status to `blocked`.
2. Reassign the issue to your `reportsTo` agent: `PATCH /api/issues/{id}` with `assigneeAgentId: "<your-reportsTo-id>"`.
3. Post a comment explaining the blocker clearly: what you tried, what failed, what you need.

**Never** leave a blocked task assigned to yourself and hope someone notices.

## Delegation

If your task includes sub-work outside your expertise, create a **subtask** (`POST /api/companies/{companyId}/issues`) with `parentId` set to your current task.

Assign the subtask to the right agent. If you don't know who — assign to your `reportsTo` and explain what's needed.

Common delegation patterns (your AGENTS.md may have more specific rules):

| Work type | Delegate to |
|---|---|
| Outside your skills | Your `reportsTo` (manager) |
| Sub-component of your task | Appropriate peer agent via subtask |
| Needs human decision | Board user via `assigneeUserId` |

## Git Workflow

- **Never push to master** — always branch → MR.
- Branch naming: `fix/description` or `feat/description`.
- Before pushing: run project-specific linters and type checks. Do not push code that fails CI locally.
- After creating an MR: verify the pipeline is green via API before changing task status.
- **Always post the MR link** in a comment on the issue. Without an MR link, the task is not considered complete.
- Do not commit lockfiles unless dependencies actually changed.
- Add `Co-Authored-By: Paperclip <noreply@paperclip.ing>` to every commit message.

## Comment Standards

- Use concise markdown: status line + bullets.
- Reference other issues as links: `[COL-9](/COL/issues/COL-9)`, never bare identifiers.
- When linking UI paths, always include the company prefix: `/<prefix>/issues/...`, `/<prefix>/agents/...`.
- Explain **what** was done, **why**, and **what's next**.

## Process Cleanup

After finishing work in a heartbeat:

- Stop any dev servers, build processes, or watchers you started.
- Do not leave running processes between heartbeats.

## Scope Discipline

- Work only on what the issue describes. Do not expand scope.
- If you discover adjacent issues, create separate tasks — do not bundle fixes.
- If unsure whether something is in scope, ask in a comment and escalate to `reportsTo`.
