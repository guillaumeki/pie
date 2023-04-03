from lark import Transformer, v_args

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.api.substitution.substitution import Substitution


class Dlgp2Transformer(Transformer):
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
        return Rule(body=ConjunctiveQuery(c[-1]),
                    head=tuple(ConjunctiveQuery(disjunct) for disjunct in c[1]), label=c[0])

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
                    if (isinstance(atom.terms[0], Constant)
                            or (atom.terms[1] not in atoms.variables and atom.terms[1] in q[1])):
                        first_term, second_term = atom.terms[1], atom.terms[0]
                    else:
                        first_term, second_term = atom.terms[0], atom.terms[1]
                    pre_substitution[first_term] = second_term

            return ConjunctiveQuery(FrozenAtomSet(atoms),
                                    answer_variables=q[1],
                                    label=q[0],
                                    pre_substitution=pre_substitution)

        return UnionConjunctiveQueries((Dlgp2Transformer.query(q[:2]+[[disjunct]]) for disjunct in q[2]),
                                       answer_variables=q[1],
                                       label=q[0])

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
    def header(items):
        return {"header": items}

    @staticmethod
    def document(*x):
        return {k: v for e in x[0] for k, v in e.items()}

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

    constant = v_args(inline=True)(Constant)
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

