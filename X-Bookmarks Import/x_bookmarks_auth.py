from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from x_runtime import atomic_write_text, request_json, summarize_payload


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: str
    token_file: Path
    auth_timeout_seconds: int = 300
    oauth_server_timeout_seconds: int = 10


class _Handler(BaseHTTPRequestHandler):
    code: str | None = None
    error_message: str | None = None
    expected_state: str | None = None

    def do_GET(self) -> None:  # noqa: N802
        query = parse_qs(urlparse(self.path).query)
        returned_state = query.get("state", [None])[0]
        error_value = query.get("error", [None])[0]
        error_description = query.get("error_description", [None])[0]

        if error_value:
            _Handler.error_message = error_description or error_value
            logger.warning("OAuth callback returned error: %s", _Handler.error_message)
            self._write_html(400, f"<h2>Error: {_Handler.error_message}</h2>")
            return

        if returned_state != _Handler.expected_state:
            _Handler.error_message = "OAuth callback state mismatch."
            logger.warning("Rejected OAuth callback because state validation failed.")
            self._write_html(400, "<h2>Error: invalid state</h2>")
            return

        code = query.get("code", [None])[0]
        if not code:
            _Handler.error_message = "OAuth callback did not include an authorization code."
            logger.warning("Rejected OAuth callback because code was missing.")
            self._write_html(400, "<h2>Error: missing code</h2>")
            return

        _Handler.code = code
        self._write_html(200, "<h2>Done! You can close this tab.</h2>")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        logger.debug("OAuth callback server: " + format, *args)

    def _write_html(self, status_code: int, payload: str) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(payload.encode("utf-8"))


def get_access_token(config: AuthConfig) -> str:
    if config.token_file.exists():
        token_data = json.loads(config.token_file.read_text(encoding="utf-8"))
        expires_in = token_data.get("expires_in", 7200)
        obtained = token_data.get("obtained_at", 0)
        if time.time() < obtained + expires_in - 60:
            return token_data["access_token"]
        if "refresh_token" in token_data:
            logger.info("Token expired, refreshing...")
            refreshed = _refresh_token(config, token_data["refresh_token"])
            if refreshed:
                return refreshed["access_token"]

    token_data = _do_pkce_auth(config)
    return token_data["access_token"]


def _do_pkce_auth(config: AuthConfig):
    verifier = secrets.token_urlsafe(64)[:128]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(32)
    _Handler.code = None
    _Handler.error_message = None
    _Handler.expected_state = state

    auth_url = "https://twitter.com/i/oauth2/authorize?" + urlencode(
        {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": config.scopes,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )

    server = HTTPServer(("127.0.0.1", 8765), _Handler)
    server.timeout = config.oauth_server_timeout_seconds

    try:
        logger.info("Opening browser for X authorization...")
        logger.info("If the browser does not open, visit:\n%s\n", auth_url)
        webbrowser.open(auth_url)

        logger.info("Waiting for authorization (timeout: 5 minutes)...")
        deadline = time.time() + config.auth_timeout_seconds
        while _Handler.code is None and _Handler.error_message is None and time.time() < deadline:
            server.handle_request()
    finally:
        server.server_close()

    if _Handler.error_message:
        raise RuntimeError(f"Authorization failed: {_Handler.error_message}")
    if _Handler.code is None:
        raise RuntimeError("Authorization timed out after 5 minutes.")

    logger.info("Exchanging code for token...")
    credentials = base64.b64encode(f"{config.client_id}:{config.client_secret}".encode()).decode()
    response = request_json(
        "POST",
        "https://api.twitter.com/2/oauth2/token",
        headers={"Authorization": f"Basic {credentials}"},
        form_data={
            "code": _Handler.code,
            "grant_type": "authorization_code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "code_verifier": verifier,
        },
        context="POST https://api.twitter.com/2/oauth2/token",
    )

    if response.status != 200:
        raise RuntimeError(f"Token exchange failed ({response.status}): {summarize_payload(response.data)}")

    token_data = response.data
    token_data["obtained_at"] = time.time()
    _write_token_file(config, token_data)
    logger.info("Token saved.")
    return token_data


def _refresh_token(config: AuthConfig, refresh_token: str):
    credentials = base64.b64encode(f"{config.client_id}:{config.client_secret}".encode()).decode()
    response = request_json(
        "POST",
        "https://api.twitter.com/2/oauth2/token",
        headers={"Authorization": f"Basic {credentials}"},
        form_data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": config.client_id,
        },
        context="POST https://api.twitter.com/2/oauth2/token",
    )
    if response.status == 200:
        data = response.data
        data["obtained_at"] = time.time()
        _write_token_file(config, data)
        logger.info("Token refreshed.")
        return data

    logger.warning("Token refresh failed (%s): %s", response.status, summarize_payload(response.data))
    return None


def _write_token_file(config: AuthConfig, token_data: dict[str, object]) -> None:
    atomic_write_text(config.token_file, json.dumps(token_data, indent=2))
