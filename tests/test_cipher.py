import pytest

from chronovault.core.cipher import decrypt_json_payload, encrypt_json_payload
from chronovault.exceptions import TamperDetectedError


def test_encrypt_decrypt_roundtrip() -> None:
    envelope = encrypt_json_payload('{"hello":"world"}', "tok", "org", 1710000000, "data")
    plaintext = decrypt_json_payload(envelope, "tok", "org")
    assert plaintext == '{"hello":"world"}'


def test_tamper_detection() -> None:
    envelope = encrypt_json_payload('{"hello":"world"}', "tok", "org", 1710000000, "data")
    envelope["tag"] = "00" * 16
    with pytest.raises(TamperDetectedError):
        decrypt_json_payload(envelope, "tok", "org")
