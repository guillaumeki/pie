from dataclasses import dataclass
from functools import cached_property

from api.atom.atom import Atom
from api.atom.atom_set import AtomSet
from api.atom.frozen_atom_set import FrozenAtomSet
from api.atom.term.term_partition import TermPartition
from api.atom.term.variable import Variable
from api.ontology.rule.rule import Rule
from api.query.conjunctive_query import ConjunctiveQuery
from api.substitution.substitution import Substitution


@dataclass(frozen=True)
class PieceUnifier:
     rule: Rule[ConjunctiveQuery, ConjunctiveQuery]
     query: ConjunctiveQuery
     unified_query_part: FrozenAtomSet[Atom]
     partition: TermPartition

     @cached_property
     def associated_substitution(self) -> Substitution:
          return self.partition.associated_substitution(self.query)

     def is_compatible_with(self, other: "PieceUnifier"):
          if any(atom in other.unified_query_part for atom in self.unified_query_part):
               return False

          part = TermPartition(self.partition)
          part.join(other.partition)

          return part.is_admissible

     def aggregate(self, other: "PieceUnifier") -> "PieceUnifier":
          unified_query_part = self.unified_query_part | other.unified_query_part
          partition = TermPartition(self.partition)
          partition.join(other.partition)
          return PieceUnifier(Rule.aggregate_conjunctive_rules(self.rule, other.rule),
                              self.query,
                              unified_query_part,
                              partition)

     @cached_property
     def not_unified_part(self) -> FrozenAtomSet:
          return FrozenAtomSet(self.query.atoms - self.unified_query_part)

     @cached_property
     def separating_variables(self) -> frozenset[Variable]:
          return frozenset(v for v in self.unified_query_part.variables if v in self.not_unified_part.variables)

     @cached_property
     def sticky_variables(self) -> frozenset[Variable]:
          return frozenset(v for cls in self.partition if any(t in self.rule.existential_variables for t in cls)
                  for v in cls if v in self.unified_query_part.variables)
