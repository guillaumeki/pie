"""Default trigger applier implementation."""

from __future__ import annotations

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.facts_handler import (
    FactsHandler,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.trigger_renamer import (
    TriggerRenamer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.trigger_applier import (
    TriggerApplier,
)

_LITERAL_FACTORY = LiteralFactory(DictStorage())


class TriggerApplierImpl(TriggerApplier):
    def __init__(self, renamer: TriggerRenamer, facts_handler: FactsHandler):
        self._renamer = renamer
        self._facts_handler = facts_handler

    def apply(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> Formula | None:
        full_substitution = self._renamer.rename_existentials(rule, substitution)
        image_atoms = [
            _materialize_atom(full_substitution.apply(atom)) for atom in rule.head.atoms
        ]
        if not image_atoms:
            return None
        image_formula: Formula = image_atoms[0]
        for atom in image_atoms[1:]:
            image_formula = ConjunctionFormula(image_formula, atom)
        return self._facts_handler.add(image_formula, read_write_data)


def _materialize_atom(atom: Atom) -> Atom:
    return Atom(atom.predicate, *(_materialize_term(term) for term in atom.terms))


def _materialize_term(term: Term) -> Term:
    if isinstance(term, EvaluableFunctionTerm):
        args = tuple(_materialize_term(arg) for arg in term.args)
        if all(arg.is_ground for arg in args):
            evaluated = _evaluate_stdfct(term.name, args)
            if evaluated is not None:
                return evaluated
        return EvaluableFunctionTerm(term.name, args)

    return term


def _evaluate_stdfct(name: str, args: tuple[Term, ...]) -> Term | None:
    if not name.startswith("stdfct:"):
        return None
    try:
        from prototyping_inference_engine.api.data.functions.integraal_standard_functions import (
            _STANDARD_FUNCTIONS,
        )

        fn = _STANDARD_FUNCTIONS.get(name[len("stdfct:") :])
        if fn is None:
            return None
        return fn.evaluator(list(args), _LITERAL_FACTORY)
    except Exception:
        return None
