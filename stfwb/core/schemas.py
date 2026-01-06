"""Shared typing schemas for JSON-like payloads used by models.

Avoid recursive aliases that require Pydantic forward-ref rebuilding.
Use `JsonObject` as a coarse but safe mapping type instead of `Any`.
"""

# Coarse JSON object mapping; narrows `Any` to `object` for strict typing
JsonObject = dict[str, object]

__all__ = ["JsonObject"]
