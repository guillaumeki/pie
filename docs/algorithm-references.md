# Algorithm References

This page documents the main algorithms implemented in PIE. Each section is
organized by **concept/algorithm**, explains the idea in prose, states the
properties used in the code, and points to where the implementation lives. The
references include full author lists and clickable links. Author names link to a
personal page when available; otherwise to Google Scholar or DBLP.

## Piece-Unifiers and Minimal UCQ Rewriting

**Summary**
Piece-unifiers are a restricted form of unification for existential rules. They
identify a "piece" of the query that must be rewritten together, preventing
unsound bindings of existential variables. This restriction preserves soundness
and completeness while enabling minimal UCQ rewriting when the rewriting set is
finite. PIE uses piece-unifiers to drive backward chaining and to keep rewriting
operators aligned with the theoretical guarantees from the literature.

**Key properties used in PIE**
- Soundness and completeness of piece-unifier based rewriting.
- Minimality of UCQ rewritings when a finite rewriting exists.
- Correct handling of separating and sticky variables through admissible partitions.

**Implementation in PIE**
- `prototyping_inference_engine/unifier/piece_unifier.py`
- `prototyping_inference_engine/unifier/piece_unifier_algorithm.py`
- `prototyping_inference_engine/backward_chaining/breadth_first_rewriting.py`
- `prototyping_inference_engine/backward_chaining/ucq_rewriting_algorithm.py`

