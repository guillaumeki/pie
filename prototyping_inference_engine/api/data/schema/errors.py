"""Schema errors."""

from prototyping_inference_engine.api.atom.predicate import Predicate


class IncompatiblePredicateSchemaError(ValueError):
    def __init__(self, predicate: Predicate, message: str):
        super().__init__(
            f"Incompatible schemas for predicate {predicate}/{predicate.arity}: {message}"
        )
        self.predicate = predicate
