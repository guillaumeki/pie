"""
ReasoningSession - Main class for scoped reasoning sessions.

Provides a session context for reasoning with managed vocabulary,
fact bases, ontologies, and query rewriting.
"""
from math import inf
from typing import Optional, Iterable, Iterator, Tuple, Union, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.factory import (
    VariableFactory,
    ConstantFactory,
    PredicateFactory,
)
from prototyping_inference_engine.api.atom.term.storage import (
    DictStorage,
    WeakRefStorage,
)
from prototyping_inference_engine.api.ontology.ontology import Ontology
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.session.cleanup_stats import SessionCleanupStats
from prototyping_inference_engine.session.parse_result import ParseResult
from prototyping_inference_engine.session.term_factories import TermFactories
from prototyping_inference_engine.session.providers import (
    FactBaseFactoryProvider,
    RewritingAlgorithmProvider,
    ParserProvider,
    DefaultFactBaseFactoryProvider,
    DefaultRewritingAlgorithmProvider,
    Dlgp2ParserProvider,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
    from prototyping_inference_engine.api.formula.formula_builder import FormulaBuilder
    from prototyping_inference_engine.api.query.fo_query import FOQuery
    from prototyping_inference_engine.api.query.fo_query_factory import FOQueryFactory


class ReasoningSession:
    """
    A scoped reasoning session with managed vocabulary and reasoning capabilities.

    The session provides:
    - Extensible term factory registry (OCP compliant)
    - Factory methods for creating atoms, fact bases, and ontologies
    - DLGP parsing with term tracking
    - UCQ rewriting
    - Context manager support for automatic cleanup

    Example usage:
        # Simple usage with defaults
        with ReasoningSession.create(auto_cleanup=True) as session:
            result = session.parse("p(a,b). q(X) :- p(X,Y).")
            x = session.variable("X")
            rewritten = session.rewrite(result.queries.pop(), result.rules)

        # Advanced usage with custom factories
        factories = TermFactories()
        factories.register(Variable, VariableFactory(custom_storage))
        factories.register(Constant, ConstantFactory(custom_storage))
        factories.register(Predicate, PredicateFactory(custom_storage))

        session = ReasoningSession(term_factories=factories)
    """

    def __init__(
        self,
        term_factories: TermFactories,
        parser_provider: Optional[ParserProvider] = None,
        fact_base_provider: Optional[FactBaseFactoryProvider] = None,
        rewriting_provider: Optional[RewritingAlgorithmProvider] = None,
    ) -> None:
        """
        Initialize a reasoning session.

        Args:
            term_factories: Registry of term factories (must include Variable, Constant, Predicate)
            parser_provider: Provider for parsing content (default: Dlgp2ParserProvider)
            fact_base_provider: Provider for creating fact bases (default: DefaultFactBaseFactoryProvider)
            rewriting_provider: Provider for rewriting algorithm (default: DefaultRewritingAlgorithmProvider)
        """
        self._term_factories = term_factories
        self._parser_provider = parser_provider or Dlgp2ParserProvider()
        self._fact_base_provider = fact_base_provider or DefaultFactBaseFactoryProvider()
        self._rewriting_provider = rewriting_provider or DefaultRewritingAlgorithmProvider()

        # Session-owned resources
        self._fact_bases: list["FactBase"] = []
        self._ontologies: list[Ontology] = []
        self._closed = False

    @classmethod
    def create(
        cls,
        auto_cleanup: bool = True,
        parser_provider: Optional[ParserProvider] = None,
        fact_base_provider: Optional[FactBaseFactoryProvider] = None,
        rewriting_provider: Optional[RewritingAlgorithmProvider] = None,
    ) -> "ReasoningSession":
        """
        Factory method to create a session with default term factories.

        Args:
            auto_cleanup: If True, use WeakRefStorage for automatic cleanup.
                         If False, use DictStorage (manual cleanup via clear).
            parser_provider: Custom parser provider (optional, default: Dlgp2ParserProvider)
            fact_base_provider: Custom fact base provider (optional)
            rewriting_provider: Custom rewriting provider (optional)

        Returns:
            A new ReasoningSession with standard term factories configured
        """
        # Choose storage strategy based on auto_cleanup
        if auto_cleanup:
            var_storage = WeakRefStorage()
            const_storage = WeakRefStorage()
            pred_storage = WeakRefStorage()
        else:
            var_storage = DictStorage()
            const_storage = DictStorage()
            pred_storage = DictStorage()

        # Create and register standard factories
        factories = TermFactories()
        factories.register(Variable, VariableFactory(var_storage))
        factories.register(Constant, ConstantFactory(const_storage))
        factories.register(Predicate, PredicateFactory(pred_storage))

        return cls(
            term_factories=factories,
            parser_provider=parser_provider,
            fact_base_provider=fact_base_provider,
            rewriting_provider=rewriting_provider,
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def term_factories(self) -> TermFactories:
        """Access the term factory registry."""
        return self._term_factories

    @property
    def fact_bases(self) -> list["FactBase"]:
        """Return a copy of the list of fact bases created in this session."""
        return list(self._fact_bases)

    @property
    def ontologies(self) -> list[Ontology]:
        """Return a copy of the list of ontologies created in this session."""
        return list(self._ontologies)

    @property
    def is_closed(self) -> bool:
        """Return True if the session has been closed."""
        return self._closed

    # =========================================================================
    # Term creation convenience methods
    # =========================================================================

    def variable(self, identifier: str) -> Variable:
        """
        Create or get a variable.

        Args:
            identifier: The variable identifier (e.g., "X", "Y")

        Returns:
            The Variable instance
        """
        self._check_not_closed()
        return self._term_factories.get(Variable).create(identifier)

    def constant(self, identifier: object) -> Constant:
        """
        Create or get a constant.

        Args:
            identifier: The constant identifier (e.g., "a", 42)

        Returns:
            The Constant instance
        """
        self._check_not_closed()
        return self._term_factories.get(Constant).create(identifier)

    def predicate(self, name: str, arity: int) -> Predicate:
        """
        Create or get a predicate.

        Args:
            name: The predicate name (e.g., "p", "parent")
            arity: The number of arguments

        Returns:
            The Predicate instance
        """
        self._check_not_closed()
        return self._term_factories.get(Predicate).create(name, arity)

    def fresh_variable(self) -> Variable:
        """
        Create a fresh variable with a unique identifier.

        Returns:
            A new Variable with a unique identifier
        """
        self._check_not_closed()
        return self._term_factories.get(Variable).fresh()

    def atom(self, predicate: Predicate, *terms: Term) -> Atom:
        """
        Create an atom with the given predicate and terms.

        Args:
            predicate: The predicate
            *terms: The terms (variables or constants)

        Returns:
            A new Atom instance
        """
        self._check_not_closed()
        return Atom(predicate, *terms)

    def formula(self) -> "FormulaBuilder":
        """
        Create a formula builder for constructing first-order formulas.

        Returns:
            A new FormulaBuilder bound to this session

        Example:
            formula = (session.formula()
                .forall("X")
                .exists("Y")
                .atom("p", "X", "Y")
                .and_()
                .atom("q", "Y")
                .build())
        """
        from prototyping_inference_engine.api.formula.formula_builder import FormulaBuilder
        self._check_not_closed()
        return FormulaBuilder(self)

    def fo_query(self) -> "FOQueryFactory":
        """
        Create a factory for constructing first-order queries.

        Returns:
            A new FOQueryFactory bound to this session

        Example using builder:
            query = (session.fo_query().builder()
                .answer("X")
                .exists("Y")
                .atom("p", "X", "Y")
                .and_()
                .atom("q", "Y")
                .build())
            # Result: ?(X) :- ∃Y.(p(X,Y) ∧ q(Y))

        Example from formula:
            formula = session.formula().atom("p", "X", "Y").build()
            query = session.fo_query().from_formula(formula, ["X"])
        """
        from prototyping_inference_engine.api.query.fo_query_factory import FOQueryFactory
        self._check_not_closed()
        return FOQueryFactory(self)

    # =========================================================================
    # Factory methods for complex objects
    # =========================================================================

    def create_fact_base(
        self, atoms: Optional[Iterable[Atom]] = None
    ) -> "MutableInMemoryFactBase":
        """
        Create a mutable fact base and register it with the session.

        Args:
            atoms: Optional initial atoms

        Returns:
            A new mutable fact base
        """
        self._check_not_closed()
        fb = self._fact_base_provider.create_mutable(atoms)
        self._fact_bases.append(fb)
        return fb

    def create_ontology(
        self,
        rules: Optional[set[Rule]] = None,
        constraints: Optional[set[NegativeConstraint]] = None,
    ) -> Ontology:
        """
        Create an ontology and register it with the session.

        Args:
            rules: Optional set of rules
            constraints: Optional set of negative constraints

        Returns:
            A new Ontology instance
        """
        self._check_not_closed()
        onto = Ontology(rules, constraints)
        self._ontologies.append(onto)
        return onto

    # =========================================================================
    # Parsing methods
    # =========================================================================

    def parse(self, text: str) -> ParseResult:
        """
        Parse text content and return structured results.

        Uses the configured parser provider (default: DLGP2).
        All terms and predicates are tracked by this session's factories.

        Args:
            text: Text content to parse (format depends on parser provider)

        Returns:
            ParseResult containing facts, rules, queries, and constraints
        """
        self._check_not_closed()

        # Parse different types using the configured parser provider
        facts = list(self._parser_provider.parse_atoms(text))
        rules = set(self._parser_provider.parse_rules(text))
        cqs = set(self._parser_provider.parse_conjunctive_queries(text))
        ucqs = set(self._parser_provider.parse_union_conjunctive_queries(text))
        queries = cqs | ucqs
        constraints = set(self._parser_provider.parse_negative_constraints(text))

        # Track all terms and predicates
        for atom in facts:
            self._track_atom(atom)
        for rule in rules:
            self._track_rule(rule)
        for query in queries:
            self._track_query(query)
        for constraint in constraints:
            self._track_query(constraint.body)

        return ParseResult(
            facts=FrozenAtomSet(facts),
            rules=frozenset(rules),
            queries=frozenset(queries),
            constraints=frozenset(constraints),
        )

    def parse_file(self, file_path: str) -> ParseResult:
        """
        Parse a DLGP file and return structured results.

        Args:
            file_path: Path to the DLGP file

        Returns:
            ParseResult containing facts, rules, queries, and constraints
        """
        self._check_not_closed()
        with open(file_path, "r") as f:
            return self.parse(f.read())

    # =========================================================================
    # Reasoning methods
    # =========================================================================

    def rewrite(
        self,
        query: Union[ConjunctiveQuery, UnionQuery[ConjunctiveQuery]],
        rules: set[Rule],
        step_limit: float = inf,
        verbose: bool = False,
    ) -> UnionQuery[ConjunctiveQuery]:
        """
        Perform UCQ rewriting.

        Args:
            query: The query to rewrite (CQ or UCQ)
            rules: The rules to use for rewriting
            step_limit: Maximum number of rewriting steps (default: unlimited)
            verbose: Whether to print progress

        Returns:
            The rewritten union of conjunctive queries
        """
        self._check_not_closed()

        # Convert CQ to UCQ if needed
        if isinstance(query, ConjunctiveQuery):
            query = UnionQuery(
                frozenset([query]),
                query.answer_variables,
                query.label,
            )

        algorithm = self._rewriting_provider.get_algorithm()
        return algorithm.rewrite(query, rules, step_limit, verbose)

    def evaluate_query(
        self,
        query: "FOQuery",
        fact_base: "FactBase",
    ) -> Iterator[Tuple[Term, ...]]:
        """
        Evaluate a first-order query against a fact base.

        Args:
            query: The FOQuery to evaluate
            fact_base: The fact base to query against

        Yields:
            Tuples of terms corresponding to the answer variables

        Example:
            query = (session.fo_query().builder()
                .answer("X")
                .atom("p", "a", "X")
                .build())
            for answer in session.evaluate_query(query, fact_base):
                print(answer)  # (b,), (c,), ...
        """
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluators import GenericFOQueryEvaluator
        self._check_not_closed()
        evaluator = GenericFOQueryEvaluator()
        return evaluator.evaluate_and_project(query, fact_base)

    # =========================================================================
    # Lifecycle methods
    # =========================================================================

    def cleanup(self) -> SessionCleanupStats:
        """
        Trigger cleanup of tracked terms.

        For WeakRefStorage, this forces garbage collection.
        For DictStorage, this clears all tracked items.

        Returns:
            Statistics about items removed
        """
        self._check_not_closed()
        import gc

        vars_before = 0
        consts_before = 0
        preds_before = 0

        # Get counts before cleanup
        if Variable in self._term_factories:
            vars_before = len(self._term_factories.get(Variable))
        if Constant in self._term_factories:
            consts_before = len(self._term_factories.get(Constant))
        if Predicate in self._term_factories:
            preds_before = len(self._term_factories.get(Predicate))

        # Force garbage collection
        gc.collect()

        # Get counts after cleanup
        vars_after = 0
        consts_after = 0
        preds_after = 0

        if Variable in self._term_factories:
            vars_after = len(self._term_factories.get(Variable))
        if Constant in self._term_factories:
            consts_after = len(self._term_factories.get(Constant))
        if Predicate in self._term_factories:
            preds_after = len(self._term_factories.get(Predicate))

        return SessionCleanupStats(
            variables_removed=vars_before - vars_after,
            constants_removed=consts_before - consts_after,
            predicates_removed=preds_before - preds_after,
        )

    def close(self) -> None:
        """
        Close the session and release resources.

        After closing, no operations can be performed on this session.
        """
        if self._closed:
            return

        # Clear storage in all factories
        for term_type in self._term_factories:
            factory = self._term_factories.get(term_type)
            if hasattr(factory, '_storage'):
                factory._storage.clear()

        self._fact_bases.clear()
        self._ontologies.clear()
        self._closed = True

    # =========================================================================
    # Context manager
    # =========================================================================

    def __enter__(self) -> "ReasoningSession":
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and close the session."""
        self.close()

    # =========================================================================
    # Private helpers
    # =========================================================================

    def _check_not_closed(self) -> None:
        """Raise an error if the session is closed."""
        if self._closed:
            raise RuntimeError("Cannot perform operations on a closed session")

    def _track_atom(self, atom: Atom) -> None:
        """Track all terms and predicate in an atom."""
        # Track predicate
        if Predicate in self._term_factories:
            self._term_factories.get(Predicate).create(
                atom.predicate.name, atom.predicate.arity
            )

        # Track terms
        for term in atom.terms:
            if isinstance(term, Variable) and Variable in self._term_factories:
                self._term_factories.get(Variable).create(str(term.identifier))
            elif isinstance(term, Constant) and Constant in self._term_factories:
                self._term_factories.get(Constant).create(term.identifier)

    def _track_rule(self, rule: Rule) -> None:
        """Track all terms in a rule."""
        for atom in rule.body.atoms:
            self._track_atom(atom)
        for head_cq in rule.head:
            for atom in head_cq.atoms:
                self._track_atom(atom)

    def _track_query(
        self, query: Union[ConjunctiveQuery, UnionQuery[ConjunctiveQuery]]
    ) -> None:
        """Track all terms in a query."""
        if isinstance(query, ConjunctiveQuery):
            for atom in query.atoms:
                self._track_atom(atom)
        elif isinstance(query, UnionQuery):
            for cq in query.conjunctive_queries:
                self._track_query(cq)
