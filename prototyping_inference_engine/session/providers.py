"""
Provider protocols and default implementations for ReasoningSession dependencies.

Providers enable dependency injection following the DIP (Dependency Inversion Principle),
allowing different implementations to be injected for testing or custom behavior.
"""

from typing import Protocol, runtime_checkable, Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
        FrozenInMemoryFactBase,
    )
    from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
        MutableInMemoryFactBase,
    )
    from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import (
        BreadthFirstRewriting,
    )
    from prototyping_inference_engine.api.ontology.rule.rule import Rule
    from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
        NegativeConstraint,
    )
    from prototyping_inference_engine.api.query.conjunctive_query import (
        ConjunctiveQuery,
    )
    from prototyping_inference_engine.api.query.query import Query
    from prototyping_inference_engine.api.query.union_conjunctive_queries import (
        UnionConjunctiveQueries,
    )


@runtime_checkable
class FactBaseFactoryProvider(Protocol):
    """
    Protocol for creating fact bases within a session.

    Implementations determine how fact bases are instantiated,
    enabling custom storage backends or testing doubles.
    """

    def create_mutable(
        self, atoms: Optional[Iterable["Atom"]] = None
    ) -> "MutableInMemoryFactBase":
        """
        Create a mutable fact base.

        Args:
            atoms: Optional initial atoms to populate the fact base

        Returns:
            A new mutable fact base instance
        """
        ...

    def create_frozen(
        self, atoms: Optional[Iterable["Atom"]] = None
    ) -> "FrozenInMemoryFactBase":
        """
        Create a frozen (immutable) fact base.

        Args:
            atoms: Optional atoms to populate the fact base

        Returns:
            A new frozen fact base instance
        """
        ...


@runtime_checkable
class RewritingAlgorithmProvider(Protocol):
    """
    Protocol for providing the UCQ rewriting algorithm.

    Implementations determine which rewriting algorithm is used,
    enabling different strategies or testing doubles.
    """

    def get_algorithm(self) -> "BreadthFirstRewriting":
        """
        Get the rewriting algorithm instance.

        Returns:
            A rewriting algorithm instance
        """
        ...


class DefaultFactBaseFactoryProvider:
    """
    Default implementation delegating to FactBaseFactory.

    Uses the existing FactBaseFactory for creating fact bases,
    maintaining compatibility with the current codebase.
    """

    def create_mutable(
        self, atoms: Optional[Iterable["Atom"]] = None
    ) -> "MutableInMemoryFactBase":
        """
        Create a mutable fact base using FactBaseFactory.

        Args:
            atoms: Optional initial atoms to populate the fact base

        Returns:
            A new mutable fact base instance
        """
        from prototyping_inference_engine.api.fact_base.factory import FactBaseFactory

        return FactBaseFactory.create_mutable(atoms)

    def create_frozen(
        self, atoms: Optional[Iterable["Atom"]] = None
    ) -> "FrozenInMemoryFactBase":
        """
        Create a frozen fact base using FactBaseFactory.

        Args:
            atoms: Optional atoms to populate the fact base

        Returns:
            A new frozen fact base instance
        """
        from prototyping_inference_engine.api.fact_base.factory import FactBaseFactory

        return FactBaseFactory.create_frozen(atoms)


class DefaultRewritingAlgorithmProvider:
    """
    Default implementation returning BreadthFirstRewriting.

    Uses the standard breadth-first rewriting algorithm.
    """

    def get_algorithm(self) -> "BreadthFirstRewriting":
        """
        Get a BreadthFirstRewriting instance.

        Returns:
            A new BreadthFirstRewriting instance
        """
        from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import (
            BreadthFirstRewriting,
        )

        return BreadthFirstRewriting()


@runtime_checkable
class ParserProvider(Protocol):
    """
    Protocol for parsing knowledge base content.

    Implementations determine how text content is parsed into
    atoms, rules, queries, and constraints. This enables support
    for different input formats (DLGP, RDF, OWL, etc.) without
    modifying the ReasoningSession class (OCP compliance).
    """

    def parse_atoms(self, text: str) -> Iterable["Atom"]:
        """
        Parse atoms (facts) from text.

        Args:
            text: The text content to parse

        Returns:
            An iterable of parsed Atom instances
        """
        ...

    def parse_rules(self, text: str) -> Iterable["Rule"]:
        """
        Parse rules from text.

        Args:
            text: The text content to parse

        Returns:
            An iterable of parsed Rule instances
        """
        ...

    def parse_conjunctive_queries(self, text: str) -> Iterable["ConjunctiveQuery"]:
        """
        Parse conjunctive queries from text.

        Args:
            text: The text content to parse

        Returns:
            An iterable of parsed ConjunctiveQuery instances
        """
        ...

    def parse_queries(self, text: str) -> Iterable["Query"]:
        """
        Parse queries from text.

        Args:
            text: The text content to parse

        Returns:
            An iterable of parsed Query instances
        """
        ...

    def parse_union_conjunctive_queries(
        self, text: str
    ) -> Iterable["UnionConjunctiveQueries"]:
        """
        Parse union of conjunctive queries from text.

        Args:
            text: The text content to parse

        Returns:
            An iterable of parsed UnionConjunctiveQueries instances
        """
        ...

    def parse_negative_constraints(self, text: str) -> Iterable["NegativeConstraint"]:
        """
        Parse negative constraints from text.

        Args:
            text: The text content to parse

        Returns:
            An iterable of parsed NegativeConstraint instances
        """
        ...


