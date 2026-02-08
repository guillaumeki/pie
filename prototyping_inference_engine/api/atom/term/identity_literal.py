"""
Identity-based literal (no value-based equality).
"""

from prototyping_inference_engine.api.atom.term.literal import Literal


class IdentityLiteral(Literal):
    __eq__ = object.__eq__
    __hash__ = object.__hash__
