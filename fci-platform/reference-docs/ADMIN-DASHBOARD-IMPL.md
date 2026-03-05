# Admin Dashboard — Implementation Specification

**Date:** 5 March 2026
**Status:** Ready for implementation
**Depends on:** Nothing (can be built independently of rolling summarization)

---

## 1. Purpose

A dedicated admin page within the platform for:

1. **Token usage monitoring** — track and display API costs across conversations, cases, and users, enabling business-case cost projections ("X investigators * Y cases/day = $Z/month")
2. **Database management** — reseed, inspect collections, clean up stale data
3. **System health** — MongoDB status, knowledge base state, configuration overview
4. **Development utilities** — tools that accelerate dev/testing workflows

This is not a production admin panel with RBAC. Auth is deferred — for now, any logged-in user can access the admin page. A `TODO: restrict to admin role` marker will be placed on the backend endpoints and the frontend route for when proper auth is implemented.

---

## 2. Existing Infrastructure

### 2.1 What Already Exists

| Component | Location | What It Does |
|-----------|----------|-------------|
| Admin router | `server/routers/admin.py` | Single `POST /api/admin/reseed` endpoint — wipes DB, re-runs seed script |
| Health endpoint | `server/main.py:104` | `GET /api/health` — MongoDB ping, KB status |
| Token usage storage | `conversation_manager.py:409` | Each assistant message stores `token_usage: {input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}` |
| Seed script | `scripts/seed_demo_data.py` | Drops collections, inserts 2 users + 5 cases |
| Auth system | `server/routers/auth.py` | Mock auth — in-memory session tokens, no roles, no passwords |
| Frontend nav | `client/src/components/AppLayout.jsx` | Header with icon links to Ingest, Free Chat. No admin link yet. |

### 2.2 Key Database Collections

```
fci_platform.users          — 2 documents (seeded)
fci_platform.cases          — 5 documents (seeded)
fci_platform.conversations  — 0+ documents (created during use)
fci_platform.ingestion_cases — 0+ documents (future, from ingestion work)
```

---

## 3. Backend: Admin API Endpoints

Extend `server/routers/admin.py` with new endpoints. All prefixed under `/api/admin`.

### 3.1 Token Usage Stats

**`GET /api/admin/stats/tokens`**

Aggregates token usage across all conversations. Returns data structured for the dashboard.

Query parameters:
- `days` (int, default 30) — look-back window
- `user_id` (str, optional) — filter to specific user

Response:
```json
{
  "period": {
    "from": "2026-02-03T00:00:00Z",
    "to": "2026-03-05T23:59:59Z",
    "days": 30
  },
  "totals": {
    "input_tokens": 2450000,
    "output_tokens": 385000,
    "cache_creation_tokens": 520000,
    "cache_read_tokens": 1890000,
    "estimated_cost_usd": 42.50,
    "api_calls": 187
  },
  "by_conversation": [
    {
      "conversation_id": "conv_abc123",
      "case_id": "CASE-2026-0451",
      "mode": "case",
      "title": "",
      "user_id": "user_001",
      "message_count": 12,
      "api_calls": 8,
      "input_tokens": 520000,
      "output_tokens": 64000,
      "cache_read_tokens": 380000,
      "estimated_cost_usd": 8.75,
      "has_rolling_summary": false,
      "first_message_at": "2026-03-01T09:15:00Z",
      "last_message_at": "2026-03-01T10:45:00Z"
    }
  ],
  "averages": {
    "tokens_per_case_conversation": 584000,
    "tokens_per_free_chat": 45000,
    "cost_per_case_conversation": 9.20,
    "cost_per_free_chat": 0.85,
    "api_calls_per_conversation": 7.2
  },
  "projections": {
    "cost_per_investigator_per_day_10_cases": 92.00,
    "cost_per_investigator_per_month": 1840.00,
    "note": "Based on average cost per case conversation * 10 cases/day * 20 working days"
  }
}
```

**Implementation:**

