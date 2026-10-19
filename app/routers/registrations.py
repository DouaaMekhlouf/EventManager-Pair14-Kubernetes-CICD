"""Pure registration business logic (no DB, no HTTP)."""


def has_available_capacity(current_count: int, max_capacity: int) -> bool:
    """True if there is still room for one more registration."""
    return current_count < max_capacity


def check_duplicate_registration(registered_ids, new_id) -> None:
    """Raise ValueError if new_id is already registered."""
    if new_id in registered_ids:
        raise ValueError(f"Participant {new_id} is already registered")
    