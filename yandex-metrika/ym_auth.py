"""
Yandex Metrika / Direct OAuth helper.

Reads YANDEX_METRIKA_TOKEN (base64 JSON with access_token, refresh_token, etc.),
checks expiry, refreshes if needed, and updates the env var + file.

Usage:
    from ym_auth import get_token
    token = get_token()  # ready-to-use access_token
"""

import base64
import json
import os
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

ENV_KEY = "YANDEX_METRIKA_TOKEN"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".ym_token_cache.json")

# Refresh 1 hour before expiry
EXPIRY_BUFFER = 3600


def _decode_env() -> dict:
    """Decode base64 JSON from env, or return empty dict."""
    raw = os.environ.get(ENV_KEY, "")
    if not raw:
        return {}
    try:
        decoded = base64.b64decode(raw + "==")
        return json.loads(decoded)
    except Exception:
        # Might be a plain token (legacy)
        return {"access_token": raw}


def _load_cache() -> dict:
    """Load cached token data with issued_at timestamp."""
    try:
        with open(TOKEN_FILE) as f:
            return json.loads(f.read())
    except Exception:
        return {}


def _save_cache(data: dict):
    """Persist token data to cache file."""
    try:
        with open(TOKEN_FILE, "w") as f:
            f.write(json.dumps(data))
    except Exception:
        pass


def _is_expired(data: dict) -> bool:
    """Check if token is expired or close to expiry."""
    issued_at = data.get("issued_at", 0)
    expires_in = data.get("expires_in", 0)
    if not issued_at or not expires_in:
        return False  # can't determine, assume valid
    return time.time() > (issued_at + expires_in - EXPIRY_BUFFER)


def _refresh(data: dict) -> dict:
    """Refresh the access token using refresh_token."""
    refresh_token = data.get("refresh_token", "")
    client_id = os.environ.get("YANDEX_CLIENT_ID", "")
    client_secret = os.environ.get("YANDEX_CLIENT_SECRET", "")

    if not all([refresh_token, client_id, client_secret]):
        raise RuntimeError(
            "Cannot refresh: need refresh_token, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET"
        )

    body = urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()

    req = Request("https://oauth.yandex.ru/token", data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    resp = urlopen(req, timeout=15)
    new_data = json.loads(resp.read())
    new_data["issued_at"] = int(time.time())
    return new_data


def _update_env(data: dict):
    """Update the env var with new base64-encoded token data."""
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    os.environ[ENV_KEY] = encoded


def get_token() -> str:
    """
    Get a valid access_token. Refreshes automatically if expired.
    Returns the access_token string ready for Authorization header.
    """
    # Start from env (source of truth)
    data = _decode_env()
    cache = _load_cache()

    # Merge issued_at from cache if env doesn't have it
    if "issued_at" not in data and "issued_at" in cache:
        # Only use cache issued_at if tokens match
        if cache.get("access_token") == data.get("access_token"):
            data["issued_at"] = cache["issued_at"]

    # If no issued_at yet, set it now (first run)
    if "issued_at" not in data and data.get("access_token"):
        data["issued_at"] = int(time.time())
        _save_cache(data)

    # Check if we need to refresh
    if _is_expired(data) and data.get("refresh_token"):
        try:
            data = _refresh(data)
            _update_env(data)
            _save_cache(data)
        except Exception as e:
            # If refresh fails, try existing token anyway
            import sys
            print(f"Warning: token refresh failed: {e}", file=sys.stderr)

    # Test the token with a simple request
    # (only on first use / after refresh — skip for performance)

    return data.get("access_token", "")


if __name__ == "__main__":
    token = get_token()
    print(f"Token: {token[:20]}...")
    print(f"Length: {len(token)}")
