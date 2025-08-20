# 🔄 Notion ↔ Supabase Two-Way Sync

This project demonstrates two parallel implementations of a **two-way synchronization system** between a **Notion database** and a **Supabase Postgres table**:

- **Track A: n8n workflows** (low-code, hosted on n8n)
- **Track B: Python FastAPI service** (code-based microservice)

Both methods follow the **same schema, mapping rules, and conflict resolution logic** so they can be benchmarked side-by-side.

---

## 🚀 Features

- Two-way sync between Notion & Supabase
- Conflict resolution via **last-write-wins** (timestamp-based)
- Mapping table to correlate rows ↔ pages
- Watermark to avoid reprocessing Notion edits
- Idempotent upserts (`on_conflict=id`)
- Error handling with retries & logging
- Rate limiting to respect Notion API quotas

---

## 📂 Repository Layout

```

notion-supabase-sync/
├─ sync-core/                 # shared spec, schema, fixtures
├─ n8n/                       # workflows (JSON exports, docs)
├─ python-service/            # FastAPI microservice implementation
├─ ops/                       # scripts, perf testing
└─ docs/                      # comparison results & notes

````

---

## 🛠️ Prerequisites

- **Supabase project** with REST enabled
- **Notion** account + integration + database
- **n8n** (self-hosted or cloud)  
- **Python 3.10+** (for Track B)

---

## 🗄️ Database Schema (Supabase)

Run this migration in Supabase SQL editor or CLI:

```sql
-- Primary data table
create table public.items (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  status text check (status in ('New','In Progress','Done')) default 'New',
  updated_at timestamptz not null default now()
);

-- Mapping table
create table public.notion_sync_map (
  supabase_id uuid primary key references public.items(id) on delete cascade,
  notion_page_id text unique not null,
  last_synced_at timestamptz not null default now()
);

-- Sync state (e.g., for Notion watermark)
create table public.sync_state (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

create index on public.items(updated_at desc);
````

---

## 📝 Notion Setup

1. Create a **Notion database** with properties:

   * `Name` (title)
   * `Status` (select: `New`, `In Progress`, `Done`)
   * `SupabaseID` (rich\_text)
2. Create a **Notion integration** at [Notion integrations](https://www.notion.so/my-integrations).
3. Share your database with the integration and copy the **database ID** + **integration token**.

> To compare fairly, create two databases:
>
> * `DB_A` → used by **n8n workflows**
> * `DB_B` → used by **Python service**

---

## 🔑 Environment

Copy `.env.example` → `.env` and fill in:

```env
NOTION_TOKEN=***
NOTION_DATABASE_ID_N8N=***
NOTION_DATABASE_ID_PY=***
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=***
WEBHOOK_SECRET=some-random-string
```

---

## ⚙️ Track A — n8n Implementation

### Workflow A — Supabase → Notion (Push)

* **Trigger:** Supabase Edge Function/Trigger posts JSON payload to an n8n Webhook:

  ```json
  {
    "type": "INSERT|UPDATE|DELETE",
    "record": {
      "id": "uuid",
      "title": "Example",
      "status": "New",
      "updated_at": "2025-08-20T08:55:00Z"
    }
  }
  ```
* **Logic:**

  * If `DELETE` → archive Notion page
  * Else:

    * If mapping exists → check timestamps → update page if Supabase newer
    * Else create new page + insert mapping
  * Update `last_synced_at`

### Workflow B — Notion → Supabase (Poll)

* **Trigger:** Cron node every 3 minutes
* **Logic:**

  * Read last watermark from `sync_state`
  * Query Notion pages updated since watermark
  * For each page:

    * Resolve `supabase_id` via `SupabaseID` property or mapping
    * If Supabase row is newer → skip
    * Else upsert row into `items` and update mapping
  * Advance watermark

> Import JSON workflow exports from `n8n/workflows/` directly into n8n.

---

## ⚙️ Track B — Python Implementation

### Install

```bash
cd python-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

### Endpoints

* `POST /supabase-change/{secret}`
  Handles Supabase change events (push direction).
* `POST /sync/notion-poll`
  Polls Notion for updates and syncs into Supabase.

### Key Files

* `app/sb.py` → Supabase REST helpers
* `app/notion.py` → Notion API wrappers
* `app/mapping.py` → conflict logic & field mapping
* `app/tests/` → pytest tests for end-to-end sync

---

## ⚖️ Conflict Resolution

* Compare timestamps:

  * Supabase: `items.updated_at`
  * Notion: `page.last_edited_time`
* Whichever is **newer wins**.
* Skipped updates are logged for traceability.

---

## 📊 Comparison Plan

1. **Seed data**: insert 50 rows into Supabase.
2. **Observe**: both implementations create pages in their respective Notion DBs.
3. **Run edits**:

   * Edit 20 Supabase rows → measure propagation time.
   * Edit 20 Notion pages → measure propagation time.
4. **Conflict test**: edit both sides simultaneously → newer survives.
5. **Failure test**: simulate Notion API downtime → ensure retries/recovery.
6. Record results in `docs/compare.md`.

Metrics to compare:

* Latency (p50/p95)
* Throughput (rows/min)
* Error rate
* Ease of debugging / extending

---

## 🔒 Security

* Keep Supabase **Service Role Key** in n8n credentials or `.env` (never expose client-side).
* Use random secrets for n8n Webhooks (`/supabase-change/<uuid>`).
* Apply Row-Level Security (RLS) in Supabase for production.

---

## ✅ Acceptance Tests

* [ ] Create Supabase row → Notion page created
* [ ] Update Supabase row → Notion page updated
* [ ] Delete Supabase row → Notion page archived
* [ ] Edit Notion page → Supabase row updated
* [ ] Conflict resolution works (newer wins)
* [ ] Pagination & batching work (>100 pages)
* [ ] Rate limits respected (no 429 errors)
* [ ] Errors logged & retried
* [ ] Idempotent (no duplicates when reprocessed)

---

## 📌 Roadmap

* Field-level merge policies
* Attachment/file sync
* Notion webhook support (when available)
* Performance testing with `k6`

---

## 📝 License

MIT

