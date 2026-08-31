from __future__ import annotations

import asyncio
import hashlib
import secrets
from typing import Any
from urllib.parse import urlencode

import aiohttp


class HeatMeisterApiError(Exception):
    """Base HeatMeister API error."""


class HeatMeisterAuthenticationRequired(HeatMeisterApiError):
    """The HeatMeister requires HTTP Digest authentication."""


class HeatMeisterInvalidAuthentication(HeatMeisterApiError):
    """The supplied HeatMeister credentials were rejected."""


class HeatMeisterApi:
    """Local HTTP API client for HeatMeister with optional Digest auth."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.host = host.strip().replace("http://", "").replace("https://", "").rstrip("/")
        self._session = session
        self.username = username or None
        self.password = password if self.username else None
        self._digest_challenge: dict[str, str] | None = None
        self._nonce_count = 0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}"

    @staticmethod
    def _parse_digest_challenge(header: str | None) -> dict[str, str] | None:
        """Parse a WWW-Authenticate Digest challenge."""
        if not header or not header.lower().startswith("digest "):
            return None

        challenge = header[7:].strip()
        result: dict[str, str] = {}
        current = ""
        quoted = False
        parts: list[str] = []

        for char in challenge:
            if char == '"':
                quoted = not quoted
                current += char
            elif char == "," and not quoted:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            parts.append(current.strip())

        for part in parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            result[key.strip().lower()] = value

        if "realm" not in result or "nonce" not in result:
            return None
        return result

    @staticmethod
    def _hash(value: str, algorithm: str) -> str:
        """Hash a Digest auth component using the challenged algorithm."""
        normalized = algorithm.upper().replace("-SESS", "")
        if normalized == "MD5":
            return hashlib.md5(value.encode("utf-8")).hexdigest()
        if normalized == "SHA-256":
            return hashlib.sha256(value.encode("utf-8")).hexdigest()
        raise HeatMeisterApiError(f"Unsupported Digest algorithm: {algorithm}")

    def _build_digest_authorization(
        self,
        method: str,
        uri: str,
        challenge: dict[str, str],
    ) -> str:
        """Build an HTTP Digest Authorization header (RFC 7616 qop=auth)."""
        if not self.username:
            raise HeatMeisterAuthenticationRequired("HeatMeister requires authentication")

        realm = challenge["realm"]
        nonce = challenge["nonce"]
        opaque = challenge.get("opaque")
        algorithm = challenge.get("algorithm", "MD5")
        qop_value = challenge.get("qop")
        qop = None
        if qop_value:
            qops = [item.strip().lower() for item in qop_value.split(",")]
            if "auth" not in qops:
                raise HeatMeisterApiError(f"Unsupported Digest qop: {qop_value}")
            qop = "auth"

        self._nonce_count += 1
        nc = f"{self._nonce_count:08x}"
        cnonce = secrets.token_hex(8)

        password = self.password or ""
        ha1 = self._hash(f"{self.username}:{realm}:{password}", algorithm)
        if algorithm.upper().endswith("-SESS"):
            ha1 = self._hash(f"{ha1}:{nonce}:{cnonce}", algorithm)
        ha2 = self._hash(f"{method}:{uri}", algorithm)

        if qop:
            response = self._hash(
                f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}", algorithm
            )
        else:
            response = self._hash(f"{ha1}:{nonce}:{ha2}", algorithm)

        fields = [
            f'username="{self.username}"',
            f'realm="{realm}"',
            f'nonce="{nonce}"',
            f'uri="{uri}"',
            f'response="{response}"',
        ]
        if "algorithm" in challenge:
            fields.append(f"algorithm={algorithm}")
        if opaque is not None:
            fields.append(f'opaque="{opaque}"')
        if qop:
            fields.extend([f"qop={qop}", f"nc={nc}", f'cnonce="{cnonce}"'])

        return "Digest " + ", ".join(fields)

    async def _async_request(
        self,
        path: str,
        params: dict[str, str] | None = None,
        expect_json: bool = False,
    ) -> Any:
        """Perform a request, negotiating Digest auth when required."""
        query = urlencode(params or {})
        uri = path + (f"?{query}" if query else "")
        url = f"{self.base_url}{uri}"

        async def do_request(authorization: str | None = None):
            headers = {"Authorization": authorization} if authorization else None
            return await self._session.get(url, headers=headers)

        try:
            async with asyncio.timeout(5):
                authorization = None
                if self.username and self._digest_challenge:
                    authorization = self._build_digest_authorization(
                        "GET", uri, self._digest_challenge
                    )

                response = await do_request(authorization)

                if response.status == 401:
                    challenge = self._parse_digest_challenge(
                        response.headers.get("WWW-Authenticate")
                    )
                    response.release()

                    if challenge is None:
                        raise HeatMeisterApiError(
                            "HeatMeister requested unsupported authentication"
                        )

                    self._digest_challenge = challenge
                    self._nonce_count = 0

                    if not self.username:
                        raise HeatMeisterAuthenticationRequired(
                            "HeatMeister requires Digest authentication"
                        )

                    authorization = self._build_digest_authorization(
                        "GET", uri, challenge
                    )
                    response = await do_request(authorization)

                    if response.status == 401:
                        response.release()
                        raise HeatMeisterInvalidAuthentication(
                            "HeatMeister rejected the supplied credentials"
                        )

                response.raise_for_status()
                if expect_json:
                    data = await response.json(content_type=None)
                    response.release()
                    return data

                await response.read()
                response.release()
                return None

        except (
            HeatMeisterAuthenticationRequired,
            HeatMeisterInvalidAuthentication,
            HeatMeisterApiError,
        ):
            raise
        except (TimeoutError, aiohttp.ClientError, ValueError) as err:
            raise HeatMeisterApiError(
                f"Could not communicate with HeatMeister at {self.host}"
            ) from err

    async def async_get_status(self) -> dict[str, Any]:
        data = await self._async_request("/getStatus", expect_json=True)
        if not isinstance(data, dict) or "NODE_NAME" not in data:
            raise HeatMeisterApiError("Unexpected response from HeatMeister")
        return data

    async def async_set_status(self, **params: Any) -> None:
        await self._async_request(
            "/setStatus",
            params={key: str(value) for key, value in params.items()},
        )
