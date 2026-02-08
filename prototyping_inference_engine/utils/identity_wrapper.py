"""
Identity-based wrapper for objects with value-based equality.
"""


class IdentityWrapper:
    def __init__(self, value: object):
        self._value = value

    @property
    def value(self) -> object:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IdentityWrapper):
            return False
        return self._value is other._value

    def __hash__(self) -> int:
        return id(self._value)

    def __repr__(self) -> str:
        return f"IdentityWrapper({self._value!r})"
