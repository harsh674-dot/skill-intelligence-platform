import os
import logging
import jwt
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SSOAdapter:
    """
    SSO Integration (Section 6):
    Authentication via government IdP (SAML/OIDC/OIDC).

    In production this integrates with the actual government IdP.
    This implementation supports JWT-based validation when configured
    and falls back to demo mode for development.
    """

    def __init__(self):
        self.enabled = os.environ.get("SSO_ENABLED", "false").lower() == "true"
        self.idp_url = os.environ.get("SSO_IDP_URL", "")
        self.client_id = os.environ.get("SSO_CLIENT_ID", "")
        self.client_secret = os.environ.get("SSO_CLIENT_SECRET", "")
        self.jwt_secret = os.environ.get("SSO_JWT_SECRET", "demo-secret-key-change-in-production")
        self.jwt_algorithm = os.environ.get("SSO_JWT_ALGORITHM", "HS256")
        self.demo_mode = os.environ.get("SSO_DEMO_MODE", "true").lower() == "true"

    def is_configured(self) -> bool:
        return self.enabled and bool(self.idp_url and self.client_id)

    def authorize(self, sso_token: str) -> Optional[dict]:
        """
        Validate SSO token and return user identity.

        Production: validates JWT token or calls IdP introspection.
        Demo: decodes and validates demo JWT or returns mock identity.
        """
        if not self.enabled and not self.demo_mode:
            logger.info("SSO not enabled and demo mode off, falling back to JWT auth")
            return None

        try:
            identity = self._validate_token(sso_token)
            if identity:
                return identity
        except Exception as exc:
            logger.error(f"SSO authorization failed: {exc}")
            return None

        if self.demo_mode:
            return self._mock_identity(sso_token)

        return None

    def _validate_token(self, token: str) -> Optional[dict]:
        """Validate a JWT token (works for both production and demo JWTs)."""
        if not token:
            return None
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
            )
            return {
                "sub": payload.get("sub", ""),
                "email": payload.get("email", ""),
                "name": payload.get("name", ""),
                "department": payload.get("department", ""),
                "role": payload.get("role", "employee"),
                "ssp_provider": "government-idp",
                "issued_at": payload.get("iat"),
                "expires_at": payload.get("exp"),
            }
        except jwt.ExpiredSignatureError:
            logger.warning("SSO token expired")
            return None
        except jwt.InvalidTokenError:
            logger.debug("SSO token invalid, trying demo")
            return None

    def _mock_identity(self, token: str) -> dict:
        """Return mock identity for demo/testing."""
        email = "demo@moSPI.gov.in"
        name = "Demo Official"
        department = "Statistics"
        role = "employee"

        if token:
            try:
                import base64, json
                parts = token.split(".")
                if len(parts) == 3:
                    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
                    decoded = base64.urlsafe_b64decode(padded)
                    payload = json.loads(decoded)
                    email = payload.get("email", email)
                    name = payload.get("name", name)
                    department = payload.get("department", department)
                    role = payload.get("role", role)
            except Exception:
                pass

        return {
            "sub": "demo-user-id",
            "email": email,
            "name": name,
            "department": department,
            "role": role,
            "ssp_provider": "government-idp",
        }

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Generate OAuth2 authorization URL."""
        if not self.is_configured() and not self.demo_mode:
            return ""
        if self.is_configured():
            return (
                f"{self.idp_url}/oauth2/authorize"
                f"?response_type=code&client_id={self.client_id}"
                f"&redirect_uri={redirect_uri}&state={state}"
            )
        return ""

    def generate_demo_token(self, email: str, name: str, department: str = "Statistics", role: str = "employee") -> str:
        """Generate a demo JWT token for testing."""
        payload = {
            "sub": f"demo-{email}",
            "email": email,
            "name": name,
            "department": department,
            "role": role,
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": (datetime.now(timezone.utc).timestamp()) + 3600,
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
