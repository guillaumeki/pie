"""DLGPE writer for ParseResult."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.quantified_formula import (
    QuantifiedFormula,
)
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
    NegativeConstraint,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.query.union_conjunctive_queries import (
    UnionConjunctiveQueries,
)
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    datatype_local_name,
    is_xsd_datatype,
    XSD_BOOLEAN,
    XSD_DECIMAL,
    XSD_DOUBLE,
    XSD_FLOAT,
    XSD_INTEGER,
    XSD_STRING,
)
from prototyping_inference_engine.api.iri.iri import IRIRef
from prototyping_inference_engine.api.iri.manager import IRIManager
from prototyping_inference_engine.api.iri.normalization import (
    RFCNormalizationScheme,
    StandardComposableNormalizer,
)
from prototyping_inference_engine.session.parse_result import ParseResult


@dataclass
class WriterIriContext:
    base_iri: Optional[str]
    prefixes: dict[str, str]


class DlgpeWriter:
    """Serialize ParseResult into a DLGPE document."""

    def __init__(
        self,
        base_iri: Optional[str] = None,
        prefixes: Optional[Iterable[tuple[str, str]]] = None,
        strict_prefix_base: bool = True,
    ) -> None:
        self._base_iri = base_iri
        self._prefixes = dict(prefixes or {})
        self._strict_prefix_base = strict_prefix_base
        self._iri_manager = IRIManager(
            normalizer=StandardComposableNormalizer(RFCNormalizationScheme.STRING),
            use_default_base=False,
        )
        if self._base_iri is not None:
            self._iri_manager.set_base(self._base_iri)
        for key, iri in self._prefixes.items():
            if self._base_iri is None and not IRIRef(iri).is_absolute():
                if self._strict_prefix_base:
                    raise ValueError("Relative prefix IRI declared without a base IRI.")
            self._iri_manager.set_prefix(key, iri)

    def write(self, result: ParseResult) -> str:
        context = WriterIriContext(
            base_iri=result.base_iri or self._base_iri,
            prefixes=dict(result.prefixes) or self._prefixes,
        )
        return self.write_with_context(result, context)

    def write_with_context(self, result: ParseResult, context: WriterIriContext) -> str:
        lines: list[str] = []
        if context.base_iri:
            lines.append(f"@base <{context.base_iri}>.")
        for prefix, iri in sorted(context.prefixes.items()):
            lines.append(f"@prefix {prefix}: <{iri}>.")

        if result.facts:
            lines.append("@facts")
            for atom in self._sorted_atoms(result.facts):
                lines.append(f"{self._format_formula(atom, context)}.")

        if result.rules:
            lines.append("@rules")
            for rule in sorted(result.rules, key=str):
                lines.append(f"{self._format_rule(rule, context)}.")

        if result.constraints:
            lines.append("@constraints")
            for constraint in sorted(result.constraints, key=str):
                lines.append(f"{self._format_constraint(constraint, context)}.")

        if result.queries:
            lines.append("@queries")
            for query in result.queries:
                lines.extend(self._format_query_lines(query, context))

        return "\n".join(lines) + ("\n" if lines else "")

    def _format_rule(self, rule: Rule, context: WriterIriContext) -> str:
        label = f"[{rule.label}] " if rule.label else ""
        head = self._format_rule_head(rule, context)
        body = self._format_conjunctive_query(rule.body, context)
        return f"{label}{head} :- {body}"

    def _format_rule_head(self, rule: Rule, context: WriterIriContext) -> str:
        disjuncts = [self._format_conjunctive_query(h, context) for h in rule.head]
        return " | ".join(
            f"({d})" if self._needs_grouping(d) and len(rule.head) > 1 else d
            for d in disjuncts
        )

    def _format_constraint(
        self, constraint: NegativeConstraint, context: WriterIriContext
    ) -> str:
        label = f"[{constraint.label}] " if constraint.label else ""
        body = self._format_query_body(constraint.body, context)
        return f"{label}! :- {body}"

    def _format_query_lines(self, query: Query, context: WriterIriContext) -> list[str]:
        if isinstance(query, UnionQuery):
            result_lines: list[str] = []
            for sub in query.queries:
                result_lines.extend(self._format_query_lines(sub, context))
            return result_lines
        if isinstance(query, UnionConjunctiveQueries):
            result_lines = []
            for sub in query.queries:
                result_lines.extend(self._format_query_lines(sub, context))
            return result_lines

        if isinstance(query, ConjunctiveQuery):
            answers = ", ".join(str(v) for v in query.answer_variables)
            body = self._format_conjunctive_query(query, context)
            return [f"?({answers}) :- {body}."]

        if isinstance(query, FOQuery):
            answers = ", ".join(str(v) for v in query.answer_variables)
            body = self._format_formula(query.formula, context)
            return [f"?({answers}) :- {body}."]

        raise ValueError(f"Unsupported query type for DLGPE writer: {type(query)}")

    def _format_query_body(self, query: Query, context: WriterIriContext) -> str:
        if isinstance(query, ConjunctiveQuery):
            return self._format_conjunctive_query(query, context)
        if isinstance(query, FOQuery):
            return self._format_formula(query.formula, context)
        raise ValueError(f"Unsupported query type for DLGPE writer: {type(query)}")

    def _format_conjunctive_query(
        self, query: ConjunctiveQuery, context: WriterIriContext
    ) -> str:
        atoms = self._sorted_atoms(query.atoms)
        return ", ".join(self._format_formula(atom, context) for atom in atoms)

    def _format_formula(self, formula: Formula, context: WriterIriContext) -> str:
        return self._format_formula_with_prec(formula, context, parent_prec=0)

    def _format_formula_with_prec(
        self, formula: Formula, context: WriterIriContext, parent_prec: int
    ) -> str:
        if isinstance(formula, Atom):
            return self._format_atom(formula, context)

        if isinstance(formula, NegationFormula):
            inner = self._format_formula_with_prec(
                formula.inner, context, parent_prec=3
            )
            return f"not {inner}"

        if isinstance(formula, ConjunctionFormula):
            parts = self._flatten_conjunction(formula)
            rendered = ", ".join(
                self._format_formula_with_prec(part, context, parent_prec=2)
                for part in parts
            )
            return self._maybe_parenthesize(rendered, parent_prec, 2)

        if isinstance(formula, DisjunctionFormula):
            parts = self._flatten_disjunction(formula)
            rendered = " | ".join(
                self._format_formula_with_prec(part, context, parent_prec=1)
                for part in parts
            )
            return self._maybe_parenthesize(rendered, parent_prec, 1)

        if isinstance(
            formula, (ExistentialFormula, UniversalFormula, QuantifiedFormula)
        ):
            raise ValueError("Quantified formulas are not supported in DLGPE writer")

        raise ValueError(f"Unsupported formula type for DLGPE writer: {type(formula)}")

    @staticmethod
    def _flatten_conjunction(formula: ConjunctionFormula) -> list[Formula]:
        parts: list[Formula] = []
        stack: list[Formula] = [formula]
        while stack:
            current = stack.pop()
            if isinstance(current, ConjunctionFormula):
                stack.append(current.right)
                stack.append(current.left)
            else:
                parts.append(current)
        return parts

    @staticmethod
    def _flatten_disjunction(formula: DisjunctionFormula) -> list[Formula]:
        parts: list[Formula] = []
        stack: list[Formula] = [formula]
        while stack:
            current = stack.pop()
            if isinstance(current, DisjunctionFormula):
                stack.append(current.right)
                stack.append(current.left)
            else:
                parts.append(current)
        return parts

    @staticmethod
    def _maybe_parenthesize(text: str, parent_prec: int, current_prec: int) -> str:
        if current_prec < parent_prec:
            return f"({text})"
        return text

    @staticmethod
    def _needs_grouping(text: str) -> bool:
        return "," in text or "|" in text

    def _format_atom(self, atom: Atom, context: WriterIriContext) -> str:
        predicate = atom.predicate
        if (
            predicate.display_mode in {"infix", "infix_no_spaces"}
            and predicate.arity == 2
        ):
            left = self._format_term(atom.terms[0], context)
            right = self._format_term(atom.terms[1], context)
            symbol = predicate.display_symbol or str(predicate)
            if predicate.display_mode == "infix_no_spaces":
                return f"{left}{symbol}{right}"
            return f"{left} {symbol} {right}"

        pred_name = self._format_predicate(predicate, context)
        terms = ", ".join(self._format_term(term, context) for term in atom.terms)
        return f"{pred_name}({terms})"

    def _format_predicate(self, predicate: Predicate, context: WriterIriContext) -> str:
        return self._format_identifier(predicate.name, context)

    def _format_term(self, term, context: WriterIriContext) -> str:
        if isinstance(term, Variable):
            return str(term)
        if isinstance(term, Literal):
            return self._format_literal(term, context)
        if isinstance(term, Constant):
            return self._format_identifier(str(term.identifier), context)
        return str(term)

    def _format_literal(self, literal: Literal, context: WriterIriContext) -> str:
        lexical = literal.lexical if literal.lexical is not None else str(literal.value)
        if literal.lang:
            return f'"{lexical}"@{literal.lang}'
        if literal.datatype is None:
            return f'"{lexical}"'

        local_name = datatype_local_name(literal.datatype)
        if is_xsd_datatype(literal.datatype):
            if local_name in {
                XSD_BOOLEAN,
                XSD_INTEGER,
                XSD_DECIMAL,
                XSD_DOUBLE,
                XSD_FLOAT,
            }:
                return lexical
            if local_name == XSD_STRING:
                return f'"{lexical}"'

        datatype = self._format_identifier(literal.datatype, context)
        return f'"{lexical}"^^{datatype}'

    def _format_identifier(self, value: str, context: WriterIriContext) -> str:
        if not self._looks_like_iri(value):
            return value

        prefix_output = self._format_prefixed_or_relative(value, context)
        if self._is_prefixed_name(prefix_output, context):
            return prefix_output
        return f"<{prefix_output}>"

    def _format_prefixed_or_relative(
        self, value: str, context: WriterIriContext
    ) -> str:
        iri = IRIRef(value)
        best = iri.recompose()
        best_len = len(best)
        best_prefix: Optional[str] = None

        if context.base_iri:
            base_ref = IRIRef(context.base_iri)
            rel = iri.relativize(base_ref)
            rel_str = rel.recompose()
            if len(rel_str) < best_len:
                best = rel_str
                best_len = len(rel_str)

        for prefix, base in context.prefixes.items():
            base_ref = IRIRef(base)
            rel = iri.relativize(base_ref)
            if rel.scheme is not None:
                continue
            rel_str = rel.recompose()
            total_len = len(prefix) + 1 + len(rel_str)
            if total_len < best_len:
                best = rel_str
                best_len = total_len
                best_prefix = prefix

        if best_prefix is not None:
            return f"{best_prefix}:{best}"
        return best

    @staticmethod
    def _is_prefixed_name(value: str, context: WriterIriContext) -> bool:
        if ":" not in value:
            return False
        prefix = value.split(":", 1)[0]
        return prefix in context.prefixes

    @staticmethod
    def _looks_like_iri(value: str) -> bool:
        if value.startswith("//") or value.startswith("/"):
            return True
        return (
            any(
                value.startswith(prefix)
                for prefix in (
                    "http:",
                    "https:",
                    "urn:",
                    "file:",
                    "mailto:",
                    "news:",
                    "tel:",
                    "ldap:",
                )
            )
            or "#" in value
            or "://" in value
        )

    @staticmethod
    def _sorted_atoms(atoms: Iterable[Atom]) -> list[Atom]:
        return sorted(atoms, key=lambda atom: str(atom))


__all__ = ["DlgpeWriter", "WriterIriContext"]
