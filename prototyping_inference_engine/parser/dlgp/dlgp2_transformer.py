from lark import Transformer, v_args  # type: ignore[import-not-found]

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
    NegativeConstraint,
)
from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    XSD_PREFIX,
    XSD_BOOLEAN,
    XSD_INTEGER,
    XSD_DECIMAL,
    XSD_DOUBLE,
    RDF_PREFIX,
    RDF_LANG_STRING,
    XSD_STRING,
)
from prototyping_inference_engine.parser.iri_resolution import resolve_iri_reference


class Dlgp2Transformer(Transformer):
    def __init__(self, literal_factory: LiteralFactory | None = None):
        super().__init__()
        self._base_iri: str | None = None
        self._prefixes: dict[str, str] = {}
        self._builtin_prefixes: dict[str, str] = {
            "xsd": XSD_PREFIX,
            "rdf": RDF_PREFIX,
        }
        self._top: str | None = None
        self._una: bool = False
        self._literal_factory = literal_factory or LiteralFactory(
            DictStorage(), LiteralConfig.default()
        )

    @staticmethod
    def std_atom(items):
        predicate, terms = items
        return Atom(Predicate(predicate, len(terms)), *terms)

    @staticmethod
    def equality(terms):
        return Atom(SpecialPredicate.EQUALITY.value, *terms)

    @staticmethod
    def constraint(c):
        if len(c) == 1:
            label, query = None, ConjunctiveQuery(c[0])
        else:
            label, query = c[0], ConjunctiveQuery(c[1])
        return NegativeConstraint(query, label)

    @staticmethod
    def rule(c):
        return Rule(
            body=ConjunctiveQuery(c[-1]),
            head=tuple(ConjunctiveQuery(disjunct) for disjunct in c[1]),
            label=c[0],
        )

    @staticmethod
    def query(q):
        if q[2] is None:
            return ConjunctiveQuery(q[2], answer_variables=q[1], label=q[0])
        elif len(q[2]) == 1:
            pre_substitution = Substitution()
            atoms = MutableAtomSet()
            for atom in q[2][0]:
                if atom.predicate != SpecialPredicate.EQUALITY.value:
                    atoms.add(atom)
            for atom in q[2][0]:
                if atom.predicate == SpecialPredicate.EQUALITY.value:
                    if isinstance(atom.terms[0], (Constant, Literal)) or (
                        atom.terms[1] not in atoms.variables and atom.terms[1] in q[1]
                    ):
                        first_term, second_term = atom.terms[1], atom.terms[0]
                    else:
                        first_term, second_term = atom.terms[0], atom.terms[1]
                    pre_substitution[first_term] = second_term

            return ConjunctiveQuery(
                FrozenAtomSet(atoms),
                answer_variables=q[1],
                label=q[0],
                pre_substitution=pre_substitution,
            )

        return UnionQuery(
            (Dlgp2Transformer.query(q[:2] + [[disjunct]]) for disjunct in q[2]),
            answer_variables=q[1],
            label=q[0],
        )

    @staticmethod
    def fact(items):
        return items[-1]

    @staticmethod
    def body(items):
        body = []
        for item in items:
            if isinstance(item, list):
                body.extend(item)
            else:
                body.append(item)
        return {"body": body}

    @staticmethod
    def __identity(x):
        return x

    @staticmethod
    @v_args(inline=True)
    def __inline_identity(x):
        return x

    @staticmethod
    def __join(s):
        return "".join(s)

    def constant(self, items):
        value = items[0]
        if isinstance(value, (Constant, Literal)):
            return value
        return Constant(str(value))

    variable = v_args(inline=True)(Variable)
    not_empty_conjunction = FrozenAtomSet
    not_empty_disjunction_of_conjunctions = list
    conjunction = __inline_identity
    disjunction_of_conjunctions = __inline_identity
    not_empty_term_list = tuple
    predicate = __inline_identity
    term = __inline_identity
    term_list = __inline_identity
    atom = __inline_identity
    statement = __inline_identity
    section = __identity
    u_ident = __join
    l_ident = __join
    label = __join

    def STRING_LITERAL_QUOTE(self, token) -> str:
        return str(token)[1:-1]

    def STRING_LITERAL_SINGLE_QUOTE(self, token) -> str:
        return str(token)[1:-1]

    def STRING_LITERAL_LONG_SINGLE_QUOTE(self, token) -> str:
        raw = str(token)
        return raw[3:-3]

    def STRING_LITERAL_LONG_QUOTE(self, token) -> str:
        raw = str(token)
        return raw[3:-3]

    def IRIREF(self, token) -> str:
        value = str(token)
        return self._resolve_iri_reference(value[1:-1])

    def LANGTAG(self, token) -> str:
        value = str(token)
        return value[1:] if value.startswith("@") else value

    def PNAME_LN(self, token) -> str:
        return str(token)

    def PNAME_NS(self, token) -> str:
        return str(token)

    def prefixed_name(self, items):
        return self._resolve_prefixed_name(items[0])

    def iri(self, items):
        return items[0]

    def string(self, items):
        return items[0]

    def rdf_literal(self, items):
        lexical = items[0]
        if len(items) == 1:
            return self._literal_factory.create(lexical, f"{XSD_PREFIX}{XSD_STRING}")
        qualifier = items[1]
        if not isinstance(qualifier, str):
            qualifier = str(qualifier)
        if ":" not in qualifier and "/" not in qualifier and "#" not in qualifier:
            return self._literal_factory.create(
                lexical, f"{RDF_PREFIX}{RDF_LANG_STRING}", qualifier
            )
        return self._literal_factory.create(lexical, qualifier)

    def numeric_literal(self, items):
        literal_type, lexical = items[0]
        return self._literal_factory.create(lexical, f"{XSD_PREFIX}{literal_type}")

    def boolean_literal(self, items):
        lexical = str(items[0]).lower()
        return self._literal_factory.create(lexical, f"{XSD_PREFIX}{XSD_BOOLEAN}")

    def INTEGER(self, token) -> tuple[str, str]:
        return XSD_INTEGER, str(token)

    def DECIMAL(self, token) -> tuple[str, str]:
        return XSD_DECIMAL, str(token)

    def DOUBLE(self, token) -> tuple[str, str]:
        return XSD_DOUBLE, str(token)

    def base(self, items):
        self._base_iri = str(items[0])
        return None

    def prefix(self, items):
        prefix = self._prefix_name(str(items[0]))
        iri = str(items[1])
        self._prefixes[prefix] = iri
        return None

    def top(self, items):
        self._top = str(items[0])
        return None

    def una(self, items):
        self._una = True
        return None

    def header(self, items):
        return {
            "header": {
                "base": self._base_iri,
                "prefixes": dict(self._prefixes),
                "top": self._top,
                "una": self._una,
            }
        }

    def document(self, items):
        return {k: v for e in items for k, v in e.items()}

    def _resolve_iri_reference(self, value: str) -> str:
        if self._base_iri is None:
            return value
        return resolve_iri_reference(value, self._base_iri)

    def _resolve_prefixed_name(self, value: str) -> str:
        prefix, local = self._split_prefixed_name(str(value))
        if prefix in self._prefixes:
            base = self._prefixes[prefix]
        elif prefix in self._builtin_prefixes:
            base = self._builtin_prefixes[prefix]
        else:
            raise ValueError(f"Unknown prefix: {prefix or '<default>'}")
        return f"{base}{local}"

    @staticmethod
    def _split_prefixed_name(value: str) -> tuple[str, str]:
        if ":" not in value:
            return value, ""
        prefix, local = value.split(":", 1)
        return prefix, local

    @staticmethod
    def _prefix_name(value: str) -> str:
        if value.endswith(":"):
            return value[:-1]
        return value
