from __future__ import annotations

from mcp.server.auth.provider import AccessToken, TokenVerifier


class StaticBearerTokenVerifier(TokenVerifier):
    """Verify a single static bearer token from request headers."""

    def __init__(self, expected_token: str) -> None:
        token = expected_token.strip()
        if not token:
            raise ValueError("expected_token must not be empty")
        self._expected_token = token

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != self._expected_token:
            return None
        return AccessToken(
            token=token,
            client_id="tdxquant-http-client",
            scopes=[],
            expires_at=None,
            resource=None,
        )
