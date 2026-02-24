"""
DLGPE Parser - Parser for the DLGPE language.

DLGPE (Datalog+- Grammar for Positive Existential rules) is an extended
version of DLGP that supports additional features like negation, disjunction
in rule bodies, and more.

This parser implements a subset of DLGPE compatible with PIE's capabilities.
"""

# References:
# - "DLGP: An Extended Datalog Syntax for Existential Rules and Datalog±" —
#   Jean-Francois Baget, Mariano Rodriguez Gutierrez, Michel Leclere,
#   Marie-Laure Mugnier, Swan Rocher, Marie Sipieter.
#   Link: https://graphik-team.github.io/graal/doc/dlgp/dlgp.pdf
#
# Summary:
# DLGP/DLGPE define a concrete syntax for existential rules, facts, and queries.
# This parser implements the DLGP-based grammar with DLGPE extensions.
#
# Properties used here:
# - Conformance to the DLGP syntax for rules, facts, and queries.
# - Extension points for DLGPE-specific constructs.
#
# Implementation notes:
# The grammar and transformer follow the DLGP specification and expose a subset
# aligned with PIE capabilities.

from pathlib import Path
from typing import List, Iterator, Optional, Union
import re

from lark import Lark  # type: ignore[import-not-found]

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import is_comparison_predicate
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
    NegativeConstraint,
)
from lark.exceptions import VisitError  # type: ignore[import-not-found]

from prototyping_inference_engine.io.parsers.dlgpe.dlgpe_transformer import (
    DlgpeTransformer,
    DlgpeUnsupportedFeatureError,
)
from prototyping_inference_engine.api.data.comparison_data import ComparisonDataSource


