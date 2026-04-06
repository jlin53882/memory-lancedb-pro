# PR: Fix malformed Discord synthetic channel route pollution

## Problem

### Summary
When OpenClaw generates an internal/synthetic session context for Discord (e.g., during subagent completion direct announce), it can mistakenly use the **sender's user ID** as the **channel ID**, creating a poisoned session entry and delivery route.

This causes:
1. A malformed session key like `agent:main:discord:channel:<userId>` to be persisted in `sessions.json`
2. Subsequent delivery attempts (e.g., subagent announce) to target `channel:<userId>` on Discord
3. Discord returns `Unknown Channel` because the user ID is not a valid channel
4. The delivery queue retries indefinitely since `Unknown Channel` was not classified as a permanent error

### Reproduction scenario
1. A subagent completes and tries to announce results back to the requester session
2. The requester session's `deliveryContext` lacks a concrete `to` field
3. The system falls back to deriving the delivery target from the session key
4. The session key was built from a synthetic context where `From = discord:channel:<senderId>` instead of `discord:channel:<channelId>`
5. `extractGroupId()` faithfully extracts the sender ID as the group/channel ID
6. The session is persisted with `groupId = <senderId>`, `origin.to = channel:<senderId>`
7. Delivery queue targets `channel:<senderId>` → Discord returns `Unknown Channel`
8. Recovery retries the same bad target repeatedly

### Evidence from production
- Queue file: `delivery-queue/10bf0390-b975-4926-aaaa-86dc3504f721.json`
  - `channel: "discord"`, `to: "channel:657229412030480397"` (this is a **user ID**, not a channel)
  - `mirror.sessionKey: "agent:main:discord:channel:657229412030480397"`
  - `lastError: "Unknown Channel"`, `retryCount: 5`
- Session store entry:
  - Key: `agent:main:discord:channel:657229412030480397`
  - `chatType: "channel"`, `groupId: "657229412030480397"`
  - `origin.from: "discord:channel:657229412030480397"`
  - `origin.to: "channel:657229412030480397"`
  - `deliveryContext.to`: **missing**
  - `sessionFile`: **missing** (no transcript — this was never a real conversation)
- Normal Discord channel sessions use actual channel IDs (e.g., `1476858065914695741`)
- The `/new` command log shows no record of this malformed key being created by user interaction

### Root cause chain
```
Synthetic/internal context builder
  → sets From = discord:channel:<senderId> (should be <channelId>)
  → resolveGroupSessionKey() extracts <senderId> as group ID
  → initSessionState() persists it as a channel session
  → deriveSessionOrigin() writes origin.to = channel:<senderId>
  → subagent announce reads this session entry
  → enqueueDelivery() targets channel:<senderId>
  → Discord returns "Unknown Channel"
  → delivery queue retries indefinitely (not classified as permanent error)
```

---

## Fix

### Overview
Three layers of defense:

1. **Block pollution at source** — Detect and reject malformed synthetic Discord channel contexts before they create session entries
2. **Session store self-healing** — Automatically prune existing malformed entries on next session init
3. **Delivery error classification** — Classify `Unknown Channel` as a permanent delivery error to prevent infinite retries

### Changes

#### 1. Pollution source guard (`src/config/sessions/groups.ts` / `src/config/sessions/metadata.ts`)

**New helper functions:**

```typescript
/**
 * Detect a malformed Discord synthetic channel context where the sender's
 * user ID was incorrectly used as the channel ID.
 *
 * Returns the sender ID if malformed, undefined otherwise.
 */
function resolveMalformedDiscordSyntheticChannelSenderId(ctx: SessionContext): string | undefined {
  const provider = normalizeMessageChannel(ctx?.OriginatingChannel || ctx?.Surface || ctx?.Provider);
  if (provider !== "discord") return;
  if (normalizeChatType(ctx?.ChatType) !== "channel") return;

  const senderId = ctx?.SenderId?.trim().toLowerCase();
  if (!senderId) return;

  const from = ctx?.From?.trim().toLowerCase() ?? "";
  const to = (ctx?.OriginatingTo ?? ctx?.To)?.trim().toLowerCase() ?? "";

  if (from === `discord:channel:${senderId}` || to === `channel:${senderId}`) {
    return senderId;
  }
}
```

**Modified functions:**

- `resolveGroupSessionKey(ctx)`: Returns `null` early if `isMalformedDiscordSyntheticChannelCtx(ctx)` is true, preventing the malformed context from being treated as a group/channel session.

- `deriveSessionKey(scope, ctx)`: When a malformed Discord synthetic channel is detected, falls back to `direct:<senderId>` instead of creating a channel session key.

- `deriveSessionOrigin(ctx)`: Suppresses `chatType`, `from`, and `to` fields when the context is malformed, preventing poisoned origin data from being persisted.

#### 2. Session store self-healing (`src/auto-reply/reply/session.ts`)

**New helper functions:**

```typescript
/**
 * Detect a malformed Discord synthetic channel session entry.
 * Matches entries where:
 * - channel = "discord", chatType = "channel"
 * - origin.from = discord:channel:<groupId>
 * - origin.to = channel:<groupId>
 * - deliveryContext.to is missing
 * - sessionFile is missing (no transcript)
 */
function isMalformedDiscordSyntheticChannelSessionEntry(entry: SessionEntry): boolean

/**
 * Scan and delete malformed Discord synthetic channel entries from the
 * session store. Called during initSessionState() after loading the store.
 */
async function pruneMalformedDiscordSyntheticChannelSessions(params: {
  storePath: string;
  sessionStore: SessionStore;
}): Promise<number>
```

