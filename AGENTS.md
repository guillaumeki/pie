# AGENTS.md

## Project Overview
Pie (Prototyping Inference Engine) is a Python library for building inference engines. It supports:
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables)
- First-order queries with conjunction, disjunction, negation, and quantifiers
- Backward chaining (query rewriting) - ~90% complete
- Query evaluation against fact bases - ~85% complete
- Data abstraction for heterogeneous sources and multi-source collections
- Forward chaining - not yet implemented
- DLGPE parser with negation, equality, sections support, and IRI resolution

Requires Python 3.10+ (uses match/case syntax).

## Commands
### Git Remotes
Push to both remotes each time:
- `bitbucket` (Bitbucket)
- `origin` (GitHub, with Bitbucket as an additional push URL)

### Quality Commands
```bash
ruff check .
ruff format --check .
python3 -m coverage run -m unittest discover -s prototyping_inference_engine -t . -v
python3 -m coverage report -m
bandit -r prototyping_inference_engine -x "prototyping_inference_engine/**/test,__pycache__" -ll
pip-audit --cache-dir .cache/pip-audit
vulture --config pyproject.toml prototyping_inference_engine
radon cc -a -s prototyping_inference_engine
```

### Python Execution (Always)
Before running any Python code or unit tests:
1) Create a virtual environment if it does not exist and install dependencies.
2) Activate the virtual environment.
3) Run the Python command/tests.

### Before Push (Always)
Run the following in order before any commit/push:
1) `mypy prototyping_inference_engine`
2) `python3 -m unittest discover -s prototyping_inference_engine -t . -v`
3) `ruff check .`
4) `ruff format --check .`
5) `python3 -m coverage run -m unittest discover -s prototyping_inference_engine -t . -v`
6) `python3 -m coverage report -m`
7) `bandit -r prototyping_inference_engine -x "prototyping_inference_engine/**/test,__pycache__" -ll`
8) `pip-audit --cache-dir .cache/pip-audit`
9) `vulture --config pyproject.toml prototyping_inference_engine` (informational)
10) `radon cc -a -s prototyping_inference_engine` (informational)

## Change Process (Always)
For any important change:
1) Propose a plan first, including:
   - Design choices + justification
   - SOLID alignment (if relevant)
   - How the proposed module hierarchy follows Python standards (see "Python Module Hierarchy Standards" below)
   - List of files to be modified
   - Type checking with Mypy
   - Fix Mypy errors
   - Unit tests to add (when relevant)
2) Wait for user feedback/approval.
3) Once approved, record the plan in `agents/plans/` and reference it in this file.
4) Execute the plan and amend it per user requests.
5) Update the project version (e.g., `pyproject.toml`) when the change is release-worthy.
6) When done, update `CHANGELOG.md` with the date and version if it changed.
7) Record design decisions in `agents/design/<feature_name>.md` with a date and list the file here.
8) Update documentation (README and `docs/`) after the design docs so docs stay current.
9) Build docs locally with `mkdocs build --clean` to verify documentation changes will not break CI.
10) Write unit tests when relevant.
11) When a new version is justified, create and push a git tag `v<version>` that matches `pyproject.toml`.
12) Commit and push changes to both `bitbucket` and `origin`.
13) Delete the plan file after changelog, design docs, and documentation updates are written.
14) Do not commit or push unless `mypy prototyping_inference_engine` and the full unit test suite have passed.
15) Every documentation example must be covered by a unit test.
16) Every documentation code block must be surrounded by explanatory text.
17) Tests must never use `str(...)` or `repr(...)` in assertions or comparisons (avoid brittle expectations).
18) Tests must be deterministic (no reliance on iteration order from sets/dicts; always sort or normalize).