```python
@router.get("/stats/tokens")
async def get_token_stats(
    days: int = 30,
    user_id: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    # TODO: restrict to admin role
    db = get_database()

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = {"updated_at": {"$gte": cutoff}}
    if user_id:
        query["user_id"] = user_id

    conversations = []
    async for conv in db.conversations.find(query):
        # Aggregate token usage from assistant messages
        conv_tokens = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0, "api_calls": 0}
        visible_count = 0
        first_msg_at = None
        last_msg_at = None

        for msg in conv.get("messages", []):
            if msg.get("visible"):
                visible_count += 1
            if msg.get("token_usage"):
                tu = msg["token_usage"]
                conv_tokens["input"] += tu.get("input_tokens", 0)
                conv_tokens["output"] += tu.get("output_tokens", 0)
                conv_tokens["cache_creation"] += tu.get("cache_creation_input_tokens", 0)
                conv_tokens["cache_read"] += tu.get("cache_read_input_tokens", 0)
                conv_tokens["api_calls"] += 1
            ts = msg.get("timestamp")
            if ts:
                if first_msg_at is None or ts < first_msg_at:
                    first_msg_at = ts
                if last_msg_at is None or ts > last_msg_at:
                    last_msg_at = ts

        conversations.append({
            "conversation_id": conv["_id"],
            "case_id": conv.get("case_id"),
            "mode": conv.get("mode", "case"),
            "title": conv.get("title", ""),
            "user_id": conv.get("user_id"),
            "message_count": visible_count,
            "api_calls": conv_tokens["api_calls"],
            "input_tokens": conv_tokens["input"],
            "output_tokens": conv_tokens["output"],
            "cache_read_tokens": conv_tokens["cache_read"],
            "estimated_cost_usd": _estimate_cost(conv_tokens),
            "has_rolling_summary": "rolling_summary" in conv,
            "first_message_at": first_msg_at.isoformat() if first_msg_at else None,
            "last_message_at": last_msg_at.isoformat() if last_msg_at else None,
        })

    # Compute totals and averages
    # ... (straightforward aggregation over the conversations list)
```

**Cost estimation helper:**

```python
# Pricing per 1M tokens (Sonnet 4.6 defaults, update for Opus/mixed)
MODEL_PRICING = {
    "input_per_1m": 3.00,
    "output_per_1m": 15.00,
    "cache_read_per_1m": 0.30,     # 90% discount on cached input
    "cache_creation_per_1m": 3.75,  # 25% premium on first cache write
}

def _estimate_cost(tokens: dict) -> float:
    """Estimate USD cost from token counts using current pricing."""
    cost = 0.0
    cost += (tokens["input"] / 1_000_000) * MODEL_PRICING["input_per_1m"]
    cost += (tokens["output"] / 1_000_000) * MODEL_PRICING["output_per_1m"]
    cost += (tokens["cache_read"] / 1_000_000) * MODEL_PRICING["cache_read_per_1m"]
    cost += (tokens["cache_creation"] / 1_000_000) * MODEL_PRICING["cache_creation_per_1m"]
    return round(cost, 2)
```

**Note:** The pricing constants should be in `config.py` so they can be updated without code changes when models or pricing change. For now, hardcode Sonnet 4.6 rates and add a `TODO` for making them configurable.

### 3.2 Database Overview

**`GET /api/admin/stats/database`**

Quick snapshot of collection sizes and document counts.

Response:
```json
{
  "collections": {
    "users": {"count": 2},
    "cases": {"count": 5, "by_status": {"open": 4, "in_progress": 1}},
    "conversations": {
      "count": 8,
      "by_mode": {"case": 5, "free_chat": 3},
      "total_messages": 142,
      "with_rolling_summary": 2
    }
  },
  "mongodb": {
    "status": "connected",
    "database": "fci_platform"
  }
}
```

**Implementation:** Simple `count_documents()` and aggregation pipeline calls. Lightweight.

### 3.3 Conversation Detail (Drill-Down)

**`GET /api/admin/conversations/{conversation_id}/debug`**

Returns full conversation metadata including token usage per message, rolling summary state, and message sizes. This is the drill-down from the token stats table.

