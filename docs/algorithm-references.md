# Algorithm References

This page mirrors the in-code reference comments for algorithm entrypoints. Each
section repeats the citations, summaries, properties, and implementation notes
embedded in the corresponding module.

## prototyping_inference_engine/unifier/piece_unifier.py
References:
- "A Sound and Complete Backward Chaining Algorithm for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://ceur-ws.org/Vol-920/paper17.pdf
- "Sound, Complete, and Minimal Query Rewriting for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://www.ijcai.org/Proceedings/13/Papers/292.pdf

Summary:
Piece-unifiers restrict unification between a conjunctive query and a rule head
to avoid unsound bindings of existential variables. They track a "piece" of the
query, a partition of terms, and frontier instantiations to ensure correctness.

Properties used here:
- Soundness and completeness of piece-unification in backward chaining.
- Separating and sticky variables characterize admissible partitions.

Implementation notes:
This class encodes the piece-unifier structure and the admissibility checks
described in the papers, serving as the core artifact manipulated by the
rewriting algorithms.

## prototyping_inference_engine/unifier/piece_unifier_algorithm.py
References:
- "A Sound and Complete Backward Chaining Algorithm for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://ceur-ws.org/Vol-920/paper17.pdf
- "Sound, Complete, and Minimal Query Rewriting for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://www.ijcai.org/Proceedings/13/Papers/292.pdf

Summary:
The piece-unifier algorithm enumerates admissible partitions between a query
and a rule head, producing the maximal set of piece-unifiers usable for
rewriting. This enumeration is the core step for backward chaining.

Properties used here:
- Completeness of enumerating all piece-unifiers for a CQ/rule pair.
- Minimality of UCQ rewritings when combined with redundancy elimination.

Implementation notes:
This implementation follows the construction steps described in the papers,
including admissibility checks and combination of compatible pre-unifiers.

## prototyping_inference_engine/unifier/disjunctive_piece_unifier.py
References:
- "Query rewriting with disjunctive existential rules and mappings" — Michel Leclere, Marie-Laure Mugnier, Guillaume Perution-Kihli. Link: https://doi.org/10.24963/kr.2023/59

Summary:
Disjunctive piece-unifiers extend piece-unifiers to rules with disjunctive
heads by combining unifiers for each disjunct and tracking a global partition.

Properties used here:
- Soundness and completeness of disjunctive unification for disjunctive heads.
- Compatibility constraints ensure correct handling of shared frontier terms.

Implementation notes:
This class stores a tuple of piece-unifiers (one per disjunct) and builds the
associated partition/substitution used during disjunctive rewriting.

## prototyping_inference_engine/unifier/disjunctive_piece_unifier_algorithm.py
References:
- "Query rewriting with disjunctive existential rules and mappings" — Michel Leclere, Marie-Laure Mugnier, Guillaume Perution-Kihli. Link: https://doi.org/10.24963/kr.2023/59

Summary:
The algorithm builds disjunctive piece-unifiers by combining piece-unifiers
computed for each disjunctive head, preserving consistency across shared
variables and partitions.

Properties used here:
- Soundness and completeness of disjunctive unifier enumeration.
- Termination for rule sets where the underlying rewriting terminates.

Implementation notes:
This module implements the construction of partial disjunctive unifiers and
their systematic extension, as described in the KR 2023 paper.

## prototyping_inference_engine/backward_chaining/breadth_first_rewriting.py
References:
- "A Sound and Complete Backward Chaining Algorithm for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://ceur-ws.org/Vol-920/paper17.pdf
- "Sound, Complete, and Minimal Query Rewriting for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://www.ijcai.org/Proceedings/13/Papers/292.pdf

Summary:
Breadth-first UCQ rewriting iteratively applies rewriting steps to expand a
union of conjunctive queries while removing redundancies. The papers provide
the correctness and minimality results for this style of backward chaining.

Properties used here:
- Soundness and completeness of UCQ rewriting for existential rules.
- Minimality with respect to redundancy elimination and subsumption tests.

Implementation notes:
This class drives the step-wise UCQ rewriting loop and uses a redundancy
cleaner consistent with the minimal rewriting guarantees from the papers.

