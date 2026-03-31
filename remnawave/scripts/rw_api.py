#!/usr/bin/env python3
"""Remnawave Panel API client.

Usage:
    rw_api.py --url URL --token TOKEN <command> [options]

Environment variables (fallback):
    REMNAWAVE_URL   - Panel base URL (e.g. http://localhost:3001)
    REMNAWAVE_TOKEN - JWT API token

Commands:
    nodes list|get <uuid>|restart <uuid>|restart-all|enable <uuid>|disable <uuid>|reset-traffic <uuid>|tags
    profiles list|get <uuid>|update <uuid> <json|@file>|computed <uuid>|inbounds [uuid]|reorder <json>
    hosts list|get <uuid>|update <uuid> <json|@file>|create <json|@file>|delete <uuid>|tags|reorder <json>
    hosts-bulk enable|disable|delete|set-inbound|set-port <json|@file>
    users list|get <uuid>|create <json|@file>|update <json|@file>|delete <uuid>
    users get-by username|email|short-uuid|telegram-id|tag|id <value>
    users enable|disable|reset-traffic|revoke <uuid>
    users accessible-nodes <uuid>|request-history <uuid>|tags
    users-bulk delete|update|reset-traffic|extend-expiration|revoke-subscription|delete-by-status|update-squads <json>
    users-bulk-all reset-traffic|extend-expiration|update <json>
    squads list [--type internal|external]|get <uuid>|create <json>|update <json>|delete <uuid>
    squads add-users <uuid> <json>|remove-users <uuid> <json>|accessible-nodes <uuid>|reorder <json>
    stats nodes|nodes-realtime|node-users <uuid>|user <uuid>
    subscriptions settings|get <uuid>|get-by-short-uuid <shortUuid>|get-by-username <username>|raw <shortUuid>
    subscription-templates list|get <uuid>|create <json>|update <json>|delete <uuid>|reorder <json>
    subscription-page-configs list|get <uuid>|create <json>|update <json>|delete <uuid>|clone <json>|reorder <json>
    subscription-settings get|update <json>
    request-history list|stats
    hwid list|user <uuid>|stats|top-users|delete <json>|delete-all
    tokens list|get <uuid>|create <json>|delete <uuid>
    keygen <json>
    passkeys list|registration-options|registration-verify <json>
    settings get|update <json>
    snippets list
    infra-billing providers-list|provider-get <uuid>|provider-create <json>|provider-update <json>|provider-delete <uuid>
    infra-billing nodes-list|node-get <uuid>|node-create <json>|node-update <json>|node-delete <uuid>
    infra-billing history|history-get <uuid>
    system health|metadata|stats|bandwidth|node-stats|node-metrics|generate-x25519|happ-encrypt <json>|srr-matcher <json>
    sub get <shortUuid> [clientType]|info <shortUuid>
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def api(base_url, token, method, path, data=None):
    url = f"{base_url.rstrip('/')}/api/{path.lstrip('/')}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)


def load_json(s):
    if s.startswith("@"):
        with open(s[1:]) as f:
            return json.load(f)
    return json.loads(s)


def pp(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


# Route table: (resource, action) -> (method, path_template, body_mode)
# body_mode: None=no body, "json"=positional json arg, "uuid_json"=uuid in body+json, "uuid_path"=uuid in path
ROUTES = {
    # Nodes
    ("nodes", "list"): ("GET", "nodes", None),
    ("nodes", "get"): ("GET", "nodes/{0}", None),
    ("nodes", "restart"): ("POST", "nodes/{0}/actions/restart", None),
    ("nodes", "restart-all"): ("POST", "nodes/actions/restart-all", None),
    ("nodes", "enable"): ("POST", "nodes/{0}/actions/enable", None),
    ("nodes", "disable"): ("POST", "nodes/{0}/actions/disable", None),
    ("nodes", "reset-traffic"): ("POST", "nodes/{0}/actions/reset-traffic", None),
    ("nodes", "tags"): ("GET", "nodes/tags", None),
    ("nodes", "reorder"): ("POST", "nodes/actions/reorder", "json"),
    # Config Profiles
    ("profiles", "list"): ("GET", "config-profiles", None),
    ("profiles", "get"): ("GET", "config-profiles/{0}", None),
    ("profiles", "update"): ("PATCH", "config-profiles", "uuid_json"),
    ("profiles", "create"): ("POST", "config-profiles", "json"),
    ("profiles", "delete"): ("DELETE", "config-profiles/{0}", None),
    ("profiles", "computed"): ("GET", "config-profiles/{0}/computed-config", None),
    ("profiles", "inbounds-all"): ("GET", "config-profiles/inbounds", None),
    ("profiles", "inbounds"): ("GET", "config-profiles/{0}/inbounds", None),
    ("profiles", "reorder"): ("POST", "config-profiles/actions/reorder", "json"),
    # Hosts
    ("hosts", "list"): ("GET", "hosts", None),
    ("hosts", "get"): ("GET", "hosts/{0}", None),
    ("hosts", "create"): ("POST", "hosts", "json"),
    ("hosts", "update"): ("PATCH", "hosts", "uuid_json"),
    ("hosts", "delete"): ("DELETE", "hosts/{0}", None),
    ("hosts", "tags"): ("GET", "hosts/tags", None),
    ("hosts", "reorder"): ("POST", "hosts/actions/reorder", "json"),
    # Hosts Bulk
    ("hosts-bulk", "delete"): ("POST", "hosts/bulk/delete", "json"),
    ("hosts-bulk", "disable"): ("POST", "hosts/bulk/disable", "json"),
    ("hosts-bulk", "enable"): ("POST", "hosts/bulk/enable", "json"),
    ("hosts-bulk", "set-inbound"): ("POST", "hosts/bulk/set-inbound", "json"),
    ("hosts-bulk", "set-port"): ("POST", "hosts/bulk/set-port", "json"),
    # Users
    ("users", "list"): ("GET", "users", None),
    ("users", "get"): ("GET", "users/{0}", None),
    ("users", "create"): ("POST", "users", "json"),
    ("users", "update"): ("PATCH", "users", "json"),
    ("users", "delete"): ("DELETE", "users/{0}", None),
    ("users", "enable"): ("POST", "users/{0}/actions/enable", None),
    ("users", "disable"): ("POST", "users/{0}/actions/disable", None),
    ("users", "reset-traffic"): ("POST", "users/{0}/actions/reset-traffic", None),
    ("users", "revoke"): ("POST", "users/{0}/actions/revoke", None),
    ("users", "accessible-nodes"): ("GET", "users/{0}/accessible-nodes", None),
    ("users", "request-history"): ("GET", "users/{0}/subscription-request-history", None),
    ("users", "tags"): ("GET", "users/tags", None),
    ("users", "by-username"): ("GET", "users/by-username/{0}", None),
    ("users", "by-email"): ("GET", "users/by-email/{0}", None),
    ("users", "by-short-uuid"): ("GET", "users/by-short-uuid/{0}", None),
    ("users", "by-telegram-id"): ("GET", "users/by-telegram-id/{0}", None),
    ("users", "by-tag"): ("GET", "users/by-tag/{0}", None),
    ("users", "by-id"): ("GET", "users/by-id/{0}", None),
    # Users Bulk
    ("users-bulk", "delete"): ("POST", "users/bulk/delete", "json"),
    ("users-bulk", "update"): ("POST", "users/bulk/update", "json"),
    ("users-bulk", "reset-traffic"): ("POST", "users/bulk/reset-traffic", "json"),
    ("users-bulk", "extend-expiration"): ("POST", "users/bulk/extend-expiration-date", "json"),
    ("users-bulk", "revoke-subscription"): ("POST", "users/bulk/revoke-subscription", "json"),
    ("users-bulk", "delete-by-status"): ("POST", "users/bulk/delete-by-status", "json"),
    ("users-bulk", "update-squads"): ("POST", "users/bulk/update-squads", "json"),
    ("users-bulk-all", "reset-traffic"): ("POST", "users/bulk/all/reset-traffic", "json"),
    ("users-bulk-all", "extend-expiration"): ("POST", "users/bulk/all/extend-expiration-date", "json"),
    ("users-bulk-all", "update"): ("POST", "users/bulk/all/update", "json"),
    # Internal Squads
    ("internal-squads", "list"): ("GET", "internal-squads", None),
    ("internal-squads", "get"): ("GET", "internal-squads/{0}", None),
    ("internal-squads", "create"): ("POST", "internal-squads", "json"),
    ("internal-squads", "update"): ("PATCH", "internal-squads", "json"),
    ("internal-squads", "delete"): ("DELETE", "internal-squads/{0}", None),
    ("internal-squads", "accessible-nodes"): ("GET", "internal-squads/{0}/accessible-nodes", None),
    ("internal-squads", "add-users"): ("POST", "internal-squads/{0}/bulk-actions/add-users", "json"),
    ("internal-squads", "remove-users"): ("POST", "internal-squads/{0}/bulk-actions/remove-users", "json"),
    ("internal-squads", "reorder"): ("POST", "internal-squads/actions/reorder", "json"),
    # External Squads
    ("external-squads", "list"): ("GET", "external-squads", None),
    ("external-squads", "get"): ("GET", "external-squads/{0}", None),
    ("external-squads", "create"): ("POST", "external-squads", "json"),
    ("external-squads", "update"): ("PATCH", "external-squads", "json"),
    ("external-squads", "delete"): ("DELETE", "external-squads/{0}", None),
    ("external-squads", "add-users"): ("POST", "external-squads/{0}/bulk-actions/add-users", "json"),
    ("external-squads", "remove-users"): ("POST", "external-squads/{0}/bulk-actions/remove-users", "json"),
    ("external-squads", "reorder"): ("POST", "external-squads/actions/reorder", "json"),
    # Bandwidth Stats
    ("stats", "nodes"): ("GET", "bandwidth-stats/nodes", None),
    ("stats", "nodes-realtime"): ("GET", "bandwidth-stats/nodes/realtime", None),
    ("stats", "node-users"): ("GET", "bandwidth-stats/nodes/{0}/users", None),
    ("stats", "user"): ("GET", "bandwidth-stats/users/{0}", None),
    # Subscriptions
    ("subscriptions", "get"): ("GET", "subscriptions/by-uuid/{0}", None),
    ("subscriptions", "by-short-uuid"): ("GET", "subscriptions/by-short-uuid/{0}", None),
    ("subscriptions", "raw"): ("GET", "subscriptions/by-short-uuid/{0}/raw", None),
    ("subscriptions", "by-username"): ("GET", "subscriptions/by-username/{0}", None),
    ("subscriptions", "subpage-config"): ("GET", "subscriptions/subpage-config/{0}", None),
    # Subscription Settings
    ("subscription-settings", "get"): ("GET", "subscription-settings", None),
    ("subscription-settings", "update"): ("PATCH", "subscription-settings", "json"),
    # Subscription Templates
    ("subscription-templates", "list"): ("GET", "subscription-templates", None),
    ("subscription-templates", "get"): ("GET", "subscription-templates/{0}", None),
    ("subscription-templates", "create"): ("POST", "subscription-templates", "json"),
    ("subscription-templates", "update"): ("PATCH", "subscription-templates", "json"),
    ("subscription-templates", "delete"): ("DELETE", "subscription-templates/{0}", None),
    ("subscription-templates", "reorder"): ("POST", "subscription-templates/actions/reorder", "json"),
    # Subscription Page Configs
    ("subscription-page-configs", "list"): ("GET", "subscription-page-configs", None),
    ("subscription-page-configs", "get"): ("GET", "subscription-page-configs/{0}", None),
    ("subscription-page-configs", "create"): ("POST", "subscription-page-configs", "json"),
    ("subscription-page-configs", "update"): ("PATCH", "subscription-page-configs", "json"),
    ("subscription-page-configs", "delete"): ("DELETE", "subscription-page-configs/{0}", None),
    ("subscription-page-configs", "clone"): ("POST", "subscription-page-configs/actions/clone", "json"),
    ("subscription-page-configs", "reorder"): ("POST", "subscription-page-configs/actions/reorder", "json"),
    # Request History
    ("request-history", "list"): ("GET", "subscription-request-history", None),
    ("request-history", "stats"): ("GET", "subscription-request-history/stats", None),
    # HWID
    ("hwid", "list"): ("GET", "hwid/devices", None),
    ("hwid", "user"): ("GET", "hwid/devices/{0}", None),
    ("hwid", "stats"): ("GET", "hwid/devices/stats", None),
    ("hwid", "top-users"): ("GET", "hwid/devices/top-users", None),
    ("hwid", "delete"): ("POST", "hwid/devices/delete", "json"),
    ("hwid", "delete-all"): ("POST", "hwid/devices/delete-all", None),
    # API Tokens
    ("tokens", "list"): ("GET", "tokens", None),
    ("tokens", "get"): ("GET", "tokens/{0}", None),
    ("tokens", "create"): ("POST", "tokens", "json"),
    ("tokens", "delete"): ("DELETE", "tokens/{0}", None),
    # Keygen
    ("keygen", "generate"): ("POST", "keygen", "json"),
    # Passkeys
    ("passkeys", "list"): ("GET", "passkeys", None),
    ("passkeys", "registration-options"): ("GET", "passkeys/registration/options", None),
    ("passkeys", "registration-verify"): ("POST", "passkeys/registration/verify", "json"),
    # Settings
    ("settings", "get"): ("GET", "remnawave-settings", None),
    ("settings", "update"): ("PATCH", "remnawave-settings", "json"),
    # Snippets
    ("snippets", "list"): ("GET", "snippets", None),
    # Infra Billing
    ("infra-billing", "providers-list"): ("GET", "infra-billing/providers", None),
    ("infra-billing", "provider-get"): ("GET", "infra-billing/providers/{0}", None),
    ("infra-billing", "provider-create"): ("POST", "infra-billing/providers", "json"),
    ("infra-billing", "provider-update"): ("PATCH", "infra-billing/providers", "json"),
    ("infra-billing", "provider-delete"): ("DELETE", "infra-billing/providers/{0}", None),
    ("infra-billing", "nodes-list"): ("GET", "infra-billing/nodes", None),
    ("infra-billing", "node-get"): ("GET", "infra-billing/nodes/{0}", None),
    ("infra-billing", "node-create"): ("POST", "infra-billing/nodes", "json"),
    ("infra-billing", "node-update"): ("PATCH", "infra-billing/nodes", "json"),
    ("infra-billing", "node-delete"): ("DELETE", "infra-billing/nodes/{0}", None),
    ("infra-billing", "history"): ("GET", "infra-billing/history", None),
    ("infra-billing", "history-get"): ("GET", "infra-billing/history/{0}", None),
    # System
    ("system", "health"): ("GET", "system/health", None),
    ("system", "metadata"): ("GET", "system/metadata", None),
    ("system", "stats"): ("GET", "system/stats", None),
    ("system", "bandwidth"): ("GET", "system/stats/bandwidth", None),
    ("system", "node-stats"): ("GET", "system/stats/nodes", None),
    ("system", "node-metrics"): ("GET", "system/nodes/metrics", None),
    ("system", "generate-x25519"): ("GET", "system/tools/x25519/generate", None),
    ("system", "happ-encrypt"): ("POST", "system/tools/happ/encrypt", "json"),
    ("system", "srr-matcher"): ("POST", "system/testers/srr-matcher", "json"),
    # Sub (subscription content)
    ("sub", "get"): ("GET", "sub/{0}", None),
    ("sub", "get-typed"): ("GET", "sub/{0}/{1}", None),
    ("sub", "info"): ("GET", "sub/{0}/info", None),
}


def main():
    parser = argparse.ArgumentParser(description="Remnawave API client", usage=__doc__)
    parser.add_argument("--url", default=os.environ.get("REMNAWAVE_URL", ""))
    parser.add_argument("--token", default=os.environ.get("REMNAWAVE_TOKEN", ""))
    parser.add_argument("command", nargs="+")
    args = parser.parse_args()

    if not args.url or not args.token:
        print("Error: --url and --token required (or REMNAWAVE_URL/REMNAWAVE_TOKEN env)", file=sys.stderr)
        sys.exit(1)

    cmd = args.command
    resource = cmd[0] if len(cmd) > 0 else ""
    action = cmd[1] if len(cmd) > 1 else ""
    rest = cmd[2:]

    # Squads shortcut: "squads --type internal list" → "internal-squads list"
    if resource == "squads":
        squad_type = "internal"
        if "--type" in cmd:
            idx = cmd.index("--type")
            if idx + 1 < len(cmd):
                squad_type = cmd[idx + 1]
                cmd = [c for i, c in enumerate(cmd) if i != idx and i != idx + 1]
        resource = f"{squad_type}-squads"
        action = cmd[1] if len(cmd) > 1 else ""
        rest = cmd[2:]

    key = (resource, action)
    if key not in ROUTES:
        # Try without action for single-action resources
        key = (resource, cmd[1] if len(cmd) > 1 else "")
        if key not in ROUTES:
            print(f"Unknown command: {' '.join(cmd)}", file=sys.stderr)
            print(f"Available resources: {sorted(set(r for r, _ in ROUTES))}", file=sys.stderr)
            sys.exit(1)

    method, path_tpl, body_mode = ROUTES[key]

    # Build path with positional args
    path = path_tpl
    arg_idx = 0
    while "{" + str(arg_idx) + "}" in path and arg_idx < len(rest):
        path = path.replace("{" + str(arg_idx) + "}", rest[arg_idx])
        arg_idx += 1

    # Build body
    data = None
    if body_mode == "json" and arg_idx < len(rest):
        data = load_json(rest[arg_idx])
    elif body_mode == "uuid_json" and len(rest) >= 2:
        data = load_json(rest[1])
        data["uuid"] = rest[0]
    elif body_mode == "json" and arg_idx >= len(rest) and method in ("POST", "PATCH"):
        data = {}  # empty body for POST without args

    pp(api(args.url, args.token, method, path, data))


if __name__ == "__main__":
    main()