Response:
```json
{
  "conversation_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "mode": "case",
  "user_id": "user_001",
  "status": "active",
  "rolling_summary": {
    "summarized_through_index": 8,
    "token_estimate": 2400,
    "model": "claude-opus-4-6",
    "created_at": "2026-03-05T10:30:00Z"
  },
  "messages": [
    {
      "index": 0,
      "message_id": "msg_abc",
      "role": "system_injected",
      "visible": false,
      "content_length": 12450,
      "estimated_tokens": 4150,
      "token_usage": null,
      "has_images": false,
      "timestamp": "2026-03-01T09:15:00Z"
    },
    {
      "index": 1,
      "message_id": "msg_def",
      "role": "assistant",
      "visible": true,
      "content_length": 8200,
      "estimated_tokens": 2733,
      "token_usage": {"input_tokens": 65000, "output_tokens": 2800, "cache_read_input_tokens": 48000},
      "has_images": false,
      "tools_used": [],
      "timestamp": "2026-03-01T09:15:30Z"
    },
    {
      "index": 4,
      "message_id": "msg_ghi",
      "role": "tool_exchange",
      "visible": false,
      "content_length": 24000,
      "estimated_tokens": 8000,
      "original_role": "user",
      "timestamp": "2026-03-01T09:20:00Z",
      "note": "Tool result: scam-fraud-sop (8000 tokens carried in every subsequent call)"
    }
  ],
  "total_content_tokens_estimate": 45000,
  "total_api_input_tokens": 520000,
  "total_api_output_tokens": 64000
}
```

This view is specifically designed to make the context bloat problem visible — you can see exactly which tool exchange messages are the largest and how they accumulate.

### 3.4 Reseed (Already Exists)

**`POST /api/admin/reseed`** — already implemented in `admin.py:25`. No changes needed.

### 3.5 Delete Conversation

**`DELETE /api/admin/conversations/{conversation_id}`**

Force-delete any conversation regardless of ownership. The existing `DELETE /api/conversations/{id}` requires the owner's token. Admin needs to clean up any conversation.

```python
@router.delete("/conversations/{conversation_id}")
async def admin_delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    # TODO: restrict to admin role
    db = get_database()
    result = await db.conversations.delete_one({"_id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Also clean up images directory
    images_dir = Path(settings.IMAGES_DIR) / conversation_id
    if images_dir.exists():
        shutil.rmtree(images_dir)

    return {"status": "deleted", "conversation_id": conversation_id}
```

### 3.6 Clear All Conversations

**`POST /api/admin/clear-conversations`**

Wipe all conversations without reseeding cases/users. Useful during development when you want fresh conversations but don't want to re-parse the demo case markdown.

```python
@router.post("/clear-conversations")
async def clear_conversations(
    current_user: dict = Depends(get_current_user),
):
    # TODO: restrict to admin role
    db = get_database()

    result = await db.conversations.delete_many({})

    # Reset conversation_id on all cases
    await db.cases.update_many(
        {},
        {"$set": {"conversation_id": None, "status": "open"}}
    )

    # Clear images directory
    images_dir = Path(settings.IMAGES_DIR)
    if images_dir.exists():
        shutil.rmtree(images_dir)
        images_dir.mkdir(parents=True, exist_ok=True)

    return {"status": "cleared", "conversations_deleted": result.deleted_count}
```

### 3.7 System Configuration (Read-Only)

**`GET /api/admin/config`**

Expose non-sensitive configuration for display on the admin page. Useful for verifying which model is configured, what the token budgets are, etc.

```python
@router.get("/config")
async def get_config(
    current_user: dict = Depends(get_current_user),
):
    # TODO: restrict to admin role
    return {
        "anthropic_model": settings.ANTHROPIC_MODEL,
        "anthropic_max_tokens": settings.ANTHROPIC_MAX_TOKENS,
        "max_tool_calls_per_turn": settings.MAX_TOOL_CALLS_PER_TURN,
        "knowledge_base_path": settings.KNOWLEDGE_BASE_PATH,
        "mongodb_db_name": settings.MONGODB_DB_NAME,
        "images_dir": settings.IMAGES_DIR,
        # Summarization settings (after rolling summarization is built)
        # "context_token_budget": settings.CONTEXT_TOKEN_BUDGET,
        # "recent_context_budget": settings.RECENT_CONTEXT_BUDGET,
        # "summarization_model": settings.SUMMARIZATION_MODEL,
    }
```

