"""
Warnings emitted during FOQuery evaluation.
"""


class UnsafeNegationWarning(UserWarning):
    """Warning emitted when evaluating unsafe negation (free variables in negated formula)."""


class UniversalQuantifierWarning(UserWarning):
    """Warning emitted when evaluating unbounded universal quantification."""