## prototyping_inference_engine/backward_chaining/ucq_rewriting_algorithm.py
References:
- "A Sound and Complete Backward Chaining Algorithm for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://ceur-ws.org/Vol-920/paper17.pdf
- "Sound, Complete, and Minimal Query Rewriting for Existential Rules" — Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo. Link: https://www.ijcai.org/Proceedings/13/Papers/292.pdf

Summary:
UCQ rewriting is the backward chaining technique for existential rules that
repeatedly replaces query atoms using rule heads to produce a union of CQs.

Properties used here:
- Soundness/completeness of UCQ rewriting relative to the rule set.
- Minimality when combined with redundancy elimination.

Implementation notes:
This abstract interface captures the UCQ rewriting contract implemented by
concrete algorithms (e.g., breadth-first rewriting).

## prototyping_inference_engine/backward_chaining/rewriting_operator/without_aggregation_rewriting_operator.py
References:
- "Query rewriting with disjunctive existential rules and mappings" — Michel Leclere, Marie-Laure Mugnier, Guillaume Perution-Kihli. Link: https://doi.org/10.24963/kr.2023/59

Summary:
This rewriting operator applies disjunctive piece-unifiers to transform UCQs
when rules have disjunctive heads, producing a UCQ that preserves answers.

Properties used here:
- Soundness and completeness of disjunctive rewriting.
- Termination guarantees under the same conditions as the underlying algorithm.

Implementation notes:
This operator implements the disjunctive rewriting step from the KR 2023 paper
by constructing new CQs from disjunctive piece-unifiers.

## prototyping_inference_engine/grd/grd.py
References:
- "Extending Decidable Cases for Rules with Existential Variables" — Jean-Francois Baget, Michel Leclere, Marie-Laure Mugnier, Eric Salvat. Link: https://www.ijcai.org/Proceedings/09/Papers/323.pdf

Summary:
The GRD captures dependencies between existential rules via unification
conditions on heads and bodies. It is used to characterize decidable classes
and to drive stratification and evaluation strategies.

Properties used here:
- Dependency edges encode potential rule triggering.
- GRD-based criteria enable reasoning about termination and stratification.

Implementation notes:
This module constructs dependency edges using piece-unification and exposes
them for stratification and evaluation procedures.

## prototyping_inference_engine/grd/dependency_checker.py
References:
- "Extending Decidable Cases for Rules with Existential Variables" — Jean-Francois Baget, Michel Leclere, Marie-Laure Mugnier, Eric Salvat. Link: https://www.ijcai.org/Proceedings/09/Papers/323.pdf

Summary:
GRD dependency checkers refine the basic dependency relation by validating
whether a unifier yields a productive edge under specific conditions.

Properties used here:
- Dependency validation aligns with GRD criteria used for decidability checks.

Implementation notes:
The ProductivityChecker mirrors the criteria described in the GRD paper to
filter dependencies for stratification and evaluation planning.

## prototyping_inference_engine/grd/stratification.py
References:
- "Extending Decidable Cases for Rules with Existential Variables" — Jean-Francois Baget, Michel Leclere, Marie-Laure Mugnier, Eric Salvat. Link: https://www.ijcai.org/Proceedings/09/Papers/323.pdf
- "The well-founded semantics for general logic programs" — Allen Van Gelder, Kenneth A. Ross, John S. Schlipf. Link: https://doi.org/10.1145/115040.115041
- "On a routing problem" — Richard Bellman. Link: https://doi.org/10.1090/qam/102435
- "Network Flow Theory" — L. R. Ford Jr. Link: https://apps.dtic.mil/sti/pdfs/AD0602524.pdf
- "A Note on a Simple Algorithm for Generating a Topological Ordering of a Directed Acyclic Graph" — Arthur B. Kahn. Link: https://doi.org/10.1145/368996.369025

Summary:
Stratification partitions rules into ordered strata based on GRD dependencies
and negation constraints. SCC-based ordering and shortest-path formulations
are used to derive minimal or single-evaluation strata.

