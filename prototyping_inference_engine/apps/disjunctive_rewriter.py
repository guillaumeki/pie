#cython: language_level=3
import argparse
import os
import sys
from math import inf

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import BreadthFirstRewriting
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The dlgp file containing the rules and the UCQ to rewrite with them", type=str)
    parser.add_argument("-l", "--limit", help="Limit number of breadth first steps", type=int, default=inf)
    parser.add_argument("-v", "--verbose", help="Print all intermediate steps", action="store_true")
    parser.add_argument("-m", "--mapping", help="Make an S-rewriting", action="store_true")
    args = parser.parse_args()

    rules: set[Rule[ConjunctiveQuery, ConjunctiveQuery]] = set(Dlgp2Parser.instance().parse_rules_from_file(args.file))

    try:
        ucq = next(iter(Dlgp2Parser.instance().parse_union_conjunctive_queries_from_file(args.file)))
    except StopIteration:
        print("The file should contain a UCQ", file=sys.stderr)
        exit()

    if args.mapping:
        schema_predicates: set[Predicate] = {a.predicate for r in rules for a in r.body.atoms}
        target_predicates: set[Predicate] = \
            {a.predicate for r in rules for h in r.head for a in h.atoms}\
            | {a.predicate for q in ucq for a in q.atoms}

        if schema_predicates & target_predicates:
            print("The rule set is not source to target", file=sys.stderr)
            exit()

        print(f'Source predicates: {schema_predicates}')
        print(f'Target predicates: {target_predicates}')

    rewriter = BreadthFirstRewriting()

    printer = None
    if args.mapping:
        def printer(ucq_to_print: UnionConjunctiveQueries, step: int):
            print(f"The UCQ produced at step {step} contains the following CQs:")
            print(*{q for q in ucq_to_print if not {a.predicate for a in q.atoms} & target_predicates}, sep="\n")
            print("------------")

    rewriting_result = rewriter.rewrite(ucq, rules, args.limit, args.verbose, printer).conjunctive_queries
    if args.mapping:
        rewriting_result = {q for q in rewriting_result if not {a.predicate for a in q.atoms} & target_predicates}

    print("<---------------------------------->")
    print(f"The UCQ produced by the breadth first rewriter contains the following CQs:")
    print(*rewriting_result, sep="\n")
    print("<---------------------------------->")


if __name__ == "__main__":
    main()
