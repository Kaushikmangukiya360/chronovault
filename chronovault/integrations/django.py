"""Django backend skeleton for ChronoVault integration."""

from __future__ import annotations

from typing import Any


class DatabaseCreation:  # pragma: no cover - integration skeleton
    pass


class DatabaseIntrospection:  # pragma: no cover - integration skeleton
    pass


class DatabaseOperations:  # pragma: no cover - integration skeleton
    pass


class DatabaseWrapper:  # pragma: no cover - integration skeleton
    """Minimal skeleton compatible with Django backend import expectations."""

    vendor = "chronovault"
    display_name = "ChronoVault"

    def __init__(self, settings_dict: dict[str, Any], alias: str = "default") -> None:
        self.settings_dict = settings_dict
        self.alias = alias
        self.creation = DatabaseCreation()
        self.introspection = DatabaseIntrospection()
        self.ops = DatabaseOperations()

    def get_connection_params(self) -> dict[str, Any]:
        return dict(self.settings_dict)

    def get_new_connection(self, conn_params: dict[str, Any]) -> dict[str, Any]:
        return conn_params

    def init_connection_state(self) -> None:
        return None

    def create_cursor(self, name: str | None = None) -> None:
        _ = name
        return None

    def _set_autocommit(self, autocommit: bool) -> None:
        _ = autocommit
        return None
