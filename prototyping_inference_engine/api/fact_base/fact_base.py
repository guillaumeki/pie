"""
FactBase - materialized data source for the inference engine.
"""

from prototyping_inference_engine.api.data.materialized_data import MaterializedData


class UnsupportedFactBaseOperation(Exception):
    def __init__(self, operation, msg=None, *args):
        if not msg:
            msg = (
                "The operation "
                + operation.__name__
                + " is unsupported on this fact base"
            )
        super().__init__(msg, *args)


class FactBase(MaterializedData):
    """
    Abstract base class for fact bases.

    A fact base is a materialized data source where all atoms are
    available in memory. Use FOQueryEvaluator for query evaluation.
    """

    pass
