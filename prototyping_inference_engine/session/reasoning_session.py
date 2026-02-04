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
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.factory import (
    VariableFactory,
    ConstantFactory,
    LiteralFactory,
    PredicateFactory,
)
from prototyping_inference_engine.api.atom.term.storage import (
    DictStorage,
    WeakRefStorage,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.function_term import FunctionTerm
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
    DlgpeParserProvider,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
    from prototyping_inference_engine.api.formula.formula_builder import FormulaBuilder
    from prototyping_inference_engine.api.query.fo_query import FOQuery
    from prototyping_inference_engine.api.query.query import Query
    from prototyping_inference_engine.api.query.fo_query_factory import FOQueryFactory


class ReasoningSession:
    """
    A scoped reasoning session with managed vocabulary and reasoning capabilities.

    The session provides:
    - Extensible term factory registry (OCP compliant)
    - Factory methods for creating atoms, fact bases, and ontologies
    - DLGPE parsing with term tracking
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
        literal_config: Optional[LiteralConfig] = None,
    ) -> None:
        """
        Initialize a reasoning session.

        Args:
            term_factories: Registry of term factories (must include Variable, Constant, Predicate)
            parser_provider: Provider for parsing content (default: DlgpeParserProvider)
            fact_base_provider: Provider for creating fact bases (default: DefaultFactBaseFactoryProvider)
            rewriting_provider: Provider for rewriting algorithm (default: DefaultRewritingAlgorithmProvider)
        """
        self._term_factories = term_factories
        self._literal_config = literal_config or LiteralConfig.default()

        if Literal not in self._term_factories:
            self._term_factories.register(Literal, LiteralFactory(DictStorage(), self._literal_config))

        self._parser_provider = parser_provider or DlgpeParserProvider(self._term_factories)
        self._fact_base_provider = fact_base_provider or DefaultFactBaseFactoryProvider()
        self._rewriting_provider = rewriting_provider or DefaultRewritingAlgorithmProvider()
        self._python_function_source = None

        if Literal in self._term_factories:
            from prototyping_inference_engine.api.data.python_function_data import PythonFunctionReadable
            literal_factory = self._term_factories.get(Literal)
            self._python_function_source = PythonFunctionReadable(literal_factory)

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
        literal_config: Optional[LiteralConfig] = None,
    ) -> "ReasoningSession":
        """
        Factory method to create a session with default term factories.

        Args:
            auto_cleanup: If True, use WeakRefStorage for automatic cleanup.
                         If False, use DictStorage (manual cleanup via clear).
            parser_provider: Custom parser provider (optional, default: DlgpeParserProvider)
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
            lit_storage = WeakRefStorage()
        else:
            var_storage = DictStorage()
            const_storage = DictStorage()
            pred_storage = DictStorage()
            lit_storage = DictStorage()

        # Create and register standard factories
        factories = TermFactories()
        factories.register(Variable, VariableFactory(var_storage))
        factories.register(Constant, ConstantFactory(const_storage))
        factories.register(Literal, LiteralFactory(lit_storage, literal_config or LiteralConfig.default()))
        factories.register(Predicate, PredicateFactory(pred_storage))

        return cls(
            term_factories=factories,
            parser_provider=parser_provider,
            fact_base_provider=fact_base_provider,
            rewriting_provider=rewriting_provider,
            literal_config=literal_config,
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def term_factories(self) -> TermFactories:
        """Access the term factory registry."""
        return self._term_factories

    @property
    def literal_config(self) -> LiteralConfig:
        """Access the literal configuration for this session."""
        return self._literal_config

    @property
    def python_function_source(self):
        """Access the Python function readable data source."""
        return self._python_function_source

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

    def literal(
        self,
        lexical: str,
        datatype: Optional[str] = None,
        lang: Optional[str] = None,
    ) -> Literal:
        """
        Create or get a literal term.

        Args:
            lexical: The literal lexical form
            datatype: Optional datatype IRI or prefixed name
            lang: Optional language tag

        Returns:
            The Literal instance
        """
        self._check_not_closed()
        return self._term_factories.get(Literal).create(lexical, datatype, lang)

    def register_python_function(
        self,
        name: str,
        func,
        *,
        mode: str = "terms",
        input_arity: Optional[int] = None,
        output_position: Optional[int] = None,
        required_positions: Optional[Iterable[int]] = None,
        min_bound: Optional[int] = None,
        solver=None,
        returns_multiple: bool = False,
    ):
        """
        Register a Python function for computed evaluation.

        Args:
            name: Function name
            func: Callable to execute
            mode: \"terms\" or \"python\"
            input_arity: Number of input arguments
            output_position: Result position (default: last)
            required_positions: Positions that must be bound to evaluate
            min_bound: Minimum number of bound positions
            solver: Optional solver for reversible functions
            returns_multiple: True if func returns an iterable of results
        """
        if self._python_function_source is None:
            raise RuntimeError("Python function source is not available")
        return self._python_function_source.register_function(
            name,
            func,
            mode=mode,
            input_arity=input_arity,
            output_position=output_position,
            required_positions=required_positions,
            min_bound=min_bound,
            solver=solver,
            returns_multiple=returns_multiple,
        )

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

        Uses the configured parser provider (default: DLGPE).
        All terms and predicates are tracked by this session's factories.

        Args:
            text: Text content to parse (format depends on parser provider)

        Returns:
            ParseResult containing facts, rules, queries, constraints, and sources
        """
        self._check_not_closed()

        # Parse different types using the configured parser provider
        facts = list(self._parser_provider.parse_atoms(text))
        rules = set(self._parser_provider.parse_rules(text))
        queries = set(self._parser_provider.parse_queries(text))
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

        sources = self._build_parse_sources(facts, rules, queries, constraints)
        return ParseResult(
            facts=FrozenAtomSet(facts),
            rules=frozenset(rules),
            queries=frozenset(queries),
            constraints=frozenset(constraints),
            sources=tuple(sources),
        )

    def _build_parse_sources(
        self,
        facts: list[Atom],
        rules: set[Rule],
        queries: set["Query"],
        constraints: set[NegativeConstraint],
    ) -> list["ReadableData"]:
        from prototyping_inference_engine.api.atom.predicate import is_comparison_predicate
        from prototyping_inference_engine.api.data.comparison_data import ComparisonDataSource
        from prototyping_inference_engine.api.data.readable_data import ReadableData

        atoms: list[Atom] = list(facts)

        for rule in rules:
            atoms.extend(rule.body.atoms)
            for head in rule.head:
                atoms.extend(head.atoms)

        for query in queries:
            atoms.extend(self._extract_query_atoms(query))

        for constraint in constraints:
            atoms.extend(constraint.body.atoms)

        sources: list[ReadableData] = []
        if any(is_comparison_predicate(atom.predicate) for atom in atoms):
            sources.append(ComparisonDataSource(self._literal_config.comparison))
        if self._python_function_source is not None and _contains_function_term(atoms):
            sources.append(self._python_function_source)
        return sources

    @staticmethod
    def _extract_query_atoms(query: object) -> list[Atom]:
        if hasattr(query, "formula"):
            return list(query.formula.atoms)
        if hasattr(query, "atoms"):
            return list(query.atoms)
        if hasattr(query, "queries"):
            atoms: list[Atom] = []
            for sub in query.queries:
                atoms.extend(ReasoningSession._extract_query_atoms(sub))
            return atoms
        return []

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
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import GenericFOQueryEvaluator
        self._check_not_closed()
        evaluator = GenericFOQueryEvaluator()
        return evaluator.evaluate_and_project(query, fact_base)

    def evaluate_query_with_sources(
        self,
        query: "FOQuery",
        fact_base: "FactBase",
        sources: Iterable["ReadableData"],
    ) -> Iterator[Tuple[Term, ...]]:
        """
        Evaluate a first-order query against a fact base plus extra sources.

        Args:
            query: The FOQuery to evaluate
            fact_base: The fact base to query against
            sources: Extra ReadableData sources to combine with the fact base

        Yields:
            Tuples of terms corresponding to the answer variables
        """
        from prototyping_inference_engine.api.data.collection.builder import ReadableCollectionBuilder
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
            GenericFOQueryEvaluator,
        )

        self._check_not_closed()
        builder = ReadableCollectionBuilder().add_all_predicates_from(fact_base)
        for source in sources:
            builder.add_all_predicates_from(source)
        data = builder.build()
        evaluator = GenericFOQueryEvaluator()
        return evaluator.evaluate_and_project(query, data)

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
            elif isinstance(term, Literal) and Literal in self._term_factories:
                self._term_factories.get(Literal).create(
                    term.lexical or str(term.value), term.datatype, term.lang
                )

    def _track_rule(self, rule: Rule) -> None:
        """Track all terms in a rule."""
        for atom in rule.body.atoms:
            self._track_atom(atom)
        for head_cq in rule.head:
            for atom in head_cq.atoms:
                self._track_atom(atom)

    def _track_query(self, query) -> None:
        """Track all terms in a query."""
        if isinstance(query, UnionQuery):
            for cq in query.conjunctive_queries:
                self._track_query(cq)
            return

        atoms = getattr(query, "atoms", None)
        if atoms is None:
            return

        for atom in atoms:
            self._track_atom(atom)


def _contains_function_term(atoms: Iterable[Atom]) -> bool:
    for atom in atoms:
        for term in atom.terms:
            if _term_contains_function(term):
                return True
    return False


def _term_contains_function(term: Term) -> bool:
    if isinstance(term, FunctionTerm):
        return True
    args = getattr(term, "args", None)
    if args:
        for arg in args:
            if _term_contains_function(arg):
                return True
    return False