**Modified function:**

- `initSessionState(params)`:
  1. Sanitizes the inbound context before processing (`sanitizeMalformedDiscordSyntheticChannelContext(ctx)`)
  2. After loading the session store, calls `pruneMalformedDiscordSyntheticChannelSessions()` to clean up any existing malformed entries
  3. Uses the sanitized context throughout the function instead of the raw `ctx`

#### 3. Delivery error classification (`src/infra/outbound/delivery-queue.ts`)

**Modified constant:**

```typescript
const PERMANENT_ERROR_PATTERNS = [
  // ... existing patterns ...
  /unknown channel/i,    // NEW
  /unknown thread/i,     // NEW
  /unknown message/i,    // NEW
];
```

#### 4. Restart sentinel guard (`src/gateway/gateway-cli.ts`)

**Modified delivery recovery logic:**

When the restart sentinel resolves a delivery target from the session key, added a guard to ignore `parsedTarget` when:
- The session's `deliveryContext.to` is missing
- The session's `chatType` is `"channel"`
- The parsed target is `channel:` prefixed on Discord

This prevents the sentinel from reconstructing a bad delivery target from a poisoned session key.

---

## Testing

### Unit-level verification (performed)

1. **Malformed context detection:**
   - Input: `From = discord:channel:657229412030480397`, `SenderId = 657229412030480397`, `ChatType = channel`
   - `resolveGroupSessionKey()` → `null` ✅
   - `resolveSessionKey()` → `agent:main:main` (not `agent:main:discord:channel:657229412030480397`) ✅
   - `deriveSessionMetaPatch()` → no `chatType`/`from`/`to` in origin ✅

2. **Normal context not affected:**
   - Input: `From = discord:channel:1476858065914695741`, `SenderId = 657229412030480397`, `ChatType = channel`
   - `resolveGroupSessionKey()` → `{ key: "discord:channel:1476858065914695741", ... }` ✅
   - `resolveSessionKey()` → `agent:main:discord:channel:1476858065914695741` ✅
   - `deriveSessionMetaPatch()` → normal group patch with correct origin ✅

3. **Malformed entry detection (session store scan):**
   - Scanned production `sessions.json` with 74 entries
   - Detected exactly 1 malformed entry: `agent:main:discord:channel:657229412030480397` ✅
   - All other Discord channel sessions were valid ✅

### Live verification (performed)

1. Gateway restarted with patched code
2. RPC probe: `ok` ✅
3. Log confirmed self-healing ran:
   ```
   [session-init] WARN: pruned malformed discord synthetic channel sessions: agent:main:discord:channel:657229412030480397
   ```
4. `sessions.json` confirmed: malformed key no longer exists (74 → 73 entries) ✅
5. No new `Unknown Channel` or delivery recovery errors in post-restart logs ✅
6. Normal Discord channel communication continues working ✅

### Suggested additional tests for CI

- [ ] Create a synthetic context with `SenderId` == channel ID in `From`, verify `resolveGroupSessionKey()` returns `null`
- [ ] Create a normal Discord channel context, verify routing is unaffected
- [ ] Create a malformed session entry in a test store, verify `pruneMalformedDiscordSyntheticChannelSessions()` removes it
- [ ] Simulate `Unknown Channel` delivery error, verify it's classified as permanent
- [ ] Test subagent announce flow with a requester session that has no `deliveryContext.to`

---

## Impact

- **Discord channel sessions**: Normal routing is unaffected (verified)
- **Discord DM sessions**: Unaffected (different code path)
- **Telegram / WhatsApp / other providers**: Unaffected (guard is Discord-specific)
- **Subagent announce**: Will no longer inherit poisoned routes from malformed requester sessions
- **Delivery queue**: `Unknown Channel` errors stop retrying immediately instead of exhausting retry budget
- **Session store**: Existing malformed entries are automatically cleaned up on next session init

## Breaking changes
None. This is a defensive fix that only changes behavior for invalid/synthetic contexts that should never have created channel sessions.

---

## Files changed

| File | Change type | Description |
|------|-------------|-------------|
| `src/config/sessions/groups.ts` | Modified + New helpers | Added malformed synthetic channel detection; `resolveGroupSessionKey()` rejects malformed ctx |
| `src/config/sessions/metadata.ts` | Modified | `deriveSessionKey()` falls back safely; `deriveSessionOrigin()` suppresses poisoned fields |
| `src/auto-reply/reply/session.ts` | Modified + New helpers | `initSessionState()` sanitizes ctx + prunes malformed entries from store |
| `src/infra/outbound/delivery-queue.ts` | Modified | Added `Unknown Channel/Thread/Message` to permanent error patterns |
| `src/gateway/gateway-cli.ts` | Modified | Restart sentinel ignores parsed target when session lacks concrete delivery context |

---

## Related issues
- Delivery queue `Unknown Channel` infinite retry (no existing issue found)
- Subagent completion announce targeting sender ID as channel (no existing issue found)

## Environment
- OpenClaw 2026.3.2 (npm, Windows)
- Discord channel sessions with subagent completion announce
- Discovered and fixed on production instance 2026-03-06/07
