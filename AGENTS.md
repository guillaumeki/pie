# AGENTS.md

## Project Overview
Pie (Prototyping Inference Engine) is a Python library for building inference engines. It supports:
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables)
- First-order queries with conjunction, disjunction, negation, and quantifiers
- Backward chaining (query rewriting) - ~90% complete
- Query evaluation against fact bases - ~85% complete
- Data abstraction for heterogeneous sources and multi-source collections
- Forward chaining - not yet implemented
- DLGPE parser with negation, equality, and sections support (IRI resolution not implemented)
- Extended DLGP 2.1 format parser with disjunction support (compatibility)

Requires Python 3.10+ (uses match/case syntax).

## Commands
### Git Remotes
Push to both remotes each time:
- `bitbucket` (Bitbucket)
- `origin` (GitHub, with Bitbucket as an additional push URL)

### Python Execution (Always)
Before running any Python code or unit tests:
1) Create a virtual environment if it does not exist and install dependencies.
2) Activate the virtual environment.
3) Run the Python command/tests.

## Change Process (Always)
For any important change:
1) Propose a plan first, including:
   - Design choices + justification
   - List of files to be modified
   - Type checking with Mypy
   - Fix Mypy errors
2) Wait for user feedback/approval.
3) Once approved, record the plan in `plans/` and reference it in this file.
4) Execute the plan and amend it per user requests.
5) When done, update `CHANGELOG.md` with the date and version if it changed.
6) Record design decisions in `design/<feature_name>.md` with a date and list the file here.
7) Commit and push changes to both `bitbucket` and `origin`.
8) Delete the plan file after changelog and design docs are written.
9) Do not commit or push unless `mypy prototyping_inference_engine` and the full unit test suite have passed.

### Tracked Plans
- None

### Design Docs
- `design/process-templates.md`
- `design/commit-process.md`
- `design/functional-terms.md`
- `design/query-evaluation-structure.md`
- `design/mypy-fixes-2026-02-04.md`
- `design/github-ci.md`
- `design/ci-badge.md`
- `design/mypy-test-gate.md`
- `design/code-quality-tooling.md`

### Process Artifacts
- `plans/PLAN_TEMPLATE.md`
- `design/DESIGN_TEMPLATE.md`
- `process/DEFINITION_OF_DONE.md`
- `process/VERSIONING.md`
- `process/REVIEW_CHECKLIST.md`
- `process/RELEASE_CHECKLIST.md`
- `process/CONVENTIONAL_COMMITS.md`
- `process/COMMIT_TEMPLATE.md`
- `process/COMMIT_POLICY.md`

### Installation
```bash
pip install -e .
```

### Dev Tools
```bash
pip install -r requirements-dev.txt
```

### Tests
```bash
# Run all tests
python3 -m unittest discover -s prototyping_inference_engine -v

# Run a single test file
python3 -m unittest prototyping_inference_engine.api.fact_base.test.test_fact_base -v

# Run a specific test class
python3 -m unittest prototyping_inference_engine.backward_chaining.test.test_breadth_first_rewriting.TestBreadthFirstRewriting
```

### Quality Checks
```bash
ruff check .
ruff format --check .
python3 -m coverage run -m unittest discover -s prototyping_inference_engine -v
python3 -m coverage report -m
bandit -r prototyping_inference_engine -x "prototyping_inference_engine/**/test" -ll
pip-audit
vulture prototyping_inference_engine
radon cc -a -s prototyping_inference_engine
```

### CLI
```bash
# Query rewriter tool
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```

## Architecture Notes
### Core API (`api/`)
- Terms: `Variable`, `Constant` with flyweight caching
- Atoms: predicate + terms, implements `Substitutable`
- Queries: `FOQuery`, `ConjunctiveQuery`, `UnionQuery[Q]`
- Fact bases: `MutableInMemoryFactBase`, `FrozenInMemoryFactBase`
- Rules & ontology: generic rules with disjunctive head support
- Term factories and storage strategies for predicate/term caching

### Data Abstraction (`api/data/`)
- `ReadableData` interface for queryable data sources
- `BasicQuery` with bound positions and answer variables
- `AtomicPattern` and `PositionConstraint` for declaring data source capabilities
- `DataCollection` for integrating multiple data sources

### Query Evaluation (`query_evaluation/`)
Hierarchical evaluator stack with `GenericFOQueryEvaluator` dispatching by formula type.
`QueryEvaluatorRegistry` provides centralized evaluator dispatch by query type.
Evaluators return `Iterator[Substitution]` via `evaluate()` or projected tuples via
`evaluate_and_project()`.

### Backward Chaining (`backward_chaining/`)
`BreadthFirstRewriting` UCQ rewriting algorithm with piece unifiers and rewriting operators.

### Parser (`parser/`)
- DLGPE with disjunction, negation, equality, sections via `DlgpeParser.instance()`
- DLGP 2.1 (extended with disjunction) via `Dlgp2Parser.instance()`

## Formats
DLGPE sample:
```prolog
@facts
person(alice).

@rules
[transitivity] knows(X, Z) :- knows(X, Y), knows(Y, Z).

@queries
?(X) :- knows(alice, X).
```

DLGP sample:
```prolog
q(X); r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

## Code Style
- Comments must always be in English.
## Writing Language
- All content written to any file must be in English.
