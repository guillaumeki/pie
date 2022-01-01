from lark import Transformer, v_args

from api.atom.atom import Atom
from api.query.conjunctive_query import ConjunctiveQuery
from api.atom.term.constant import Constant
from api.atom.frozen_atom_set import FrozenAtomSet
from api.ontology.constraint.negative_constraint import NegativeConstraint
from api.atom.predicate import Predicate
from api.ontology.rule_base.rule import Rule
from api.atom.term.variable import Variable


class Dlgp2Transformer(Transformer):
    @staticmethod
    def std_atom(items):
        predicate, terms = items
        return Atom(Predicate(predicate, len(terms)), *terms)

    @staticmethod
    def equality(terms):
        return Atom(Predicate("=", 2), *terms)

    @staticmethod
    def constraint(c):
        if len(c) == 1:
            label, query = None, ConjunctiveQuery(c[0])
        else:
            label, query = c[0], ConjunctiveQuery(c[1])
        return NegativeConstraint(query, label)

    @staticmethod
    def rule(c):
        return Rule(body=ConjunctiveQuery(c[2]), head=ConjunctiveQuery(c[1]), label=c[0])

    @staticmethod
    def query(q):
        return ConjunctiveQuery(q[2], answer_variables=q[1], label=q[0])

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
    conjunction = __inline_identity
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

