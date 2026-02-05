# Design: IRI Resolution
Date: 2026-02-05
Status: Accepted

## Context
PIE parses DLGPE/DLGP2 files containing IRIs, @base, and @prefix directives, but IRI resolution was previously not applied and the prefix/base context was not preserved for later export.

## Decision
Implement RFC 3986-style IRI resolution (including dot-segment removal) for IRIREFs and prefixed names during parsing, and store @base/@prefix context in both ParseResult and ReasoningSession.

## Rationale
Resolving IRIs at parse time keeps downstream API objects consistent and simplifies evaluation. Capturing the namespace context allows future exporters to rebuild a DLGPE header with the same prefixes/base. We keep the internal `xsd:`/`rdf:` datatype prefixes unchanged by treating them as built-in prefix bases to avoid breaking literal handling.

## Alternatives Considered
- Use `urllib.parse.urljoin` — rejected to avoid implicit normalization differences and keep the implementation aligned with RFC 3986 steps.
- Expand all datatypes to full IRIs — rejected because literal parsing currently expects `xsd:`/`rdf:` forms and changing them would be a larger refactor.

## Consequences
- Positive: IRIREF and prefixed names resolve consistently in DLGPE and DLGP2 parsing.
- Positive: Session and parse results retain namespace context for later export.
- Negative: Undefined prefixes now raise errors during parsing.

## Follow-ups
- Consider exposing an exporter that uses captured base/prefix context.
