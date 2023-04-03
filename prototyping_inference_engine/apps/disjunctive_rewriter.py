import argparse
import sys
from math import inf

from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import BreadthFirstRewriting
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The dlgp file containing the rules and the UCQ to rewrite with them", type=str)
    parser.add_argument("-l", "--limit", help="Limit number of breadth first steps", type=int, default=inf)
    parser.add_argument("-v", "--verbose", help="Print all intermediate steps", action="store_true")
    args = parser.parse_args()

    rules = Dlgp2Parser.instance().parse_rules_from_file(args.file)
    try:
        ucq = next(iter(Dlgp2Parser.instance().parse_union_conjunctive_queries_from_file(args.file)))
    except StopIteration:
        print("The file should contain a UCQ", file=sys.stderr)

    rewriter = BreadthFirstRewriting()

    print("<---------------------------------->")
    print(f"The UCQ produced by the breadth first rewriter contains the following CQs:")
    print(*rewriter.rewrite(ucq, rules, args.limit, args.verbose).conjunctive_queries, sep="\n")
    print("<---------------------------------->")


if __name__ == "__main__":
    main()