Properties used here:
- Stratified negation forbids negative cycles (well-founded semantics).
- Bellman-Ford shortest paths compute strata levels under weighted edges.
- Kahn's algorithm provides topological ordering for SCC condensation graphs.

Implementation notes:
This module computes SCCs (via igraph), applies Bellman-Ford for weighted
stratification variants, and topologically orders SCCs for stratified execution.

## prototyping_inference_engine/utils/graph/topological_sort.py
References:
- "A Note on a Simple Algorithm for Generating a Topological Ordering of a Directed Acyclic Graph" — Arthur B. Kahn. Link: https://doi.org/10.1145/368996.369025

Summary:
Kahn's algorithm iteratively removes nodes with zero in-degree to produce a
topological ordering of a DAG.

Properties used here:
- Linear-time topological sorting in the size of nodes plus edges.
- Detection of cycles when not all nodes can be ordered.

Implementation notes:
This implementation keeps a priority queue to provide deterministic ordering
when multiple nodes are available.

## prototyping_inference_engine/utils/partition.py
References:
- "Efficiency of a Good But Not Linear Set Union Algorithm" — Robert E. Tarjan. Link: https://doi.org/10.1145/360680.360685

Summary:
Union-find maintains a partition of a set with near-constant-time union and
find operations using path compression and union-by-rank heuristics.

Properties used here:
- Amortized inverse-Ackermann complexity for union/find operations.

Implementation notes:
This module implements a union-find based partition structure that is used
throughout the codebase for term equivalence classes.

## prototyping_inference_engine/api/atom/set/homomorphism/homomorphism_algorithm.py
References:
- "Foundations of Databases" — Serge Abiteboul, Richard Hull, Victor Vianu. Link: https://dl.acm.org/doi/book/10.5555/64510

Summary:
Conjunctive query answering can be characterized by the existence of a
homomorphism from the query body to the database instance.

Properties used here:
- Homomorphism-based semantics for conjunctive queries.

Implementation notes:
This abstract interface defines the homomorphism computation contract used by
CQ evaluation and query rewriting components.

## prototyping_inference_engine/api/atom/set/homomorphism/backtrack/naive_backtrack_homomorphism_algorithm.py
References:
- "Foundations of Databases" — Serge Abiteboul, Richard Hull, Victor Vianu. Link: https://dl.acm.org/doi/book/10.5555/64510

Summary:
Backtracking homomorphism search enumerates substitutions that map a CQ body
into a fact base, which is the core of conjunctive query evaluation.

Properties used here:
- Completeness of backtracking for enumerating homomorphisms.
- Correctness of homomorphism-based CQ semantics.

Implementation notes:
This module implements a straightforward backtracking search with indexing and
scheduling heuristics for atom ordering.

## prototyping_inference_engine/query_evaluation/evaluator/fo_query/fo_query_evaluator.py
References:
- "Foundations of Databases" — Serge Abiteboul, Richard Hull, Victor Vianu. Link: https://dl.acm.org/doi/book/10.5555/64510

Summary:
FO queries are evaluated by interpreting their formulas over a database
instance, with conjunctive queries handled via homomorphisms.

Properties used here:
- Standard FO semantics and CQ homomorphism characterization.

Implementation notes:
This base class defines the evaluator interface used to dispatch on formula
types in the query evaluation stack.

## prototyping_inference_engine/query_evaluation/evaluator/fo_query/fo_query_evaluators.py
References:
- "Foundations of Databases" — Serge Abiteboul, Richard Hull, Victor Vianu. Link: https://dl.acm.org/doi/book/10.5555/64510

Summary:
FO query evaluation decomposes formulas by logical connectives and quantifiers,
reducing to conjunction evaluation and homomorphism checks for atoms.

Properties used here:
- Standard FO semantics for conjunction, disjunction, negation, and quantifiers.

Implementation notes:
This module provides the concrete evaluator classes that follow the FO
semantics described in the reference.

## prototyping_inference_engine/query_evaluation/evaluator/query/conjunctive_query_evaluator.py
References:
- "Foundations of Databases" — Serge Abiteboul, Richard Hull, Victor Vianu. Link: https://dl.acm.org/doi/book/10.5555/64510