**Important:** Never expose `ANTHROPIC_API_KEY`, `MONGODB_URI`, or `ELLIPTIC_API_KEY`. Only expose operational settings.

---

## 4. Frontend: Admin Page

### 4.1 Route and Navigation

**`client/src/App.jsx`** — add route:
```jsx
<Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
```

**`client/src/components/AppLayout.jsx`** — add nav icon (gear/cog) alongside Ingest and Free Chat icons in the header (line 40 area). Same pattern as existing icon links.

### 4.2 Page Structure

**`client/src/pages/AdminPage.jsx`**

Single-page layout using `AppLayout`, with a tabbed or sectioned view. Follows the existing dark theme with `surface` and `gold` color scales.

```
+---------------------------------------------------------------+
| FCI Investigation Platform                    [icons] Admin    |
+---------------------------------------------------------------+
|                                                               |
|  Admin Dashboard                                              |
|                                                               |
|  +-- System Status Card --+  +-- Config Card ---------------+|
|  | MongoDB: Connected     |  | Model: claude-sonnet-4-6     ||
|  | KB: 10 core, 8 ref     |  | Max tokens: 4096            ||
|  | Users: 2  Cases: 5     |  | Tool calls/turn: 5          ||
|  | Conversations: 8       |  | Images dir: ./data/images    ||
|  +------------------------+  +-------------------------------+|
|                                                               |
|  +-- Token Usage Summary (30 days) --------------------------+|
|  |                                                           ||
|  |  Total Input: 2,450,000    Total Output: 385,000         ||
|  |  Cache Reads: 1,890,000    API Calls: 187                ||
|  |  Estimated Cost: $42.50                                   ||
|  |                                                           ||
|  |  Avg per case: $9.20 (6.3 API calls)                     ||
|  |  Avg per free chat: $0.85 (2.1 API calls)                ||
|  |                                                           ||
|  |  +----- Cost Projection Box ------+                       ||
|  |  | 10 cases/day, 1 investigator:  |                       ||
|  |  |   $92/day  |  $1,840/month     |                       ||
|  |  | 5 investigators:               |                       ||
|  |  |   $460/day |  $9,200/month     |                       ||
|  |  +--------------------------------+                       ||
|  +-----------------------------------------------------------+|
|                                                               |
|  +-- Conversation Token Table --------------------------------+|
|  |                                                           ||
|  | Conv ID    | Case      | Mode  | Msgs | Calls | Cost     ||
|  |------------|-----------|-------|------|-------|----------|
|  | conv_abc.. | CASE-0451 | case  | 12   | 8     | $8.75   ||
|  | conv_def.. | CASE-0387 | case  | 8    | 5     | $6.20   ||
|  | conv_ghi.. | —         | chat  | 15   | 6     | $1.20   ||
|  |                                                           ||
|  | [Click row to expand → shows per-message token breakdown] ||
|  +-----------------------------------------------------------+|
|                                                               |
|  +-- Database Actions ----------------------------------------+|
|  |                                                           ||
|  |  [Clear Conversations]  [Reseed Database]                 ||
|  |                                                           ||
|  |  Both require confirmation dialog.                        ||
|  +-----------------------------------------------------------+|
|                                                               |
+---------------------------------------------------------------+
```

### 4.3 Component Breakdown

```
client/src/pages/AdminPage.jsx            — Main page, fetches data, coordinates sections
client/src/components/admin/
  SystemStatusCard.jsx                     — MongoDB, KB, collection counts
  ConfigCard.jsx                           — Read-only config display
  TokenUsageSummary.jsx                    — Totals, averages, projections
  ConversationTokenTable.jsx               — Sortable table of conversations with token data
  ConversationDebugPanel.jsx               — Expandable detail for a single conversation
  DatabaseActions.jsx                      — Reseed, clear conversations (with confirm dialogs)
  CostProjectionBox.jsx                    — Configurable projection calculator
```

