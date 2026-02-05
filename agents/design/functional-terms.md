# Design: Functional Terms (Python-Backed)
Date: 2026-02-04
Status: Accepted

## Context
DLGPE functional terms need evaluation support during query execution. Functions may operate
either on Term objects or on native Python values derived from Literals. Some functions can
be evaluated with partial bindings (e.g., add(a, b, result) when any two positions are bound),
which requires scheduler awareness of required inputs.

## Decision
- Introduce a Python-backed readable data source (`PythonFunctionReadable`) that registers
  functions by name with a per-function mode ("terms" or "python"), arity, required positions,
  and optional `min_bound` + solver for partial bindings.
- Represent functional terms in the AST as `FunctionTerm`, and rewrite them at evaluation time
  into computed atoms using a reserved predicate prefix (`__func__<name>`).
- Use a shared rewrite helper so both atomic and conjunction evaluators expand functional terms.
- Allow the backtracking scheduler to select evaluable formulas based on `ReadableData.can_evaluate`,
  so function atoms with binding constraints are scheduled only when evaluable.

## Rationale
This keeps evaluation homogeneous (everything becomes an atom query), supports both Term-based
and Python-native functions, and enables partial evaluation via a solver without introducing
special-case execution paths in every evaluator.

## Alternatives Considered
- Directly evaluate functional terms inside the atom evaluator without rewriting — rejected
  because it duplicates evaluation logic and breaks the uniform data-source abstraction.
- Only support fully bound input arguments — rejected because it prevents common patterns like
  inverse arithmetic with partial bindings.

## Consequences
- Positive: Unified evaluation model (computed atoms), flexible function modes, and support
  for partial bindings via `min_bound` + solver.
- Negative: Requires a reserved predicate namespace and an extra rewrite step during evaluation.

## Follow-ups
- Add documentation examples for registering functions and using partial bindings.
