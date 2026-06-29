---
name: client-data
description: DFW persistent state — client records, project phases, deliverable tracking, and proposal history via dbhub.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Database, SQLite, dbhub, CRM]
    related_skills: [dfw-web-design-now, project-tracker, proposal-gen]
---

# Client Data

Canonical read/write SOP for DFW client and project state. All Hermes phases that touch client state route through the `data-layer-node`.

## Pattern
A single SQLite database (`/root/.dfw/dfw-clients.db`) holds clients, projects, phases, deliverables, proposals, and communications. Every agent reads/writes through `dbhub_execute_sql`.

## Schema

```sql
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    niche TEXT,
    city TEXT,
    phone TEXT,
    email TEXT,
    website_url TEXT,
    gmaps_url TEXT,
    status TEXT DEFAULT 'lead',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    name TEXT,
    phase TEXT DEFAULT 'discovery',
    spec_path TEXT,
    build_path TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS proposals (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    project_id INTEGER,
    amount TEXT,
    status TEXT DEFAULT 'draft',
    sent_at TEXT,
    accepted_at TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    channel TEXT,
    direction TEXT,
    summary TEXT,
    occurred_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
```

## Protocol

1. **On new lead**: INSERT into `clients` with status='lead'.
2. **On project start**: INSERT into `projects`, phase='discovery'.
3. **On phase transition**: UPDATE `projects.phase` to one of: discovery, spec, build, qa, deliver, closed.
4. **On proposal send**: INSERT into `proposals`, status='sent'.
5. **On communication**: INSERT into `communications`.
6. **On task creation**: link `projects.task_uuid` to Taskwarrior UUID.

## Queries

```sql
-- Active projects by phase
SELECT id, name, phase, status FROM projects WHERE status = 'active' ORDER BY phase;

-- Proposals pending acceptance
SELECT p.id, c.name, p.amount FROM proposals p JOIN clients c ON p.client_id = c.id WHERE p.status = 'sent';
```

## Failure Modes
- Writing client state to flat files instead of the DB.
- Not updating phase on transitions, causing duplicate work.
- Storing PII unencrypted; keep DB on VPS only.
