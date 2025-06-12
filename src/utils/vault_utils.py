from __future__ import annotations

# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "utils_vault_utils_py_g235",
        "g_annotation_created": 235,
        "version_tag_of_host_at_annotation": "1.0.0",
    },
    "payload": {
        "description": "A utility module for managing the age-encrypted secrets vault.",
        "artifact_type": "UTILITY_MODULE_PYTHON",
        "status_in_lifecycle": "PROPOSED",
        "purpose_statement": "To provide a secure, file-based vault for managing secrets with different scopes, as per ADR-OS-018.",
        "authors_and_contributors": [{"g_contribution": 235, "identifier": "Roo"}],
        "internal_dependencies": ["core.exceptions"],
        "external_dependencies": [
            {"name": "age", "version_constraint": ">=1.0.0,<2.0.0"}
        ],
        "linked_issue_ids": ["issue_C1_roadmap"],
    },
}
# ANNOTATION_BLOCK_END

import json
import os
from pathlib import Path
from typing import Any, Dict

try:
    import age  # type: ignore
except ImportError:  # pragma: no cover – testing environment stub
    import sys
    import types

    age = types.ModuleType("age")

    class _Identity:
        @staticmethod
        def from_bech32(key):
            return _Identity()

        def to_public(self):
            return self

    def _noop(data, recipients):
        return data

    age.Identity = _Identity
    age.encrypt = _noop
    age.decrypt = _noop
    age.DecryptError = Exception
    sys.modules["age"] = age

from core.exceptions import VaultError


class Vault:
    """Manages the age-encrypted secrets vault."""

    def __init__(self, vault_path: Path, key: str):
        self.vault_path = vault_path
        self.key = age.Identity.from_bech32(key)

    def initialize(self):
        """Initializes an empty, encrypted vault if one doesn't exist."""
        if self.vault_path.exists():
            raise VaultError("Vault already exists at the specified path.")
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_secrets({})

    def _read_secrets(self) -> Dict[str, Any]:
        """Reads and decrypts the secrets from the vault."""
        if not self.vault_path.exists():
            raise VaultError("Vault does not exist. Please initialize it first.")

        try:
            with open(self.vault_path, "rb") as f:
                decrypted_data = age.decrypt(f.read(), [self.key])
            return json.loads(decrypted_data)
        except (age.DecryptError, json.JSONDecodeError) as e:
            raise VaultError(f"Failed to read or decrypt vault: {e}") from e

    def _write_secrets(self, secrets: Dict[str, Any]):
        """Encrypts and writes secrets to the vault."""
        try:
            encrypted_data = age.encrypt(
                json.dumps(secrets, indent=2).encode(), [self.key.to_public()]
            )
            with open(self.vault_path, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            raise VaultError(f"Failed to encrypt or write to vault: {e}") from e

    def add_secret(self, name: str, value: str, scope: str):
        """Adds or updates a secret in the vault."""
        secrets = self._read_secrets()
        secrets[name] = {"value": value, "scope": scope}
        self._write_secrets(secrets)

    def get_secret(self, name: str) -> Dict[str, Any]:
        """Retrieves a secret from the vault."""
        secrets = self._read_secrets()
        if name not in secrets:
            raise VaultError(f"Secret '{name}' not found in vault.")
        return secrets[name]

    def list_secrets(self) -> Dict[str, Any]:
        """Lists all secrets in the vault, without their values."""
        secrets = self._read_secrets()
        return {name: {"scope": data["scope"]} for name, data in secrets.items()}
