---
name: remnawave
description: Manage Remnawave VPN panel — nodes, config profiles, hosts, users, squads, subscriptions, bandwidth stats, HWID devices, API tokens, billing, and system tools via REST API. Use when working with Remnawave panel operations like viewing/restarting nodes, updating xray config profiles (inbounds, outbounds, routing), managing subscription hosts (xHttpExtraParams, downloadSettings, split configuration), user CRUD and bulk operations, squad management (internal/external), subscription templates and settings, bandwidth statistics, HWID device tracking, or system diagnostics. Triggers on "remnawave", "VPN panel", "config profile", "xray config", "hosts", "subscription", "nodes", "squads", "bandwidth stats", "HWID".
---

# Remnawave Panel Management

## Prerequisites

- **Panel URL**: Accessible directly or via SSH tunnel
- **API token**: JWT with API role or session token from login
- Env vars: `REMNAWAVE_URL`, `REMNAWAVE_TOKEN`

If panel is behind firewall:
```bash
ssh -f -N -L 3001:localhost:3001 user@panel-server
# Use http://localhost:3001
```

## CLI Script

`scripts/rw_api.py` — Python client (stdlib only, no pip).

```bash
python3 scripts/rw_api.py --url $REMNAWAVE_URL --token $REMNAWAVE_TOKEN <resource> <action> [args]
```

### Resources and actions

| Resource | Actions |
|----------|---------|
| `nodes` | `list` `get` `restart` `restart-all` `enable` `disable` `reset-traffic` `tags` `reorder` |
| `profiles` | `list` `get` `create` `update` `delete` `computed` `inbounds` `inbounds-all` `reorder` |
| `hosts` | `list` `get` `create` `update` `delete` `tags` `reorder` |
| `hosts-bulk` | `enable` `disable` `delete` `set-inbound` `set-port` |
| `users` | `list` `get` `create` `update` `delete` `enable` `disable` `reset-traffic` `revoke` `tags` |
| `users` | `by-username` `by-email` `by-short-uuid` `by-telegram-id` `by-tag` `by-id` |
| `users` | `accessible-nodes` `request-history` |
| `users-bulk` | `delete` `update` `reset-traffic` `extend-expiration` `revoke-subscription` `delete-by-status` `update-squads` |
| `users-bulk-all` | `reset-traffic` `extend-expiration` `update` |
| `squads` | `list` `get` `create` `update` `delete` `add-users` `remove-users` `reorder` (use `--type internal\|external`) |
| `stats` | `nodes` `nodes-realtime` `node-users <uuid>` `user <uuid>` |
| `subscriptions` | `get` `by-short-uuid` `by-username` `raw` `subpage-config` |
| `subscription-settings` | `get` `update` |
| `subscription-templates` | `list` `get` `create` `update` `delete` `reorder` |
| `subscription-page-configs` | `list` `get` `create` `update` `delete` `clone` `reorder` |
| `request-history` | `list` `stats` |
| `hwid` | `list` `user <uuid>` `stats` `top-users` `delete` `delete-all` |
| `tokens` | `list` `get` `create` `delete` |
| `keygen` | `generate` |
| `settings` | `get` `update` |
| `snippets` | `list` |
| `infra-billing` | `providers-list` `provider-get` `provider-create` `provider-update` `provider-delete` |
| `infra-billing` | `nodes-list` `node-get` `node-create` `node-update` `node-delete` |
| `infra-billing` | `history` `history-get` |
| `system` | `health` `metadata` `stats` `bandwidth` `node-stats` `node-metrics` `generate-x25519` `happ-encrypt` `srr-matcher` |
| `sub` | `get <shortUuid>` `get-typed <shortUuid> <clientType>` `info <shortUuid>` |

### Examples

```bash
# List nodes
rw_api.py nodes list

# Update config profile
rw_api.py profiles update PROFILE_UUID '{"config":{...}}'

# Update host extra params
rw_api.py hosts update HOST_UUID '{"xHttpExtraParams":{"scMaxEachPostBytes":50000}}'

# Get user by telegram ID
rw_api.py users by-telegram-id 177030771

# Bandwidth stats
rw_api.py stats nodes-realtime

# Restart all nodes
rw_api.py nodes restart-all
```

JSON args can be inline or `@filepath`.

## Common workflows

**Update xray routing:** Get profile → modify config.routing.rules → update profile. Xray auto-restarts.

**Update XHTTP params across hosts:** List hosts → update each host's `xHttpExtraParams`.

**User management:** Create/update users, manage squads, track bandwidth, handle HWID devices.

## Full API Reference

See `references/api.md` for complete endpoint documentation.
