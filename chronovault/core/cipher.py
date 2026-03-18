"""AES-256-GCM encryption/decryption wrappers for encrypted JSON files."""

from __future__ import annotations

import os
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from chronovault.core.kde import derive_key
from chronovault.exceptions import TamperDetectedError


def _validate_envelope(envelope: dict[str, Any]) -> None:
    required = {"v", "org_id", "purpose", "ts", "nonce", "tag", "ct"}
    missing = required - set(envelope.keys())
    if missing:
        raise TamperDetectedError("encrypted JSON envelope is missing required fields")
    if envelope.get("v") != 1:
        raise TamperDetectedError("unsupported encrypted JSON version")


def encrypt_json_payload(
    payload_json: str,
    tenant_token: str,
    org_id: str,
    timestamp: int,
    purpose: str,
) -> dict[str, Any]:
    """Encrypt UTF-8 JSON payload into an AES-GCM envelope with hex fields."""
    key = derive_key(tenant_token=tenant_token, org_id=org_id, timestamp=timestamp)
    nonce = os.urandom(12)

    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend(),
    ).encryptor()
    ciphertext = encryptor.update(payload_json.encode("utf-8")) + encryptor.finalize()

    return {
        "v": 1,
        "org_id": org_id,
        "purpose": purpose,
        "ts": int(timestamp),
        "nonce": nonce.hex(),
        "tag": encryptor.tag.hex(),
        "ct": ciphertext.hex(),
    }


def decrypt_json_payload(envelope: dict[str, Any], tenant_token: str, org_id: str) -> str:
    """Decrypt an encrypted JSON envelope and return UTF-8 JSON string."""
    _validate_envelope(envelope)
    if str(envelope.get("org_id")) != org_id:
        raise TamperDetectedError("envelope tenant mismatch")

    ts = int(envelope["ts"])
    key = derive_key(tenant_token=tenant_token, org_id=org_id, timestamp=ts)
    nonce = bytes.fromhex(envelope["nonce"])
    tag = bytes.fromhex(envelope["tag"])
    ciphertext = bytes.fromhex(envelope["ct"])

    try:
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend(),
        ).decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    except (InvalidTag, ValueError, TypeError) as exc:
        raise TamperDetectedError("ciphertext authentication failed") from exc

    try:
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TamperDetectedError("decrypted payload is invalid UTF-8") from exc
