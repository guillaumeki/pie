"""
DLGPE Transformer - Converts DLGPE parse tree to PIE objects.
"""
from typing import List, Optional, Tuple, Any
from lark import Transformer, v_args, Token

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.factory.literal_factory import LiteralFactory
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    XSD_PREFIX,
    XSD_STRING,
    XSD_INTEGER,
    XSD_DECIMAL,
    XSD_DOUBLE,
    XSD_BOOLEAN,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.api.formula.disjunction_formula import DisjunctionFormula
from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint


class DlgpeUnsupportedFeatureError(Exception):
    """Raised when the DLGPE file uses a feature not supported by PIE."""
    pass


class Label(str):
    """Wrapper for label strings to distinguish them from other strings."""
    pass


class DlgpeTransformer(Transformer):
    """
    Transforms a DLGPE parse tree into PIE objects.

    Supported features:
    - Facts, rules, constraints, queries
    - Disjunction in heads and bodies
    - Negation (not)
    - Labels on statements
    - @base, @prefix, @top, @una directives

    Unsupported features (will raise DlgpeUnsupportedFeatureError):
    - Functional terms
    - Arithmetic expressions
    - Comparison operators (<, >, <=, >=, !=)
    - Subqueries (Var := body)
    - Macro predicates ($predicate)
    - Repeated atoms (predicate+ or predicate*)
    - @import, @computed, @view, @patterns directives
    - JSON metadata
    """

    def __init__(self, literal_factory: Optional[LiteralFactory] = None):
        super().__init__()
        self._base_iri: Optional[str] = None
        self._prefixes: dict[str, str] = {}
        self._top: Optional[str] = None
        self._una: bool = False
        self._ground_neck: bool = False  # Track if ::- was used
        self._literal_factory = literal_factory or LiteralFactory(
            DictStorage(), LiteralConfig.default()
        )

    # ==================== Unsupported Features ====================

    def unsupported_import(self, items):
        raise DlgpeUnsupportedFeatureError(
            "@import directive is not supported by PIE"
        )

    def unsupported_computed(self, items):
        raise DlgpeUnsupportedFeatureError(
            "@computed directive is not supported by PIE"
        )

    def unsupported_view(self, items):
        raise DlgpeUnsupportedFeatureError(
            "@view directive is not supported by PIE"
        )

    def unsupported_patterns(self, items):
        raise DlgpeUnsupportedFeatureError(
            "@patterns directive is not supported by PIE"
        )

    def unsupported_json(self, items):
        raise DlgpeUnsupportedFeatureError(
            "JSON metadata is not supported by PIE. Use simple labels [name] instead."
        )

    def unsupported_subquery(self, items):
        raise DlgpeUnsupportedFeatureError(
            "Subqueries (Var := body) are not supported by PIE"
        )

    def unsupported_operator(self, items):
        raise DlgpeUnsupportedFeatureError(
            "Comparison operators (<, >, <=, >=, !=) are not supported by PIE"
        )

    def unsupported_repeated(self, items):
        raise DlgpeUnsupportedFeatureError(
            "Repeated atoms (predicate+ or predicate*) are not supported by PIE"
        )

    def unsupported_pattern_atom(self, items):
        raise DlgpeUnsupportedFeatureError(
            "Pattern predicates ($name) are not supported by PIE"
        )

    def unsupported_arithmetic(self, items):
        raise DlgpeUnsupportedFeatureError(
            "Arithmetic expressions (+, -, *, /, **) are not supported by PIE"
        )

    def unsupported_functional(self, items):
        raise DlgpeUnsupportedFeatureError(
            "Functional terms (f(X, Y)) are not supported by PIE"
        )

    # ==================== Document Structure ====================

    def document(self, items):
        """Process the entire document."""
        header = items[0] if items else {}
        body = items[1] if len(items) > 1 else []
        return {
            "header": header,
            "statements": body,
        }

    def header(self, items):
        """Collect header directives."""
        return {
            "base": self._base_iri,
            "prefixes": self._prefixes.copy(),
            "top": self._top,
            "una": self._una,
        }

    def body(self, items):
        """Flatten body statements."""
        result = []
        for item in items:
            if isinstance(item, list):
                result.extend(item)
            elif item is not None:
                result.append(item)
        return result

    # ==================== Directives ====================

    def base_directive(self, items):
        # items[0] = BASE_KWD, items[1] = identifier
        self._base_iri = str(items[1])
        return None

    def prefix_directive(self, items):
        # items[0] = PREFIX_KWD, items[1] = prefix, items[2] = identifier
        prefix = str(items[1])
        iri = str(items[2])
        self._prefixes[prefix] = iri
        return None

    def top_directive(self, items):
        # items[0] = TOP_KWD, items[1] = identifier
        self._top = str(items[1])
        return None

    def una_directive(self, items):
        self._una = True
        return None

    # ==================== Blocks ====================

    def facts_block(self, items):
        return [item for item in items if item is not None]

    def rules_block(self, items):
        return [item for item in items if item is not None]

    def constraints_block(self, items):
        return [item for item in items if item is not None]

    def queries_block(self, items):
        return [item for item in items if item is not None]

    def block(self, items):
        return items[0] if items else []

    def statement(self, items):
        return items[0] if items else None

    # ==================== Sentences ====================

    def dlgpe_fact(self, items) -> Tuple[str, List[Atom]]:
        """Process a fact: [label] head."""
        label = None
        head_formula = None

        for item in items:
            if isinstance(item, Label):
                label = str(item) if item else None
            elif isinstance(item, Formula):
                head_formula = item

        if head_formula is None:
            return ("fact", [], label)

        # Extract atoms from head formula
        atoms = self._extract_atoms_from_formula(head_formula)
        return ("fact", atoms, label)

    def dlgpe_rule(self, items) -> Tuple[str, Rule, Optional[str]]:
        """Process a rule: [label] head :- body."""
        label = None
        head_formula = None
        body_formula = None
        found_neck = False

        for item in items:
            if isinstance(item, Label):
                label = str(item) if item else None
            elif isinstance(item, str) and item in (":-", "::-"):
                found_neck = True
            elif isinstance(item, Formula):
                if not found_neck:
                    head_formula = item
                else:
                    body_formula = item

        # Convert head to disjunction of ConjunctiveQuery
        if head_formula is None:
            head_disjuncts = [ConjunctiveQuery(frozenset())]
        else:
            head_disjuncts = self._formula_to_head_disjuncts(head_formula)

        # Convert body to ConjunctiveQuery
        if body_formula is None:
            body = ConjunctiveQuery(frozenset())
        else:
            body = self._formula_to_conjunctive_query(body_formula)

        rule = Rule(body=body, head=tuple(head_disjuncts), label=label)
        return ("rule", rule, label)

    def dlgpe_constraint(self, items) -> Tuple[str, NegativeConstraint, Optional[str]]:
        """Process a constraint: [label] ! :- body."""
        label = None
        body_formula = None

        for item in items:
            if isinstance(item, Label):
                label = str(item) if item else None
            elif isinstance(item, Formula):
                body_formula = item

        if body_formula is None:
            body = ConjunctiveQuery(frozenset())
        else:
            body = self._formula_to_conjunctive_query(body_formula)

        constraint = NegativeConstraint(body=body, label=label)
        return ("constraint", constraint, label)

    def dlgpe_query(self, items) -> Tuple[str, FOQuery, Optional[str]]:
        """Process a query: [label] ?(vars) :- body."""
        label = None
        answer_vars = frozenset()
        body_formula = None

        for item in items:
            if isinstance(item, Label):
                label = str(item) if item else None
            elif isinstance(item, frozenset):
                answer_vars = item
            elif isinstance(item, Formula):
                body_formula = item
            elif str(item) == "*":
                # All variables in body are answer vars
                answer_vars = None  # Will be computed later

        if body_formula is None:
            body_formula = ConjunctionFormula(())

        # If answer_vars is None (*), compute from body
        if answer_vars is None:
            answer_vars = body_formula.free_variables
        else:
            extra_free_vars = body_formula.free_variables - set(answer_vars)
            for var in sorted(extra_free_vars, key=str):
                body_formula = ExistentialFormula(var, body_formula)

        query = FOQuery(formula=body_formula, answer_variables=answer_vars, label=label)
        return ("query", query, label)

    # ==================== Formulas ====================

    def head_formula(self, items):
        return items[0] if items else None

    def head_disjunction(self, items) -> Formula:
        """Head disjunction: conj | conj | ..."""
        if len(items) == 1:
            return items[0]
        return DisjunctionFormula(items[0], items[1]) if len(items) == 2 else self._build_disjunction(items)

    def head_conjunction(self, items) -> Formula:
        """Head conjunction: elem, elem, ..."""
        if len(items) == 1:
            return items[0]
        return self._build_conjunction(items)

    def head_elementary(self, items):
        return items[0] if items else None

    def body_formula(self, items):
        return items[0] if items else None

    def body_disjunction(self, items) -> Formula:
        """Body disjunction: conj | conj | ..."""
        if len(items) == 1:
            return items[0]
        return DisjunctionFormula(items[0], items[1]) if len(items) == 2 else self._build_disjunction(items)

    def body_conjunction(self, items) -> Formula:
        """Body conjunction: elem, elem, ..."""
        if len(items) == 1:
            return items[0]
        return self._build_conjunction(items)

    def body_elementary(self, items):
        return items[0] if items else None

    def grouped_formula(self, items):
        """Parenthesized formula."""
        return items[0] if items else None

    def negated_formula(self, items) -> NegationFormula:
        """not (formula)"""
        return NegationFormula(items[-1])

    def negated_atom(self, items) -> NegationFormula:
        """not atom"""
        return NegationFormula(items[-1])

    # ==================== Atoms ====================

    def head_atom(self, items) -> Atom:
        """Atom in head: predicate(terms)"""
        predicate_name = items[0]
        terms = items[1] if len(items) > 1 else ()
        predicate = Predicate(predicate_name, len(terms))
        return Atom(predicate, *terms)

    def body_atom(self, items) -> Atom:
        """Atom in body: predicate(terms)"""
        predicate_name = items[0]
        terms = items[1] if len(items) > 1 else ()
        predicate = Predicate(predicate_name, len(terms))
        return Atom(predicate, *terms)

    def equal_atom(self, items) -> Atom:
        """Equality atom: term = term"""
        # Create equality as a special atom with predicate "="
        eq_pred = Predicate("=", 2)
        return Atom(eq_pred, items[0], items[1])

    # ==================== Terms ====================

    def head_terms_list(self, items) -> Tuple[Term, ...]:
        return tuple(items)

    def body_terms_list(self, items) -> Tuple[Term, ...]:
        return tuple(items)

    def variable_list(self, items) -> frozenset:
        return frozenset(items)

    def answer_vars(self, items):
        if not items:
            return frozenset()
        # Check for STAR token (when * is used for all variables)
        if hasattr(items[0], 'type') and items[0].type == 'STAR':
            return "*"
        if isinstance(items[0], frozenset):
            return items[0]
        return frozenset()

    def head_term(self, items):
        return items[0] if items else None

    def body_term(self, items):
        return items[0] if items else None

    def term(self, items):
        return items[0] if items else None

    def named_variable(self, items) -> Variable:
        name = str(items[0])
        return Variable(name)

    def anonymous_variable(self, items) -> Variable:
        # Generate a unique anonymous variable
        return Variable.anonymous()

    def constant(self, items) -> Term:
        value = items[0]
        if isinstance(value, Constant):
            return value
        if isinstance(value, Literal):
            return value
        return Constant(str(value))

    def predicate(self, items) -> Predicate:
        # Predicate arity will be determined when creating the atom
        # For now, just return the identifier
        return items[0]

    # ==================== Literals ====================

    def literal(self, items) -> Literal:
        value = items[0]
        if isinstance(value, Literal):
            return value
        lexical = str(value)
        return self._literal_factory.create(lexical, f"{XSD_PREFIX}{XSD_STRING}")

    def typed_literal(self, items) -> Literal:
        lexical = str(items[0])
        type_iri = str(items[1])
        return self._literal_factory.create(lexical, type_iri)

    def numeric_literal(self, items) -> Literal:
        literal_type, lexical = items[0]
        datatype = f"{XSD_PREFIX}{literal_type}"
        return self._literal_factory.create(lexical, datatype)

    def boolean_literal(self, items) -> Literal:
        lexical = str(items[0]).lower()
        return self._literal_factory.create(lexical, f"{XSD_PREFIX}{XSD_BOOLEAN}")

    def STRING_LITERAL_QUOTE(self, token) -> str:
        # Remove surrounding quotes
        return token[1:-1]

    def STRING_LITERAL_SINGLE_QUOTE(self, token) -> str:
        return token[1:-1]

    # ==================== Identifiers ====================

    def identifier(self, items) -> str:
        token = items[0]
        if isinstance(token, Token):
            value = str(token)
            # Handle IRI references
            if value.startswith("<") and value.endswith(">"):
                return value[1:-1]
            return value
        return str(token)

    def prefix(self, items) -> str:
        return str(items[0])

    def IRIREF(self, token) -> str:
        # Remove < and >
        return str(token)[1:-1]

    def PNAME_LN(self, token) -> str:
        return str(token)

    def PNAME_NS(self, token) -> str:
        return str(token)

    def SIMPLE_IDENTIFIER(self, token) -> str:
        return str(token)

    def LOWERCASE_PREFIX(self, token) -> str:
        return str(token)

    def NAMED_VARIABLE(self, token) -> str:
        return str(token)

    def UPPERCASE_PREFIX(self, token) -> str:
        return str(token)

    def INTEGER(self, token) -> tuple[str, str]:
        return XSD_INTEGER, str(token)

    def DECIMAL(self, token) -> tuple[str, str]:
        return XSD_DECIMAL, str(token)

    def DOUBLE(self, token) -> tuple[str, str]:
        return XSD_DOUBLE, str(token)

    # ==================== Labels ====================

    def label(self, items) -> Label:
        if items and items[0]:
            # Return just the content without brackets (consistent with DLGP)
            return Label(str(items[0]).strip())
        return Label("")

    def item_info(self, items):
        return items[0] if items else None

    def LABEL_CONTENT(self, token) -> str:
        return str(token).strip()

    # ==================== Neck ====================

    def neck(self, items):
        token = items[0] if items else ":-"
        self._ground_neck = (str(token) == "::-")
        return str(token)

    # ==================== Helper Methods ====================

    def _build_disjunction(self, formulas: List[Formula]) -> Formula:
        """Build a disjunction from multiple formulas."""
        if len(formulas) == 0:
            raise ValueError("Cannot build disjunction from empty list")
        if len(formulas) == 1:
            return formulas[0]

        result = formulas[0]
        for f in formulas[1:]:
            result = DisjunctionFormula(result, f)
        return result

    def _build_conjunction(self, formulas: List[Formula]) -> Formula:
        """Build a conjunction from multiple formulas."""
        if len(formulas) == 0:
            raise ValueError("Cannot build conjunction from empty list")
        if len(formulas) == 1:
            return formulas[0]

        result = formulas[0]
        for f in formulas[1:]:
            result = ConjunctionFormula(result, f)
        return result

    def _extract_atoms_from_formula(self, formula: Formula) -> List[Atom]:
        """Extract all atoms from a formula (for facts)."""
        if isinstance(formula, Atom):
            return [formula]
        elif isinstance(formula, ConjunctionFormula):
            result = []
            result.extend(self._extract_atoms_from_formula(formula.left))
            result.extend(self._extract_atoms_from_formula(formula.right))
            return result
        elif isinstance(formula, DisjunctionFormula):
            result = []
            result.extend(self._extract_atoms_from_formula(formula.left))
            result.extend(self._extract_atoms_from_formula(formula.right))
            return result
        else:
            return []

    def _formula_to_head_disjuncts(self, formula: Formula) -> List[ConjunctiveQuery]:
        """Convert a head formula to a list of ConjunctiveQuery disjuncts."""
        if isinstance(formula, Atom):
            return [ConjunctiveQuery(frozenset([formula]))]
        elif isinstance(formula, ConjunctionFormula):
            atoms = self._extract_atoms_from_formula(formula)
            return [ConjunctiveQuery(frozenset(atoms))]
        elif isinstance(formula, DisjunctionFormula):
            result = []
            result.extend(self._formula_to_head_disjuncts(formula.left))
            result.extend(self._formula_to_head_disjuncts(formula.right))
            return result
        else:
            raise ValueError(f"Unexpected formula type in head: {type(formula)}")

    def _formula_to_conjunctive_query(self, formula: Formula) -> ConjunctiveQuery:
        """Convert a body formula to a ConjunctiveQuery."""
        atoms = self._extract_atoms_from_formula(formula)
        return ConjunctiveQuery(frozenset(atoms))
