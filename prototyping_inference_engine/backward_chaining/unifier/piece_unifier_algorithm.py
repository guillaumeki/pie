from collections import defaultdict

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.backward_chaining.unifier.piece_unifier import PieceUnifier


class PieceUnifierAlgorithm:
    @staticmethod
    def compute_most_general_full_piece_unifiers(
            query: ConjunctiveQuery,
            rule: Rule[ConjunctiveQuery, ConjunctiveQuery]) -> list[PieceUnifier]:
        result = PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(query, rule)
        for i in range(len(result)):
            mpu = result[i]
            for j in range(len(result)):
                other_mpu = result[j]
                if (mpu is not other_mpu
                        and len(mpu.unified_query_part) < len(mpu.query.atoms)
                        and len(other_mpu.unified_query_part) < len(mpu.query.atoms)
                        and len(mpu.unified_query_part | other_mpu.unified_query_part) != len(mpu.unified_query_part)):
                    merging = mpu.try_to_merge_with(other_mpu)
                    if merging:
                        result.append(merging)
        return result

    @staticmethod
    def compute_most_general_mono_piece_unifiers(
            query: ConjunctiveQuery,
            rule: Rule[ConjunctiveQuery, ConjunctiveQuery]) -> list[PieceUnifier]:
        apu = PieceUnifierAlgorithm._compute_atomic_pre_unifiers(query, rule)
        return PieceUnifierAlgorithm._extend_atomic_pre_unifiers(query, apu)

    @staticmethod
    def _compute_separating_sticky_variables(pre_unifier: PieceUnifier) -> frozenset[Variable]:
        return pre_unifier.separating_variables & pre_unifier.sticky_variables

    @staticmethod
    def _exists_separating_sticky_variables(pre_unifier: PieceUnifier) -> bool:
        return any(v in pre_unifier.separating_variables for v in pre_unifier.sticky_variables)

    @staticmethod
    def _compute_atomic_pre_unifiers(query: ConjunctiveQuery,
                                     rule: Rule[ConjunctiveQuery, ConjunctiveQuery]) -> list[PieceUnifier]:
        atomic_pre_unifiers = []
        for a in rule.head[0].atoms:
            for b in query.atoms:
                if a.predicate == b.predicate:
                    by_position_part = TermPartition(({a[i], b[i]} for i in range(a.predicate.arity)))
                    if by_position_part.is_valid(rule, query):
                        atomic_pre_unifiers.append(PieceUnifier(rule, query, FrozenAtomSet([b]), by_position_part))
        return atomic_pre_unifiers

    @staticmethod
    def _compute_var_to_query_atoms(query: ConjunctiveQuery) -> dict[Variable, MutableAtomSet]:
        v_to_qa = defaultdict(MutableAtomSet)
        for atom in query.atoms:
            for v in atom.variables:
                v_to_qa[v].add(atom)
        return v_to_qa

    @staticmethod
    def _compute_atom_to_atomic_pre_unifiers(apu: list[PieceUnifier]) -> dict[Atom, set[PieceUnifier]]:
        a_to_apu = defaultdict(set)
        for pu in apu:
            a_to_apu[next(iter(pu.unified_query_part))].add(pu)
        return a_to_apu

    @staticmethod
    def _extend_atomic_pre_unifiers(query: ConjunctiveQuery, apu: list[PieceUnifier]) -> list[PieceUnifier]:
        piece_unifiers, to_extend = [], []
        for pre_unifier in apu:
            if PieceUnifierAlgorithm._exists_separating_sticky_variables(pre_unifier):
                to_extend.append(pre_unifier)
            else:
                piece_unifiers.append(pre_unifier)

        if not to_extend:
            return piece_unifiers

        var_to_query_atoms = PieceUnifierAlgorithm._compute_var_to_query_atoms(query)
        atom_to_apu = PieceUnifierAlgorithm._compute_atom_to_atomic_pre_unifiers(apu)

        while to_extend:
            pre_unifier = to_extend.pop()
            if len(pre_unifier.unified_query_part) == 1:
                atom_to_apu[next(iter(pre_unifier.unified_query_part))].remove(pre_unifier)
            neighbour_atoms = {a for sep in pre_unifier.sticky_variables
                               for a in var_to_query_atoms[sep] if a not in pre_unifier.unified_query_part}
            for extended_pu in PieceUnifierAlgorithm._compute_local_extension(pre_unifier,
                                                                              neighbour_atoms,
                                                                              atom_to_apu):
                if PieceUnifierAlgorithm._exists_separating_sticky_variables(extended_pu):
                    to_extend.append(extended_pu)
                else:
                    piece_unifiers.append(extended_pu)

        return piece_unifiers

    @staticmethod
    def _compute_local_extension(pu: PieceUnifier,
                                 neighbour_atoms: set[Atom],
                                 atom_to_apu: dict[Atom, set[PieceUnifier]]) -> list[PieceUnifier]:
        if not neighbour_atoms:
            return [pu]

        to_extend = [pu]
        for atom in neighbour_atoms:
            to_extend_next = []
            for apu in atom_to_apu[atom]:
                for pu_to_ext in to_extend:
                    new_pu = pu_to_ext.aggregate(apu)
                    if new_pu.partition.is_valid(new_pu.rule, new_pu.query):
                        to_extend_next.append(new_pu)
            to_extend = to_extend_next

        return to_extend
