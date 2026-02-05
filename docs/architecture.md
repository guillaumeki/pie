# Architecture

## Overview
Pie is organized around core API types (terms, atoms, queries), evaluators for first-order queries, and parsers for DLGPE/DLGP.

## Key Modules
- `prototyping_inference_engine.api`: core terms, atoms, queries, rules, and fact bases.
- `prototyping_inference_engine.query_evaluation`: evaluator stack for FO queries.
- `prototyping_inference_engine.parser`: DLGPE and DLGP parsers.
- `prototyping_inference_engine.backward_chaining`: query rewriting (UCQ).

## Data Flow
Typical flow: parse facts/query -> build a fact base -> evaluate with the FO query evaluator (or run rewriting for backward chaining).