**References**
- “A Sound and Complete Backward Chaining Algorithm for Existential Rules.”  
  [Mélanie König](https://dblp.org/search?q=M%C3%A9lanie%20K%C3%B6nig),
  [Michel Leclère](https://www.lirmm.fr/~leclere/),
  [Marie-Laure Mugnier](https://www.lirmm.fr/~mugnier/),
  [Michaël Thomazo](https://prairie-institute.fr/chairs/thomazo-michael/).  
  Publication: [https://www.lirmm.fr/~mugnier/ArticlesPostscript/FullTR-RR2012KonigLeclereMugnierThomazoV2.pdf](https://www.lirmm.fr/~mugnier/ArticlesPostscript/FullTR-RR2012KonigLeclereMugnierThomazoV2.pdf)
- “Sound, Complete, and Minimal Query Rewriting for Existential Rules.”  
  [Mélanie König](https://dblp.org/search?q=M%C3%A9lanie%20K%C3%B6nig),
  [Michel Leclère](https://www.lirmm.fr/~leclere/),
  [Marie-Laure Mugnier](https://www.lirmm.fr/~mugnier/),
  [Michaël Thomazo](https://prairie-institute.fr/chairs/thomazo-michael/).  
  Publication: [https://iccl.inf.tu-dresden.de/web/Inproceedings4058/en](https://iccl.inf.tu-dresden.de/web/Inproceedings4058/en)

## Disjunctive Rewriting with Disjunctive Piece-Unifiers

**Summary**
Disjunctive piece-unifiers extend piece-unifiers to rules whose heads are
(disjunctions of) conjunctive heads. The rewriting operator applies one
piece-unifier per head disjunct and merges them through a shared partition,
ensuring consistent frontier instantiations across disjuncts. PIE relies on
this operator to perform sound and complete UCQ rewriting under disjunctive
existential rules, with minimality when a finite rewriting exists.

**Key properties used in PIE**
- Soundness and completeness of the disjunctive rewriting operator.
- Minimality of breadth-first UCQ rewriting when it terminates.
- Correct propagation of shared frontier instantiations across disjuncts.

**Implementation in PIE**
- `prototyping_inference_engine/unifier/disjunctive_piece_unifier.py`
- `prototyping_inference_engine/unifier/disjunctive_piece_unifier_algorithm.py`
- `prototyping_inference_engine/backward_chaining/rewriting_operator/without_aggregation_rewriting_operator.py`

**References**
- “Query Rewriting with Disjunctive Existential Rules and Mappings.”  
  [Michel Leclère](https://www.lirmm.fr/~leclere/),
  [Marie-Laure Mugnier](https://www.lirmm.fr/~mugnier/),
  [Guillaume Pérution-Kihli](https://dblp.org/search?q=Guillaume%20P%C3%A9rution-Kihli).  
  Publication: [https://proceedings.kr.org/2023/42/](https://proceedings.kr.org/2023/42/)

## Graph of Rule Dependencies (GRD)

**Summary**
A GRD encodes potential triggering relationships between rules by analyzing
unifications between rule heads and bodies. It is used to reason about rule
interaction, decidability, and evaluation strategies, and it provides the base
structure for stratification under negation.

**Key properties used in PIE**
- Dependency edges encode potential rule triggering.
- GRD-based criteria can be used to reason about termination and stratification.

**Implementation in PIE**
- `prototyping_inference_engine/grd/grd.py`
- `prototyping_inference_engine/grd/dependency_checker.py`

**References**
- “Extending Decidable Cases for Rules with Existential Variables.”  
  [Jean-François Baget](https://www.lirmm.fr/~baget/),
  [Michel Leclère](https://www.lirmm.fr/~leclere/),
  [Marie-Laure Mugnier](https://www.lirmm.fr/~mugnier/),
  [Éric Salvat](https://dblp.org/search?q=Eric%20Salvat).  
  Publication: [https://www.ijcai.org/Proceedings/09/Papers/323.pdf](https://www.ijcai.org/Proceedings/09/Papers/323.pdf)

## Stratification with Negation

**Summary**
Stratification orders rules into strata so that negative dependencies only point
to strictly lower strata, preventing negative cycles. PIE supports SCC-based
stratification and weighted variants that compute minimal or single-evaluation
strata where possible, which is crucial for controlled evaluation under
negation.

**Key properties used in PIE**
- Negative cycles are forbidden in stratified programs.
- SCC condensation yields a DAG that can be topologically ordered.
- Weighted shortest paths can compute strata levels under constraint systems.

**Implementation in PIE**
- `prototyping_inference_engine/grd/stratification.py`
- `prototyping_inference_engine/utils/graph/topological_sort.py`

**References**
- “The well-founded semantics for general logic programs.”  
  [Allen Van Gelder](https://dblp.org/search?q=Allen%20Van%20Gelder),
  [Kenneth A. Ross](https://dblp.org/search?q=Kenneth%20A.%20Ross),
  [John S. Schlipf](https://dblp.org/search?q=John%20S.%20Schlipf).  
  Publication: [https://doi.org/10.1145/115040.115041](https://doi.org/10.1145/115040.115041)
- “On a routing problem.”  
  [Richard Bellman](https://dblp.org/search?q=Richard%20Bellman).  
  Publication: [https://doi.org/10.1090/qam/102435](https://doi.org/10.1090/qam/102435)
- “Network Flow Theory.”  
  [L. R. Ford Jr.](https://dblp.org/search?q=L.%20R.%20Ford).  
  Publication: [https://apps.dtic.mil/sti/pdfs/AD0602524.pdf](https://apps.dtic.mil/sti/pdfs/AD0602524.pdf)
- “A Note on a Simple Algorithm for Generating a Topological Ordering of a Directed Acyclic Graph.”  
  [Arthur B. Kahn](https://dblp.org/search?q=Arthur%20B.%20Kahn).  
  Publication: [https://doi.org/10.1145/368996.369025](https://doi.org/10.1145/368996.369025)

## Backtracking Homomorphism Search for Conjunctive Queries

**Summary**
Conjunctive query answering can be characterized by the existence of a
homomorphism from the query body to a fact base. PIE uses a backtracking search
with indexing and scheduling to enumerate homomorphisms and build substitutions.
This is the core evaluation strategy behind the backtracking FO query evaluator
and the prepared backtracking CQ implementation.

**Key properties used in PIE**
- Completeness of backtracking enumeration for homomorphisms.
- Correctness of homomorphism-based CQ semantics.

**Implementation in PIE**
- `prototyping_inference_engine/api/atom/set/homomorphism/backtrack/naive_backtrack_homomorphism_algorithm.py`
- `prototyping_inference_engine/query_evaluation/evaluator/fo_query/prepared_queries.py`
- `prototyping_inference_engine/query_evaluation/evaluator/fo_query/fo_query_evaluators.py`

**References**
- “Foundations of Databases.”  
  [Serge Abiteboul](https://dblp.org/search?q=Serge%20Abiteboul),
  [Richard Hull](https://dblp.org/search?q=Richard%20Hull),
  [Victor Vianu](https://dblp.org/search?q=Victor%20Vianu).  
  Publication: [https://dl.acm.org/doi/book/10.5555/64510](https://dl.acm.org/doi/book/10.5555/64510)
- “Extensions of Simple Conceptual Graphs: The Complexity of Rules and Constraints.”  
  [Jean-François Baget](https://www.lirmm.fr/~baget/),
  [Marie-Laure Mugnier](https://www.lirmm.fr/~mugnier/).  
  Publication: [https://doi.org/10.1613/jair.918](https://doi.org/10.1613/jair.918)

## Union-Find for Term Partitions

**Summary**
Term partitions are implemented via union-find to maintain equivalence classes
used by unification and equality reasoning. PIE relies on union-find for
near-constant-time merges and representative queries across the codebase.

**Key properties used in PIE**
- Amortized inverse-Ackermann complexity for union/find operations.

**Implementation in PIE**
- `prototyping_inference_engine/utils/partition.py`

**References**
- “Efficiency of a Good But Not Linear Set Union Algorithm.”  
  [Robert E. Tarjan](https://dblp.org/search?q=Robert%20E.%20Tarjan).  
  Publication: [https://doi.org/10.1145/360680.360685](https://doi.org/10.1145/360680.360685)

## DLGP/DLGPE Syntax

**Summary**
DLGP (and its DLGPE extensions) provide a textual syntax for facts, rules,
negative constraints, and queries in the existential-rule framework. PIE’s
parser and writer implement a compatible subset of this syntax.

**Implementation in PIE**
- `prototyping_inference_engine/io/parsers/dlgpe/dlgpe_parser.py`
- `prototyping_inference_engine/io/writers/dlgpe_writer.py`

**References**
- “DLGP: An Extended Datalog Syntax (Version 2.1).”  
  [GraphIK Team](https://team.inria.fr/graphik/).  
  Publication: [https://graphik-team.github.io/graal/doc/dlgp](https://graphik-team.github.io/graal/doc/dlgp)

## RDF Translation and RDF I/O

**Summary**
RDF defines a graph data model based on triples (subject, predicate, object).
PIE translates RDF triples to atoms using configurable translation modes and
reads/writes RDF through rdflib, preserving RDF semantics while exposing atoms
to the inference engine.

**Implementation in PIE**
- `prototyping_inference_engine/rdf/translator.py`
- `prototyping_inference_engine/io/parsers/rdf/rdf_parser.py`
- `prototyping_inference_engine/io/writers/rdf/rdf_writer.py`

**References**
- “RDF 1.1 Concepts and Abstract Syntax.”  
  [Richard Cyganiak](https://dblp.org/search?q=Richard%20Cyganiak),
  [David Wood](https://dblp.org/search?q=David%20Wood),
  [Markus Lanthaler](https://dblp.org/search?q=Markus%20Lanthaler).  
  Publication: [https://www.w3.org/TR/rdf11-concepts/](https://www.w3.org/TR/rdf11-concepts/)