### 4.4 API Service

**`client/src/services/admin_api.js`** — new file:

```javascript
const API_BASE = '/api/admin';

export async function getTokenStats(token, days = 30) {
  const res = await fetch(`${API_BASE}/stats/tokens?days=${days}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch token stats');
  return res.json();
}

export async function getDatabaseStats(token) {
  const res = await fetch(`${API_BASE}/stats/database`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch database stats');
  return res.json();
}

export async function getConfig(token) {
  const res = await fetch(`${API_BASE}/config`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch config');
  return res.json();
}

export async function getConversationDebug(token, conversationId) {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}/debug`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Failed to fetch conversation debug');
  return res.json();
}

export async function reseedDatabase(token) {
  const res = await fetch(`${API_BASE}/reseed`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Reseed failed');
  return res.json();
}

export async function clearConversations(token) {
  const res = await fetch(`${API_BASE}/clear-conversations`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Clear failed');
  return res.json();
}

export async function adminDeleteConversation(token, conversationId) {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Delete failed');
  return res.json();
}
```

### 4.5 Cost Projection Calculator

The `CostProjectionBox` component lets you adjust two sliders:
- **Cases per day per investigator** (1-20, default 10)
- **Number of investigators** (1-10, default 1)

It multiplies: `avg_cost_per_case * cases_per_day * investigators * 20 working_days`

This gives you the number to take to your bosses: "At current usage patterns, 5 investigators doing 10 cases a day would cost $X per month."

If the average hasn't stabilized (< 5 case conversations in the period), show a warning: "Limited data — projections based on N conversations."

### 4.6 Conversation Debug Drill-Down

When you click a row in the conversation token table, it expands to show per-message token data from the `GET /admin/conversations/{id}/debug` endpoint:

```
▼ conv_abc123 — CASE-2026-0451 (case) — $8.75 total

  Msg  Role              Visible  Content Size  Est. Tokens  API Usage
  ──────────────────────────────────────────────────────────────────────
  0    system_injected   hidden   12,450 chars  4,150 tok    —
  1    assistant         shown     8,200 chars  2,733 tok    in: 65K out: 2.8K
  2    user              shown       42 chars      14 tok    —
  3    tool_exchange     hidden      600 chars     200 tok   — (tool_use request)
  4    tool_exchange     hidden   24,000 chars   8,000 tok   — (scam-fraud-sop.md)
  5    assistant         shown    11,500 chars   3,833 tok   in: 98K out: 3.5K
  ...

  Rolling Summary: None
  Total stored content: ~45K tokens
  Total API input billed: 520K tokens (content resent on every call)
```

This is the view that makes the context bloat problem tangible. You can point to message index 4 and say "this 8,000-token SOP was carried in every subsequent API call, costing us an extra 40K input tokens over 5 calls."

### 4.7 Styling

Follow existing design conventions:
- Dark mode: `bg-surface-900` page, `bg-surface-800` cards, `border-surface-700/50` borders
- Light mode: `bg-surface-50` page, `bg-white` cards, `border-surface-200` borders
- Gold accents for key numbers and active states
- `font-mono` for token counts, conversation IDs, costs
- Cards use `rounded-xl shadow-soft-sm` consistent with `CaseCard.jsx`
- Confirmation dialogs for destructive actions (reseed, clear) — simple modal with "Are you sure?" and a 3-second delay on the confirm button to prevent accidental clicks

---

## 5. Files Changed

### 5.1 Backend

| File | Change |
|------|--------|
| `server/routers/admin.py` | Add 5 new endpoints (stats/tokens, stats/database, config, conversation debug, clear-conversations). Expand from 55 lines to ~250 lines. |
| `server/main.py` | No change — admin router already registered (line 93) |
| `server/config.py` | Add `MODEL_PRICING` dict (or keep in admin.py for now) |

### 5.2 Frontend

| File | Change |
|------|--------|
| `client/src/App.jsx` | Add `/admin` route (1 line + import) |
| `client/src/components/AppLayout.jsx` | Add admin (gear) icon link in header nav |
| `client/src/pages/AdminPage.jsx` | **New file** — main admin page |
| `client/src/components/admin/*.jsx` | **New directory** — 7 components |
| `client/src/services/admin_api.js` | **New file** — admin API calls |

### 5.3 Files NOT Changed

| File | Why |
|------|-----|
| `server/services/conversation_manager.py` | Token data is already stored. Admin reads it, doesn't write it. |
| `server/services/ai_client.py` | No changes |
| `server/routers/conversations.py` | No changes |
| `server/models/schemas.py` | Admin endpoints return raw dicts, not Pydantic models. Internal tool, not public API. |
| `client/src/services/api.js` | Admin has its own API file |

---

## 6. Data Already Available vs. Gaps

### 6.1 Already Stored (No Backend Changes Needed)

Every assistant message in MongoDB already has:
```json
{
  "token_usage": {
    "input_tokens": 65000,
    "output_tokens": 2800,
    "cache_creation_input_tokens": 48000,
    "cache_read_input_tokens": 0
  }
}
```

This is stored by `store_streamed_response()` at `conversation_manager.py:409`. The admin endpoints simply aggregate these existing fields.

### 6.2 Not Yet Stored (Future Enhancement)

| Data | Why It's Missing | When to Add |
|------|-----------------|-------------|
| Model name per message | Currently a global setting, not recorded per-call. When dual models are introduced (summarization uses Opus, investigation uses Sonnet), each message should record which model was used. | When rolling summarization is built — add `model` field alongside `token_usage` on assistant messages. |
| Summarization call costs | Rolling summary Opus calls are a separate cost stream. Not tracked in conversation messages. | When rolling summarization is built — the `rolling_summary` object should include token usage from the summarization call. |
| Response latency | Time from API call start to completion. Useful for tracking the slowdown problem. | Low priority — add `latency_ms` to `token_usage` when convenient. |

### 6.3 Cost Estimation Accuracy

The cost estimate is approximate because:
1. **Mixed model pricing** — if Opus is used for some calls (free chat, future summarization) and Sonnet for others, the flat Sonnet pricing underestimates Opus calls. The admin page should note this.
2. **Prompt caching discount** — `cache_read_input_tokens` are billed at 10% of normal input price. The cost helper accounts for this.
3. **The stored `input_tokens` includes cached tokens** — the Anthropic API reports total input tokens (including cache hits). For cost purposes, we need to separate: `billed_input = input_tokens - cache_read_input_tokens`, then `cost = billed_input * normal_rate + cache_read * discounted_rate`. The cost helper handles this correctly.

---

## 7. Build Order

1. **Backend endpoints** — extend `admin.py` with all 5 new endpoints (~2 hours)
2. **Admin API service** — `admin_api.js` (~15 minutes)
3. **AdminPage + SystemStatusCard + ConfigCard** — basic page layout with health/config data (~1 hour)
4. **TokenUsageSummary + CostProjectionBox** — the key feature (~1.5 hours)
5. **ConversationTokenTable** — sortable table (~1 hour)
6. **ConversationDebugPanel** — expandable drill-down (~1 hour)
7. **DatabaseActions** — reseed/clear buttons with confirmation dialogs (~30 minutes)
8. **Route + nav link** — wire it up in App.jsx and AppLayout.jsx (~10 minutes)

Total estimated effort: ~7-8 hours.

---

## 8. Future Enhancements (Not In This Build)

- **Role-based access** — restrict admin page to users with `role: "admin"` once proper auth is built
- **Usage charts** — line chart of daily token usage over time (would need a charting library — recharts or similar)
- **Per-user breakdown** — when multiple investigators are using the platform, show token usage grouped by user
- **Export stats as CSV** — download the conversation token table as a spreadsheet for business reporting
- **Knowledge base management** — view/edit core and reference documents through the UI
- **Active sessions** — show currently logged-in users and their active conversations (from the in-memory session store)
- **Latency tracking** — show average response time and highlight conversations where latency degraded (the "it's getting very slow" problem, now measurable)
- **Alerts** — configurable threshold: "warn if a single conversation exceeds $X" or "warn if monthly spend exceeds $Y"
