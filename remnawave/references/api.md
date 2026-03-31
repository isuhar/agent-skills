# Remnawave API Reference

## Authentication

All requests require `Authorization: Bearer <JWT_TOKEN>` header.

Token types:
- **API token**: Long-lived, role=API, created via `/api/tokens`
- **Auth token**: Short-lived, obtained via `POST /api/auth/login`

Base URL: `<panel_url>/api/`

## Error Responses

| Code | Meaning |
|------|---------|
| 400 | Validation error — body: `{"message":"...","errorCode":"E000"}` |
| 401 | Unauthorized |
| 403 | Forbidden (wrong role) |
| 404 | Not found |
| 500 | Server error |

---

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login `{username, password}` → JWT |
| POST | `/api/auth/register` | Register first admin |
| GET | `/api/auth/status` | Check auth status |
| POST | `/api/auth/oauth2/authorize` | OAuth2 authorization |
| POST | `/api/auth/oauth2/callback` | OAuth2 callback |
| POST | `/api/auth/oauth2/tg/callback` | Telegram OAuth2 callback |
| GET | `/api/auth/passkey/authentication/options` | Passkey auth options |
| POST | `/api/auth/passkey/authentication/verify` | Passkey auth verify |

---

## Nodes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/nodes` | List all nodes |
| GET | `/api/nodes/{uuid}` | Get node |
| POST | `/api/nodes` | Create node |
| PATCH | `/api/nodes` | Update node (`uuid` in body) |
| DELETE | `/api/nodes/{uuid}` | Delete node |
| POST | `/api/nodes/{uuid}/actions/enable` | Enable node |
| POST | `/api/nodes/{uuid}/actions/disable` | Disable node |
| POST | `/api/nodes/{uuid}/actions/restart` | Restart xray on node |
| POST | `/api/nodes/{uuid}/actions/reset-traffic` | Reset node traffic counter |
| POST | `/api/nodes/actions/restart-all` | Restart xray on all nodes |
| POST | `/api/nodes/actions/reorder` | Reorder nodes |
| POST | `/api/nodes/bulk-actions` | Bulk node actions |
| POST | `/api/nodes/bulk-actions/profile-modification` | Bulk assign config profile |
| GET | `/api/nodes/tags` | List node tags |

---

## Config Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config-profiles` | List all profiles |
| GET | `/api/config-profiles/{uuid}` | Get profile |
| POST | `/api/config-profiles` | Create profile (`name` + `config` required) |
| PATCH | `/api/config-profiles` | Update profile (`uuid` in body) |
| DELETE | `/api/config-profiles/{uuid}` | Delete profile |
| GET | `/api/config-profiles/{uuid}/computed-config` | Get rendered xray config |
| GET | `/api/config-profiles/{uuid}/inbounds` | List inbounds in profile |
| GET | `/api/config-profiles/inbounds` | List all inbounds across all profiles |
| POST | `/api/config-profiles/actions/reorder` | Reorder profiles |

`config` field is a full xray JSON config: `{log, inbounds, outbounds, routing}`. PATCH replaces it entirely.

---

## Hosts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hosts` | List all hosts (subscription entries) |
| GET | `/api/hosts/{uuid}` | Get host |
| POST | `/api/hosts` | Create host (`inbound`, `remark`, `address`, `port` required) |
| PATCH | `/api/hosts` | Update host (`uuid` in body) |
| DELETE | `/api/hosts/{uuid}` | Delete host |
| POST | `/api/hosts/actions/reorder` | Reorder hosts |
| GET | `/api/hosts/tags` | List host tags |
| POST | `/api/hosts/bulk/delete` | Bulk delete hosts |
| POST | `/api/hosts/bulk/disable` | Bulk disable hosts |
| POST | `/api/hosts/bulk/enable` | Bulk enable hosts |
| POST | `/api/hosts/bulk/set-inbound` | Bulk assign inbound |
| POST | `/api/hosts/bulk/set-port` | Bulk set port |

Key host fields: `remark`, `address`, `port`, `sni`, `path`, `fingerprint`, `alpn`, `securityLayer`, `xHttpExtraParams`, `muxParams`, `inbound.configProfileUuid`, `inbound.configProfileInboundUuid`, `nodes[]`

---

## Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List users (paginated) |
| GET | `/api/users/{uuid}` | Get user by UUID |
| POST | `/api/users` | Create user |
| PATCH | `/api/users` | Update user (`uuid` in body) |
| DELETE | `/api/users/{uuid}` | Delete user |
| POST | `/api/users/{uuid}/actions/enable` | Enable user |
| POST | `/api/users/{uuid}/actions/disable` | Disable user |
| POST | `/api/users/{uuid}/actions/reset-traffic` | Reset user traffic |
| POST | `/api/users/{uuid}/actions/revoke` | Revoke user subscription |
| GET | `/api/users/{uuid}/accessible-nodes` | List accessible nodes |
| GET | `/api/users/{uuid}/subscription-request-history` | User sub request history |
| GET | `/api/users/by-username/{username}` | Lookup by username |
| GET | `/api/users/by-email/{email}` | Lookup by email |
| GET | `/api/users/by-short-uuid/{shortUuid}` | Lookup by short UUID |
| GET | `/api/users/by-telegram-id/{telegramId}` | Lookup by Telegram ID |
| GET | `/api/users/by-tag/{tag}` | List users with tag |
| GET | `/api/users/by-id/{id}` | Lookup by numeric ID |
| GET | `/api/users/tags` | List user tags |
| POST | `/api/users/bulk/delete` | Bulk delete users |
| POST | `/api/users/bulk/update` | Bulk update users |
| POST | `/api/users/bulk/reset-traffic` | Bulk reset traffic |
| POST | `/api/users/bulk/extend-expiration-date` | Bulk extend expiry |
| POST | `/api/users/bulk/revoke-subscription` | Bulk revoke subscriptions |
| POST | `/api/users/bulk/delete-by-status` | Bulk delete by status |
| POST | `/api/users/bulk/update-squads` | Bulk update squad assignments |
| POST | `/api/users/bulk/all/reset-traffic` | Reset traffic for all users |
| POST | `/api/users/bulk/all/extend-expiration-date` | Extend expiry for all users |
| POST | `/api/users/bulk/all/update` | Update all users |

---

## Squads (Internal)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/internal-squads` | List internal squads |
| GET | `/api/internal-squads/{uuid}` | Get squad |
| POST | `/api/internal-squads` | Create squad |
| PATCH | `/api/internal-squads` | Update squad (`uuid` in body) |
| DELETE | `/api/internal-squads/{uuid}` | Delete squad |
| GET | `/api/internal-squads/{uuid}/accessible-nodes` | Accessible nodes |
| POST | `/api/internal-squads/{uuid}/bulk-actions/add-users` | Add users to squad |
| POST | `/api/internal-squads/{uuid}/bulk-actions/remove-users` | Remove users from squad |
| POST | `/api/internal-squads/actions/reorder` | Reorder squads |

## Squads (External)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/external-squads` | List external squads |
| GET | `/api/external-squads/{uuid}` | Get squad |
| POST | `/api/external-squads` | Create squad |
| PATCH | `/api/external-squads` | Update squad (`uuid` in body) |
| DELETE | `/api/external-squads/{uuid}` | Delete squad |
| POST | `/api/external-squads/{uuid}/bulk-actions/add-users` | Add users |
| POST | `/api/external-squads/{uuid}/bulk-actions/remove-users` | Remove users |
| POST | `/api/external-squads/actions/reorder` | Reorder squads |

---

## Bandwidth Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bandwidth-stats/nodes` | Stats for all nodes |
| GET | `/api/bandwidth-stats/nodes/realtime` | Realtime node stats |
| GET | `/api/bandwidth-stats/nodes/{uuid}/users` | Per-user stats on a node |
| GET | `/api/bandwidth-stats/users/{uuid}` | Stats for a user |

---

## Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscriptions` | Subscription global settings |
| GET | `/api/subscriptions/by-uuid/{uuid}` | Get subscription by UUID |
| GET | `/api/subscriptions/by-short-uuid/{shortUuid}` | Get by short UUID |
| GET | `/api/subscriptions/by-short-uuid/{shortUuid}/raw` | Raw subscription content |
| GET | `/api/subscriptions/by-username/{username}` | Get by username |
| GET | `/api/subscriptions/subpage-config/{shortUuid}` | Subscription page config |
| GET | `/api/sub/{shortUuid}` | Subscription content (no auth) |
| GET | `/api/sub/{shortUuid}/{clientType}` | Typed subscription content |
| GET | `/api/sub/{shortUuid}/info` | Subscription info |
| GET | `/api/sub/outline/{shortUuid}/{type}/{encodedTag}` | Outline subscription |