class DlgpeParser:
    """
    Parser for DLGPE files.

    DLGPE extends DLGP with:
    - Negation (not) in rule bodies
    - Disjunction (|) in rule bodies
    - Ground neck (::-)
    - Arithmetic expressions in terms
    - Extended directives

    Features NOT supported by PIE (will raise DlgpeUnsupportedFeatureError):
    - Subqueries
    - Macro predicates
    - @patterns directives
    - JSON metadata

    Usage:
        parser = DlgpeParser.instance()
        result = parser.parse_file("knowledge.dlgpe")
        facts = result["facts"]
        rules = result["rules"]
        queries = result["queries"]
    """

    _instance: Optional["DlgpeParser"] = None
    _grammar_path = Path(__file__).parent / "dlgpe.lark"

    def __init__(self, strict_prefix_base: bool = True):
        """Initialize the parser with the DLGPE grammar."""
        self._strict_prefix_base = strict_prefix_base
        self._lark = Lark(
            self._grammar_path.read_text(),
            start="document",
            parser="lalr",
            transformer=None,  # We'll transform manually
        )
        self._transformer = DlgpeTransformer(strict_prefix_base=strict_prefix_base)

    @classmethod
    def instance(cls) -> "DlgpeParser":
        """Get the singleton parser instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def create(cls, strict_prefix_base: bool = True) -> "DlgpeParser":
        """Create a non-singleton parser with custom options."""
        return cls(strict_prefix_base=strict_prefix_base)

    def parse(self, text: str, transformer: Optional[DlgpeTransformer] = None) -> dict:
        """
        Parse DLGPE text and return structured results.

        Args:
            text: DLGPE source text

        Returns:
            Dictionary with keys:
            - "header": Header information (base, prefixes, top, una)
            - "facts": List of Atom objects
            - "rules": List of Rule objects
            - "constraints": List of NegativeConstraint objects
            - "queries": List of FOQuery objects
            - "sources": List of ReadableData sources required for evaluation
            - "imports": List of imported file references

        Raises:
            DlgpeUnsupportedFeatureError: If the text uses unsupported features
            lark.exceptions.LarkError: If the text has syntax errors
        """
        self._raise_for_unsupported_text(text)
        tree = self._lark.parse(text)
        transformer = transformer or DlgpeTransformer(
            strict_prefix_base=self._strict_prefix_base
        )
        try:
            result = transformer.transform(tree)
        except VisitError as e:
            # Unwrap DlgpeUnsupportedFeatureError from Lark's VisitError
            if isinstance(e.orig_exc, DlgpeUnsupportedFeatureError):
                raise e.orig_exc from None
            raise
        return self._organize_result(result)

    def _raise_for_unsupported_text(self, text: str) -> None:
        """Pre-scan for unsupported constructs that may fail in the parser."""
        stripped = re.sub(r"%[^\r\n]*", "", text)
        stripped = re.sub(r"<[^>]*>", "", stripped)

        if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\*\s*\(", stripped):
            return

        if re.search(
            r"\b(?!not\b)[a-z][A-Za-z0-9_]*\s*\(\s*[a-z][A-Za-z0-9_]*\s*\(",
            stripped,
        ):
            return

    def parse_file(self, path: Union[str, Path]) -> dict:
        """
        Parse a DLGPE file and return structured results.

        Args:
            path: Path to the DLGPE file

        Returns:
            Same as parse()

        Raises:
            FileNotFoundError: If the file doesn't exist
            DlgpeUnsupportedFeatureError: If the file uses unsupported features
        """
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        return self.parse(text)

    def parse_atoms(
        self, text: str, transformer: Optional[DlgpeTransformer] = None
    ) -> Iterator[Atom]:
        """
        Parse text containing only facts and yield atoms.

        Args:
            text: DLGPE text containing facts

        Yields:
            Atom objects
        """
        result = self.parse(text, transformer)
        yield from result["facts"]

    def parse_rules(
        self, text: str, transformer: Optional[DlgpeTransformer] = None
    ) -> Iterator[Rule]:
        """
        Parse text and yield rules.

        Args:
            text: DLGPE text containing rules

        Yields:
            Rule objects
        """
        result = self.parse(text, transformer)
        yield from result["rules"]

    def parse_queries(
        self, text: str, transformer: Optional[DlgpeTransformer] = None
    ) -> Iterator[FOQuery]:
        """
        Parse text and yield queries.

        Args:
            text: DLGPE text containing queries

        Yields:
            FOQuery objects
        """
        result = self.parse(text, transformer)
        yield from result["queries"]

    def parse_constraints(
        self, text: str, transformer: Optional[DlgpeTransformer] = None
    ) -> Iterator[NegativeConstraint]:
        """
        Parse text and yield constraints.

        Args:
            text: DLGPE text containing constraints

        Yields:
            NegativeConstraint objects
        """
        result = self.parse(text, transformer)
        yield from result["constraints"]

    def _organize_result(self, raw_result: dict) -> dict:
        """Organize the raw transformer result into categorized lists."""
        facts: List[Atom] = []
        rules: List[Rule] = []
        constraints: List[NegativeConstraint] = []
        queries: List[FOQuery] = []
        imports: list[str] = []
        header = raw_result.get("header", {}) or {}

        statements = raw_result.get("statements", [])

        for stmt in statements:
            if stmt is None:
                continue

            if isinstance(stmt, tuple):
                stmt_type = stmt[0]
                if stmt_type == "fact":
                    atoms = stmt[1]
                    facts.extend(atoms)
                elif stmt_type == "rule":
                    rules.append(stmt[1])
                elif stmt_type == "constraint":
                    constraints.append(stmt[1])
                elif stmt_type == "query":
                    queries.append(stmt[1])
                elif stmt_type == "import":
                    imports.append(str(stmt[1]))
            elif isinstance(stmt, Atom):
                facts.append(stmt)
            elif isinstance(stmt, Rule):
                rules.append(stmt)
            elif isinstance(stmt, NegativeConstraint):
                constraints.append(stmt)
            elif isinstance(stmt, FOQuery):
                queries.append(stmt)

        if isinstance(header, dict):
            imports.extend(header.get("imports", []) or [])

        sources = self._build_sources(facts, rules, queries, constraints, header)
        return {
            "header": header,
            "facts": facts,
            "rules": rules,
            "constraints": constraints,
            "queries": queries,
            "sources": sources,
            "imports": imports,
        }

    @staticmethod
    def _build_sources(
        facts: List[Atom],
        rules: List[Rule],
        queries: List[FOQuery],
        constraints: List[NegativeConstraint],
        header: dict,
    ) -> list:
        atoms: list[Atom] = list(facts)

        for rule in rules:
            atoms.extend(rule.body.atoms)
            atoms.extend(rule.head.atoms)

        for query in queries:
            atoms.extend(query.formula.atoms)

        for constraint in constraints:
            atoms.extend(getattr(constraint.body, "atoms", ()))

        from prototyping_inference_engine.api.data.readable_data import ReadableData

        sources: list[ReadableData] = []
        if any(is_comparison_predicate(atom.predicate) for atom in atoms):
            sources.append(ComparisonDataSource())

        stdfct_predicates: set = set()
        if atoms:
            from prototyping_inference_engine.api.atom.predicate import Predicate
            from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
                EvaluableFunctionTerm,
            )

            def collect_term_predicates(term) -> None:
                if isinstance(term, EvaluableFunctionTerm) and term.name.startswith(
                    "stdfct:"
                ):
                    stdfct_predicates.add(Predicate(term.name, len(term.args) + 1))
                args = getattr(term, "args", None)
                if args:
                    for arg in args:
                        collect_term_predicates(arg)

            for atom in atoms:
                for term in atom.terms:
                    collect_term_predicates(term)

        computed_prefixes = (
            header.get("computed", {}) if isinstance(header, dict) else {}
        )
        std_prefixes = {
            prefix for prefix, value in computed_prefixes.items() if value == "stdfct"
        }
        stdfct_predicates.update(
            {
                atom.predicate
                for atom in atoms
                if atom.predicate.name.startswith("stdfct:")
            }
        )
        if std_prefixes or stdfct_predicates:
            from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
                LiteralFactory,
            )
            from prototyping_inference_engine.api.atom.term.literal_config import (
                LiteralConfig,
            )
            from prototyping_inference_engine.api.atom.term.storage.dict_storage import (
                DictStorage,
            )
            from prototyping_inference_engine.api.data.functions.integraal_standard_functions import (
                IntegraalStandardFunctionSource,
            )

            resolved_prefixes = {prefix: "stdfct:" for prefix in std_prefixes}
            if not resolved_prefixes:
                resolved_prefixes = {"stdfct": "stdfct:"}
            computed_predicates = {
                atom.predicate
                for atom in atoms
                if atom.predicate.name.startswith("stdfct:")
            }
            if computed_predicates:
                literal_factory = LiteralFactory(DictStorage(), LiteralConfig.default())
                sources.append(
                    IntegraalStandardFunctionSource(
                        literal_factory, resolved_prefixes, computed_predicates
                    )
                )

        return sources


# Re-export the exception for convenience
__all__ = ["DlgpeParser", "DlgpeUnsupportedFeatureError"]
