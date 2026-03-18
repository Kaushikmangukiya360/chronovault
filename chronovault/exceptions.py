"""Custom exceptions for chronovault."""

from __future__ import annotations


class VaultError(Exception):
    """Base exception for all ChronoVault errors."""


class AuthenticationError(VaultError):
    """Raised when token authentication fails."""


class UnauthorizedIPError(VaultError):
    """Raised when source IP is not in token allowlist."""


class PermissionDeniedError(VaultError):
    """Raised when token role lacks required permission."""


class TokenExpiredError(VaultError):
    """Raised when a token or link has expired."""


class TokenRevokedError(VaultError):
    """Raised when a revoked token is used."""


class CollectionNotFoundError(VaultError):
    """Raised when a collection does not exist."""


class RecordNotFoundError(VaultError):
    """Raised when a target record cannot be found."""


class VaultLockTimeoutError(VaultError):
    """Raised when file lock acquisition exceeds timeout."""


class TamperDetectedError(VaultError):
    """Raised when ciphertext authenticity verification fails."""


class AuditIntegrityError(VaultError):
    """Raised when audit chain hash verification fails."""


class TenantNotFoundError(VaultError):
    """Raised when tenant metadata cannot be located."""


class TenantAlreadyExistsError(VaultError):
    """Raised when attempting to create an existing tenant."""


class InvalidTokenError(VaultError):
    """Raised when token format or metadata is invalid."""


class SchemaValidationError(VaultError):
    """Raised when record data violates collection schema constraints."""


class IndexAlreadyExistsError(VaultError):
    """Raised when trying to create an index that already exists."""


class IndexNotFoundError(VaultError):
    """Raised when trying to access or delete a missing index."""


class UniqueConstraintError(VaultError):
    """Raised when a unique index detects duplicate values."""


class TransactionError(VaultError):
    """Raised for generic transaction processing failures."""


class TransactionConflictError(VaultError):
    """Raised when serializable transaction conflicts are detected."""


class ShardError(VaultError):
    """Raised when shard read/write/split operations fail."""


class MigrationError(VaultError):
    """Raised for migration registration or execution failures."""


class BackupError(VaultError):
    """Raised when encrypted backup export fails."""


class RestoreError(VaultError):
    """Raised when encrypted backup import or restore fails."""


class QueryError(VaultError):
    """Raised for invalid query syntax or unsupported operators."""


class FullTextSearchError(VaultError):
    """Raised when full-text search indexing/querying fails."""


class ServerConnectionError(VaultError):
    """Raised when daemon/server mode communication fails."""