## Subscription Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscription-settings` | Get settings |
| PATCH | `/api/subscription-settings` | Update settings |

## Subscription Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscription-templates` | List templates |
| GET | `/api/subscription-templates/{uuid}` | Get template |
| POST | `/api/subscription-templates` | Create template |
| PATCH | `/api/subscription-templates` | Update template (`uuid` in body) |
| DELETE | `/api/subscription-templates/{uuid}` | Delete template |
| POST | `/api/subscription-templates/actions/reorder` | Reorder templates |

## Subscription Page Configs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscription-page-configs` | List page configs |
| GET | `/api/subscription-page-configs/{uuid}` | Get page config |
| POST | `/api/subscription-page-configs` | Create page config |
| PATCH | `/api/subscription-page-configs` | Update page config (`uuid` in body) |
| DELETE | `/api/subscription-page-configs/{uuid}` | Delete page config |
| POST | `/api/subscription-page-configs/actions/clone` | Clone page config |
| POST | `/api/subscription-page-configs/actions/reorder` | Reorder page configs |

## Subscription Request History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscription-request-history` | List request history |
| GET | `/api/subscription-request-history/stats` | Request history stats |

---

## HWID Devices

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hwid/devices` | List all devices |
| GET | `/api/hwid/devices/{userUuid}` | Devices for user |
| POST | `/api/hwid/devices/delete` | Delete specific devices |
| POST | `/api/hwid/devices/delete-all` | Delete all devices |
| GET | `/api/hwid/devices/stats` | HWID stats |
| GET | `/api/hwid/devices/top-users` | Top users by device count |

---

## Tokens

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tokens` | List API tokens |
| GET | `/api/tokens/{uuid}` | Get token |
| POST | `/api/tokens` | Create token |
| DELETE | `/api/tokens/{uuid}` | Delete token |

---

## Passkeys

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/passkeys` | List passkeys |
| GET | `/api/passkeys/registration/options` | Registration options |
| POST | `/api/passkeys/registration/verify` | Verify registration |

---

## Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/remnawave-settings` | Get panel settings |
| PATCH | `/api/remnawave-settings` | Update panel settings |
| GET | `/api/snippets` | Get config snippets |

---

## Infra Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/infra-billing/providers` | List providers |
| GET | `/api/infra-billing/providers/{uuid}` | Get provider |
| POST | `/api/infra-billing/providers` | Create provider |
| PATCH | `/api/infra-billing/providers` | Update provider |
| DELETE | `/api/infra-billing/providers/{uuid}` | Delete provider |
| GET | `/api/infra-billing/nodes` | List billed nodes |
| GET | `/api/infra-billing/nodes/{uuid}` | Get billed node |
| POST | `/api/infra-billing/nodes` | Create billed node |
| PATCH | `/api/infra-billing/nodes` | Update billed node |
| DELETE | `/api/infra-billing/nodes/{uuid}` | Delete billed node |
| GET | `/api/infra-billing/history` | Billing history |
| GET | `/api/infra-billing/history/{uuid}` | Get billing history entry |

---

## System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/health` | Health check |
| GET | `/api/system/metadata` | Panel metadata |
| GET | `/api/system/stats` | System stats |
| GET | `/api/system/stats/bandwidth` | Bandwidth stats |
| GET | `/api/system/stats/nodes` | Node stats |
| GET | `/api/system/nodes/metrics` | Node metrics |
| GET | `/api/system/tools/x25519/generate` | Generate X25519 keypair |
| POST | `/api/system/tools/happ/encrypt` | Encrypt HAPP config |
| POST | `/api/system/testers/srr-matcher` | Test SRR matcher |

---

## Keygen

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/keygen` | Generate key pair |

---

## Common Patterns

**Update config profile routing:**
```bash
# 1. Get current config
python3 rw_api.py profiles get <uuid> > profile.json
# 2. Edit profile.json routing section
# 3. Push update
python3 rw_api.py profiles update <uuid> @profile.json
```

**Restart node after manual change:**
```bash
python3 rw_api.py nodes restart <uuid>
```

**Update host xHttpExtraParams:**
```bash
python3 rw_api.py hosts update <uuid> '{"xHttpExtraParams":{"xPaddingBytes":"100-1000"}}'
```

**Generate X25519 keypair for Reality:**
```bash
python3 rw_api.py system generate-x25519
```
