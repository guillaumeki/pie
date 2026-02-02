"""
DLGPE Parser - Parser for the DLGPE language.

DLGPE (Datalog+- Grammar for Positive Existential rules) is an extended
version of DLGP that supports additional features like negation, disjunction
in rule bodies, and more.

This parser implements a subset of DLGPE compatible with PIE's capabilities.
"""
from pathlib import Path
from typing import List, Iterator, Optional, Union, Any
from functools import cache
import re

from lark import Lark

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from lark.exceptions import VisitError

from prototyping_inference_engine.parser.dlgpe.dlgpe_transformer import (
    DlgpeTransformer,
    DlgpeUnsupportedFeatureError,
)


class DlgpeParser:
    """
    Parser for DLGPE files.

    DLGPE extends DLGP with:
    - Negation (not) in rule bodies
    - Disjunction (|) in rule bodies
    - Ground neck (::-)
    - Extended directives

    Features NOT supported by PIE (will raise DlgpeUnsupportedFeatureError):
    - Functional terms
    - Arithmetic expressions
    - Comparison operators
    - Subqueries
    - Macro predicates
    - @import, @computed, @view, @patterns directives
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

    def __init__(self):
        """Initialize the parser with the DLGPE grammar."""
        self._lark = Lark(
            self._grammar_path.read_text(),
            start="document",
            parser="lalr",
            transformer=None,  # We'll transform manually
        )
        self._transformer = DlgpeTransformer()

    @classmethod
    def instance(cls) -> "DlgpeParser":
        """Get the singleton parser instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

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

        Raises:
            DlgpeUnsupportedFeatureError: If the text uses unsupported features
            lark.exceptions.LarkError: If the text has syntax errors
        """
        self._raise_for_unsupported_text(text)
        tree = self._lark.parse(text)
        transformer = transformer or self._transformer
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

        if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\*\s*\(", stripped):
            return

        if (
            re.search(r"(?<![eE])\b\d+\s*[+\-*/]\s*\d+\b", stripped)
            or re.search(
                r"\b[A-Za-z_][A-Za-z0-9_]*\s*[+\-*/]\s*[A-Za-z0-9_]",
                stripped,
            )
            or "**" in stripped
        ):
            raise DlgpeUnsupportedFeatureError(
                "Arithmetic expressions (+, -, *, /, **) are not supported by PIE"
            )

        if re.search(
            r"\b(?!not\b)[a-z][A-Za-z0-9_]*\s*\(\s*[a-z][A-Za-z0-9_]*\s*\(",
            stripped,
        ):
            raise DlgpeUnsupportedFeatureError(
                "Functional terms (f(X, Y)) are not supported by PIE"
            )

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

    def parse_atoms(self, text: str, transformer: Optional[DlgpeTransformer] = None) -> Iterator[Atom]:
        """
        Parse text containing only facts and yield atoms.

        Args:
            text: DLGPE text containing facts

        Yields:
            Atom objects
        """
        result = self.parse(text, transformer)
        yield from result["facts"]

    def parse_rules(self, text: str, transformer: Optional[DlgpeTransformer] = None) -> Iterator[Rule]:
        """
        Parse text and yield rules.

        Args:
            text: DLGPE text containing rules

        Yields:
            Rule objects
        """
        result = self.parse(text, transformer)
        yield from result["rules"]

    def parse_queries(self, text: str, transformer: Optional[DlgpeTransformer] = None) -> Iterator[FOQuery]:
        """
        Parse text and yield queries.

        Args:
            text: DLGPE text containing queries

        Yields:
            FOQuery objects
        """
        result = self.parse(text, transformer)
        yield from result["queries"]

    def parse_constraints(self, text: str, transformer: Optional[DlgpeTransformer] = None) -> Iterator[NegativeConstraint]:
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
            elif isinstance(stmt, Atom):
                facts.append(stmt)
            elif isinstance(stmt, Rule):
                rules.append(stmt)
            elif isinstance(stmt, NegativeConstraint):
                constraints.append(stmt)
            elif isinstance(stmt, FOQuery):
                queries.append(stmt)

        return {
            "header": raw_result.get("header", {}),
            "facts": facts,
            "rules": rules,
            "constraints": constraints,
            "queries": queries,
        }


# Re-export the exception for convenience
__all__ = ["DlgpeParser", "DlgpeUnsupportedFeatureError"]
