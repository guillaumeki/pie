"""
Shared evaluator errors.
"""


class UnsupportedFormulaError(Exception):
    """Raised when no evaluator is registered for a formula type."""

    def __init__(self, formula_type: type):
        self.formula_type = formula_type
        super().__init__(
            f"No evaluator registered for formula type: {formula_type.__name__}"
        )
