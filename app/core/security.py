from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings

PBKDF2_ITERATIONS = 390000
JWT_ALGORITHM = "RS256"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}")


def _int_to_base64(value: int) -> str:
    length = max(1, (value.bit_length() + 7) // 8)
    return _b64url_encode(value.to_bytes(length, "big"))


def _generate_rsa_key_pair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


def _normalize_pem(value: str) -> str:
    return value.replace("\\n", "\n").strip()


def _load_signing_keys() -> tuple[str, str]:
    if settings.rsa_private_key and settings.rsa_public_key:
        return _normalize_pem(settings.rsa_private_key), _normalize_pem(settings.rsa_public_key)
    return _generate_rsa_key_pair()


PRIVATE_KEY_PEM, PUBLIC_KEY_PEM = _load_signing_keys()


def hash_secret(secret: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_secret(secret: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = _b64url_decode(salt_b64)
        expected_digest = _b64url_decode(digest_b64)
        computed_digest = hashlib.pbkdf2_hmac(
            "sha256",
            secret.encode("utf-8"),
            salt,
            int(iterations_str),
        )
        return hmac.compare_digest(computed_digest, expected_digest)
    except (TypeError, ValueError):
        return False


def create_access_token(
    *,
    subject: str,
    audience: str,
    tenant_id: int,
    roles: list[str],
    custom_attributes: dict[str, Any],
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> tuple[str, int]:
    now = datetime.now(UTC)
    expiration = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))

    payload: dict[str, Any] = {
        "iss": settings.issuer,
        "sub": subject,
        "aud": audience,
        "tenant_id": tenant_id,
        "roles": roles,
        "custom_attributes": custom_attributes,
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp()),
    }
    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(
        payload,
        PRIVATE_KEY_PEM,
        algorithm=JWT_ALGORITHM,
        headers={"kid": settings.rsa_key_id},
    )
    return token, int((expiration - now).total_seconds())


def get_jwks() -> dict[str, list[dict[str, str]]]:
    public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM.encode("utf-8"))
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise ValueError("La llave pública configurada no es RSA")

    numbers = public_key.public_numbers()
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "kid": settings.rsa_key_id,
        "alg": JWT_ALGORITHM,
        "n": _int_to_base64(numbers.n),
        "e": _int_to_base64(numbers.e),
    }
    return {"keys": [jwk]}