class Dlgp2ParserProvider:
    """
    Default parser provider using DLGP2 format.

    Delegates to the existing Dlgp2Parser for parsing DLGP format content.
    """

    def __init__(self, term_factories=None) -> None:
        self._term_factories = term_factories

    def _parser(self):
        from prototyping_inference_engine.api.atom.term.literal import Literal
        from prototyping_inference_engine.io.parsers.dlgp.dlgp2_parser import (
            Dlgp2Parser,
        )
        from prototyping_inference_engine.io.parsers.dlgp.dlgp2_transformer import (
            Dlgp2Transformer,
        )

        if self._term_factories and Literal in self._term_factories:
            literal_factory = self._term_factories.get(Literal)
            return Dlgp2Parser.create(Dlgp2Transformer(literal_factory))
        return Dlgp2Parser.instance()

    def parse_atoms(self, text: str) -> Iterable["Atom"]:
        """Parse atoms from DLGP text."""
        return self._parser().parse_atoms(text)

    def parse_rules(self, text: str) -> Iterable["Rule"]:
        """Parse rules from DLGP text."""
        return self._parser().parse_rules(text)

    def parse_conjunctive_queries(self, text: str) -> Iterable["ConjunctiveQuery"]:
        """Parse conjunctive queries from DLGP text."""
        return self._parser().parse_conjunctive_queries(text)

    def parse_queries(self, text: str) -> Iterable["Query"]:
        """Parse queries from DLGP text."""
        parser = self._parser()
        yield from parser.parse_conjunctive_queries(text)
        yield from parser.parse_union_conjunctive_queries(text)

    def parse_union_conjunctive_queries(
        self, text: str
    ) -> Iterable["UnionConjunctiveQueries"]:
        """Parse union of conjunctive queries from DLGP text."""
        return self._parser().parse_union_conjunctive_queries(text)

    def parse_negative_constraints(self, text: str) -> Iterable["NegativeConstraint"]:
        """Parse negative constraints from DLGP text."""
        return self._parser().parse_negative_constraints(text)

    def parse_document(self, text: str) -> dict:
        """Parse a full DLGP document and return header + body."""
        return self._parser().parse(text)


class DlgpeParserProvider:
    """
    Default parser provider using DLGPE format.

    Delegates to the existing DlgpeParser for parsing DLGPE format content.
    """

    def __init__(self, term_factories=None) -> None:
        self._term_factories = term_factories

    def _transformer(self):
        from prototyping_inference_engine.api.atom.term.literal import Literal
        from prototyping_inference_engine.io.parsers.dlgpe.dlgpe_transformer import (
            DlgpeTransformer,
        )

        if self._term_factories and Literal in self._term_factories:
            literal_factory = self._term_factories.get(Literal)
            return DlgpeTransformer(literal_factory)
        return DlgpeTransformer()

    def parse_atoms(self, text: str) -> Iterable["Atom"]:
        """Parse atoms from DLGPE text."""
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

        return DlgpeParser.instance().parse_atoms(text, self._transformer())

    def parse_rules(self, text: str) -> Iterable["Rule"]:
        """Parse rules from DLGPE text."""
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

        return DlgpeParser.instance().parse_rules(text, self._transformer())

    def parse_conjunctive_queries(self, text: str) -> Iterable["ConjunctiveQuery"]:
        """Parse conjunctive queries from DLGPE text when possible."""
        from prototyping_inference_engine.api.query.conjunctive_query import (
            ConjunctiveQuery,
        )
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
        from prototyping_inference_engine.io.parsers.dlgpe.conversions import (
            try_convert_fo_query,
        )

        for query in DlgpeParser.instance().parse_queries(text, self._transformer()):
            converted = try_convert_fo_query(query)
            if isinstance(converted, ConjunctiveQuery):
                yield converted

    def parse_queries(self, text: str) -> Iterable["Query"]:
        """Parse queries from DLGPE text."""
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

        return DlgpeParser.instance().parse_queries(text, self._transformer())

    def parse_union_conjunctive_queries(
        self, text: str
    ) -> Iterable["UnionConjunctiveQueries"]:
        """Parse UCQs from DLGPE text when possible."""
        from prototyping_inference_engine.api.query.union_conjunctive_queries import (
            UnionConjunctiveQueries,
        )
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
        from prototyping_inference_engine.io.parsers.dlgpe.conversions import (
            try_convert_fo_query,
        )

        for query in DlgpeParser.instance().parse_queries(text, self._transformer()):
            converted = try_convert_fo_query(query)
            if isinstance(converted, UnionConjunctiveQueries):
                yield converted

    def parse_negative_constraints(self, text: str) -> Iterable["NegativeConstraint"]:
        """Parse negative constraints from DLGPE text."""
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

        return DlgpeParser.instance().parse_constraints(text, self._transformer())

    def parse_document(self, text: str) -> dict:
        """Parse a full DLGPE document and return header + statements."""
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

        return DlgpeParser.instance().parse(text, self._transformer())
