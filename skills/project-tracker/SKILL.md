---
name: project-tracker
description: DFW phase-gate project tracking via Taskwarrior task templates.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Taskwarrior, Project, Tracking]
    related_skills: [dfw-web-design-now, client-data]
---

# Project Tracker

Auto-create and update Taskwarrior tasks for every DFW project phase transition.

## Pattern
DFW projects move through fixed phases: discovery → spec → build → qa → deliver. Each phase gets a Taskwarrior task with dependencies, due dates, and tags.

## Protocol

1. **On project creation**
   - Create parent task: `dfw:<client>:project` with tag `+dfw` and `+project`.
2. **On phase transition**
   - Mark previous phase task done.
   - Create new task for current phase with `depends:` on previous.
3. **Phase task templates**

| Phase | Task Description | Tags |
|---|---|---|
| discovery | `DFW <client>: discovery + competitor research` | `+dfw,+discovery` |
| spec | `DFW <client>: write spec build requirements` | `+dfw,+spec` |
| build | `DFW <client>: Awwwards spec build` | `+dfw,+build` |
| qa | `DFW <client>: QA + client preview` | `+dfw,+qa` |
| deliver | `DFW <client>: deliver + handoff` | `+dfw,+deliver` |

4. **Link to client-data**
   - Store the Taskwarrior UUID in `projects.task_uuid`.
5. **Daily sync**
   - Query pending DFW tasks with `task +dfw next`.
   - Surface blockers in status updates.

## Tools Used
- `mcp_server_taskwarrior_add_task`
- `mcp_server_taskwarrior_mark_task_done`
- `mcp_server_taskwarrior_get_next_tasks`
- `dbhub_execute_sql` to update project records.

## Failure Modes
- Creating duplicate tasks for the same phase.
- Not marking old phase tasks done, leading to stale views.
- Losing the link between Taskwarrior UUID and client-data project ID.