Summary:
Conjunctive query answering reduces to finding homomorphisms from the query
body to the database instance.

Properties used here:
- Correctness of CQ evaluation via homomorphisms.

Implementation notes:
This evaluator delegates CQ evaluation to the FO query evaluator stack.

## prototyping_inference_engine/query_evaluation/evaluator/query/union_query_evaluator.py
References:
- "Foundations of Databases" — Serge Abiteboul, Richard Hull, Victor Vianu. Link: https://dl.acm.org/doi/book/10.5555/64510

Summary:
Unions of conjunctive queries represent disjunctions and are evaluated by
taking the union of answers of each disjunct.

Properties used here:
- Correctness of UCQ evaluation as set-union of CQ answers.

Implementation notes:
This evaluator delegates each sub-query to the registry and merges results.

## prototyping_inference_engine/io/parsers/dlgpe/dlgpe_parser.py
References:
- "DLGP: An Extended Datalog Syntax for Existential Rules and Datalog±" — Jean-Francois Baget, Mariano Rodriguez Gutierrez, Michel Leclere, Marie-Laure Mugnier, Swan Rocher, Marie Sipieter. Link: https://graphik-team.github.io/graal/doc/dlgp/dlgp.pdf

Summary:
DLGP/DLGPE define a concrete syntax for existential rules, facts, and queries.
This parser implements the DLGP-based grammar with DLGPE extensions.

Properties used here:
- Conformance to the DLGP syntax for rules, facts, and queries.
- Extension points for DLGPE-specific constructs.

Implementation notes:
The grammar and transformer follow the DLGP specification and expose a subset
aligned with PIE capabilities.

## prototyping_inference_engine/io/writers/dlgpe_writer.py
References:
- "DLGP: An Extended Datalog Syntax for Existential Rules and Datalog±" — Jean-Francois Baget, Mariano Rodriguez Gutierrez, Michel Leclere, Marie-Laure Mugnier, Swan Rocher, Marie Sipieter. Link: https://graphik-team.github.io/graal/doc/dlgp/dlgp.pdf

Summary:
DLGP/DLGPE define a concrete syntax for existential rules, facts, and queries.
This writer serializes PIE structures to that syntax.

Properties used here:
- Conformance to DLGP syntax for rules, facts, queries, and directives.

Implementation notes:
The serializer mirrors the DLGP specification and PIE's DLGPE extensions.

## prototyping_inference_engine/io/parsers/rdf/rdf_parser.py
References:
- "RDF 1.1 Concepts and Abstract Syntax" — Richard Cyganiak, David Wood, Markus Lanthaler. Link: https://www.w3.org/TR/rdf11-concepts/

Summary:
RDF defines a graph-based data model with triples that can be parsed from
concrete syntaxes and translated into application-specific representations.

Properties used here:
- Standard RDF graph semantics for triples and IRIs.

Implementation notes:
This parser uses rdflib to parse RDF and maps triples into atoms via PIE's
translation modes.

## prototyping_inference_engine/io/writers/rdf/rdf_writer.py
References:
- "RDF 1.1 Concepts and Abstract Syntax" — Richard Cyganiak, David Wood, Markus Lanthaler. Link: https://www.w3.org/TR/rdf11-concepts/

Summary:
RDF defines a graph-based data model with triples that can be serialized into
standard syntaxes such as Turtle.

Properties used here:
- Standard RDF graph semantics for triples and IRIs.

Implementation notes:
This writer uses rdflib to serialize triples produced by PIE translators.

## prototyping_inference_engine/rdf/translator.py
References:
- "RDF 1.1 Concepts and Abstract Syntax" — Richard Cyganiak, David Wood, Markus Lanthaler. Link: https://www.w3.org/TR/rdf11-concepts/

Summary:
RDF graphs are sets of triples with IRIs, literals, and blank nodes; translators
map between RDF terms and application-specific representations.

Properties used here:
- RDF term model and graph semantics.

Implementation notes:
This module implements translation modes that map RDF triples to PIE atoms.