## Python Module Hierarchy Standards
- This project uses a flat layout (importable packages at repo root). Do not introduce a `src/` layout unless the plan explicitly justifies it and includes required packaging changes. (https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- In general, use either a flat layout (importable packages at repo root) or a src layout (importable packages under `src/`). The src layout is standard practice to avoid accidental imports from the working directory and to ensure only intended packages are importable; it typically requires an editable install for development. (https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- Keep `pyproject.toml` at the project root as the canonical packaging and tooling configuration file, including `[build-system]` and `[project]` metadata when applicable. (https://packaging.python.org/guides/writing-pyproject-toml/)
- Keep a README file at the project root (commonly `README.md`, `README.rst`, or `README.txt`) for project description and packaging metadata. (https://packaging.python.org/guides/making-a-pypi-friendly-readme/)
- Name modules and packages using short, all-lowercase names; underscores are acceptable in module names for readability, while package underscores are discouraged. (https://peps.python.org/pep-0008/)
- Module and package names used with `import` must be valid identifiers; within ASCII this means letters and underscores, with digits allowed only after the first character. (https://docs.python.org/3/reference/lexical_analysis.html)
- A module is a `.py` file containing Python definitions and statements; the module name is the filename without the `.py` suffix. Organize code so each logical module maps to one file. (https://docs.python.org/3/tutorial/modules.html)
- Use packages and subpackages (dotted module names) to structure the module namespace and group related modules; a package can contain subpackages that further group related modules. (https://docs.python.org/3/tutorial/modules.html)
- Regular packages are directories containing `__init__.py`; `__init__.py` can be empty or perform package initialization and define `__all__` for explicit exported submodules. (https://docs.python.org/3/tutorial/modules.html)
- For `import a.b.c`, each item except the last must be a package; the last item can be a module or a package. Ensure intermediate path segments are packages (directories) when designing the hierarchy. (https://docs.python.org/3/tutorial/modules.html)
- Use packages (directories) and subpackages (nested directories) to structure modules; regular packages are directories containing `__init__.py`. (https://docs.python.org/3.13/tutorial/modules.html)
- Treat a directory as a regular package only when it contains `__init__.py`, unless you are intentionally using namespace packages (PEP 420). (https://docs.python.org/3.13/tutorial/modules.html) (https://peps.python.org/pep-0420/)
- Avoid accidentally packaging `tests/` or `docs/` by using flat-layout discipline or explicit include/exclude configuration. (https://setuptools.pypa.io/en/stable/userguide/package_discovery.html)

## Common Project Layout Practices (Imposed)
- Keep a clear top-level structure with key project files at the root (at least `pyproject.toml`, `README.md`, and `LICENSE` when applicable). (https://realpython.com/ref/best-practices/project-layout/)
- Do not leave many Python files at the repository root. Put importable code in a package directory (named after the project), and group related modules under subpackages that reflect logical domains. (https://realpython.com/ref/best-practices/project-layout/)
- If the project has many source files, create a subdirectory named after the project and place the code there. (https://wiki.python.org/moin/ProjectFileAndDirectoryLayout)
- Place tests in a `tests/` directory (even for small projects). (https://wiki.python.org/moin/ProjectFileAndDirectoryLayout) (https://realpython.com/ref/best-practices/project-layout/)
- If the project includes executable scripts, put them in `bin/` (or `scripts/`) and avoid the `.py` suffix for user-facing executables. (https://wiki.python.org/moin/ProjectFileAndDirectoryLayout) (https://realpython.com/ref/best-practices/project-layout/)
- If the project has documentation, place it under `docs/`. (https://wiki.python.org/moin/ProjectFileAndDirectoryLayout) (https://realpython.com/ref/best-practices/project-layout/)

## Module Classification Rules (Imposed)
- Put all parsers and writers under `prototyping_inference_engine/io/` with subpackages `parsers/` and `writers/`.
- Treat reusable primitives (IRI utilities, terms, atoms, substitutions) as API modules under `prototyping_inference_engine/api/`.
- Keep `api/data/` for abstractions and protocols; move concrete data sources into named subpackages (e.g., `api/data/functions/`, `api/data/collection/`).
- Mirror the code hierarchy in tests (tests live in the corresponding package subtree).
- Avoid catch-all modules: if a module grows beyond a single responsibility, carve out a dedicated subpackage with explicit naming.
- Keep package `__init__.py` minimal and only re-export stable public entry points.

## Documentation Practices (Imposed)
- Keep documentation in `docs/` at the repository root, written in Markdown, and keep `README.md` as the entry point. (https://docs.python-guide.org/writing/structure/)
- Use MkDocs (`mkdocs.yml`) to build the documentation site from `docs/` when publishing to GitHub Pages. (https://www.mkdocs.org/user-guide/configuration/)
- Use docstrings for API-level explanations; keep narrative guides in `docs/`. (https://peps.python.org/pep-0257/)
- Publish documentation via GitHub Pages using the workflow in `.github/workflows/docs.yml`. (https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

### Tracked Plans
- None

### Design Docs
- `agents/design/computed-json-loader.md`
- `agents/design/computed-json-default-module.md`
- `agents/design/io-api-restructure.md`
- `agents/design/execution-notes-hygiene.md`
- `agents/design/dlgpe-nested-functional-terms.md`
- `agents/design/coverage-badge.md`
- `agents/design/tests-when-pertinent.md`
- `agents/design/atom-evaluator-dip.md`
- `agents/design/pypi-cd.md`
- `agents/design/docs-content.md`
- `agents/design/agent-artifacts-docs.md`
- `agents/design/iri-resolution.md`
- `agents/design/iri-manager.md`
- `agents/design/io-parsers-writers.md`
- `agents/design/iri-relativization-fixes.md`
- `agents/design/integraal-standard-functions.md`
- `agents/design/integraal-tests-port.md`
- `agents/design/kb-rulebase-csvcopyable.md`
- `agents/design/data-delegation-wrappers.md`
- `agents/design/prepared-queries-factory.md`
- `agents/design/functional-terms-identity.md`
- `agents/design/test-writing-rules.md`
- `agents/design/process-templates.md`
- `agents/design/commit-process.md`
- `agents/design/functional-terms.md`
- `agents/design/query-evaluation-structure.md`
- `agents/design/mypy-fixes-2026-02-04.md`
- `agents/design/github-ci.md`
- `agents/design/ci-badge.md`
- `agents/design/mypy-test-gate.md`
- `agents/design/code-quality-tooling.md`
- `agents/design/readme-badges.md`
- `agents/design/ci-mypy-install.md`
- `agents/design/doc-examples-tests.md`
- `agents/design/computed-functions-docs.md`
- `agents/design/negation-function-terms.md`
- `agents/design/remove-dlgp2-parser.md`

### Process Artifacts
- `agents/templates/PLAN_TEMPLATE.md`
- `agents/templates/DESIGN_TEMPLATE.md`
- `agents/templates/docs/index.md`
- `agents/templates/docs/architecture.md`
- `agents/templates/docs/usage.md`
- `agents/templates/docs/api.md`
- `agents/templates/docs/contributing.md`
- `agents/process/DEFINITION_OF_DONE.md`
- `agents/process/VERSIONING.md`
- `agents/process/REVIEW_CHECKLIST.md`
- `agents/process/RELEASE_CHECKLIST.md`
- `agents/process/CONVENTIONAL_COMMITS.md`
- `agents/process/COMMIT_TEMPLATE.md`
- `agents/process/COMMIT_POLICY.md`

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
python3 -m unittest discover -s prototyping_inference_engine -t . -v

# Run a single test file
python3 -m unittest prototyping_inference_engine.api.fact_base.test.test_fact_base -v

# Run a specific test class
python3 -m unittest prototyping_inference_engine.backward_chaining.test.test_breadth_first_rewriting.TestBreadthFirstRewriting
```

### Quality Checks
```bash
ruff check .
ruff format --check .
python3 -m coverage run -m unittest discover -s prototyping_inference_engine -t . -v
python3 -m coverage report -m
bandit -r prototyping_inference_engine -x "prototyping_inference_engine/**/test,__pycache__" -ll
pip-audit --cache-dir .cache/pip-audit
vulture --config pyproject.toml prototyping_inference_engine
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
- DLGP-compatible files (`.dlgp`) are parsed by `DlgpeParser` and must use `|` for disjunction.

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

DLGP-compatible sample (.dlgp extension, DLGPE syntax):
```prolog
q(X) | r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

## Code Style
- Comments must always be in English.
## Writing Language
- All content written to any file must be in English.
