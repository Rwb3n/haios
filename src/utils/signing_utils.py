from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "utils_signing_utils_py_g238",
    "g_annotation_created": 238,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "A utility for handling Ed25519 digital signatures.",
    "artifact_type": "UTILITY_MODULE_PYTHON",
    "status_in_lifecycle": "PROPOSED",
    "purpose_statement": "To provide a centralized mechanism for creating and verifying detached digital signatures, as per ADR-OS-018.",
    "authors_and_contributors": [{"g_contribution": 238, "identifier": "Roo"}],
    "internal_dependencies": ["core.exceptions"],
    "external_dependencies": [
        {"name": "pynacl", "version_constraint": ">=1.5.0,<2.0.0"}
    ],
    "linked_issue_ids": ["issue_C6_roadmap"]
  }
}
# ANNOTATION_BLOCK_END

from pathlib import Path

from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from core.exceptions import SignatureError

def generate_keypair() -> tuple[str, str]:
    """Generates a new Ed25519 keypair."""
    signing_key = SigningKey.generate()
    return (
        signing_key.encode(encoder=HexEncoder).decode(),
        signing_key.verify_key.encode(encoder=HexEncoder).decode(),
    )

def sign_file(file_path: Path, signing_key_hex: str):
    """Signs a file and saves the signature to a .sig file."""
    signing_key = SigningKey(signing_key_hex.encode(), encoder=HexEncoder)
    with open(file_path, "rb") as f:
        message = f.read()
    signature = signing_key.sign(message).signature
    sig_path = file_path.with_suffix(f"{file_path.suffix}.sig")
    with open(sig_path, "wb") as f:
        f.write(signature)

def verify_file(file_path: Path, verify_key_hex: str):
    """Verifies the signature of a file."""
    verify_key = VerifyKey(verify_key_hex.encode(), encoder=HexEncoder)
    sig_path = file_path.with_suffix(f"{file_path.suffix}.sig")
    if not sig_path.exists():
        raise SignatureError(f"Signature file not found for {file_path}")

    with open(file_path, "rb") as f:
        message = f.read()
    with open(sig_path, "rb") as f:
        signature = f.read()

    try:
        verify_key.verify(message, signature)
    except Exception as e:
        raise SignatureError(f"Signature verification failed for {file_path}") from e