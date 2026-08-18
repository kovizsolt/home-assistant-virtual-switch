from __future__ import annotations

from dataclasses import dataclass

from .const import (
    FIXED_STATUSES,
    STATUS_ERROR,
    STATUS_ONLINE,
    STATUS_UNAVAILABLE,
    STATUS_UNKNOWN,
)


@dataclass(frozen=True)
class StatusDefinition:
    name: str
    available: bool
    is_on: bool | None


FIXED_STATUS_DEFINITIONS = {
    STATUS_ONLINE: StatusDefinition(STATUS_ONLINE, True, None),
    STATUS_UNAVAILABLE: StatusDefinition(STATUS_UNAVAILABLE, False, None),
    STATUS_UNKNOWN: StatusDefinition(STATUS_UNKNOWN, True, None),
    STATUS_ERROR: StatusDefinition(STATUS_ERROR, True, None),
}


def parse_custom_status(value: str) -> StatusDefinition:
    """Parse <name>[:available][:is_on], applying the documented defaults."""
    parts = [part.strip() for part in value.split(":")]
    if not 1 <= len(parts) <= 3 or not parts[0]:
        raise ValueError("expected <name>[:available][:is_on]")

    name = parts[0]
    if name.casefold() in FIXED_STATUSES:
        raise ValueError(f"{name!r} is a reserved status")

    available = True
    if len(parts) >= 2 and parts[1]:
        available = _parse_bool(parts[1], "available")

    is_on: bool | None = None
    if len(parts) == 3 and parts[2]:
        raw_is_on = parts[2].lower()
        if raw_is_on != "none":
            is_on = _parse_bool(raw_is_on, "is_on")

    # An unavailable entity always has HA state "unavailable"; is_on is immaterial.
    return StatusDefinition(name, available, is_on if available else None)


def build_status_definitions(values: list[str]) -> dict[str, StatusDefinition]:
    definitions = dict(FIXED_STATUS_DEFINITIONS)
    normalized_names = {name.casefold() for name in definitions}
    for value in values:
        definition = parse_custom_status(value)
        normalized_name = definition.name.casefold()
        if normalized_name in normalized_names:
            raise ValueError(f"duplicate status {definition.name!r}")
        definitions[definition.name] = definition
        normalized_names.add(normalized_name)
    return definitions


def _parse_bool(value: str, field: str) -> bool:
    normalized = value.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{field} must be true or false")


class VirtualSwitchState:
    """Single source of truth for the simulated device."""

    def __init__(
        self,
        *,
        status: str = STATUS_ONLINE,
        internal_state: bool,
        definitions: dict[str, StatusDefinition] | None = None,
        online: bool | None = None,
    ) -> None:
        self.definitions = definitions or dict(FIXED_STATUS_DEFINITIONS)
        # Keep the old constructor usable for stored-state and test compatibility.
        if online is not None:
            status = STATUS_ONLINE if online else STATUS_UNAVAILABLE
        if status not in self.definitions:
            status = STATUS_ONLINE
        self.status = status
        self.internal_state = internal_state

    @property
    def main_available(self) -> bool:
        return self.definitions[self.status].available

    @property
    def main_is_on(self) -> bool | None:
        if self.status == STATUS_ONLINE:
            return self.internal_state
        return self.definitions[self.status].is_on

    def set_from_main(self, value: bool) -> bool:
        if self.status != STATUS_ONLINE:
            return False
        return self.set_internal(value)

    def set_internal(self, value: bool) -> bool:
        if self.internal_state == value:
            return False
        self.internal_state = value
        return True

    def set_status(self, value: str) -> bool:
        if value not in self.definitions:
            raise ValueError(f"unknown status {value!r}")
        if self.status == value:
            return False
        self.status = value
        return True

    def set_online(self, value: bool) -> bool:
        return self.set_status(STATUS_ONLINE if value else STATUS_UNAVAILABLE)
