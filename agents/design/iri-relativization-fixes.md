# IRI Relativization and Normalization Fixes

Date: 2026-02-05

## Context
Tightened IRI regression tests exposed edge cases in recomposition, normalization, and
relativization behavior that diverged from the Java reference tests.

## Decisions
- Preserve scheme-specific paths during parsing (e.g., `urn:isbn:...`) by disabling
  nested scheme parsing when a scheme is already present.
- Treat non-unreserved ASCII characters as not iunreserved in extended percent-decoding,
  keeping them percent-encoded (e.g., backslash in userinfo).
- Normalize empty authority paths to `/` to match expected normalization output.
- When a relativized candidate fails to resolve back to the target, fall back to the
  absolute IRI to preserve correctness.

## Files
- `prototyping_inference_engine/iri/resolution.py`
- `prototyping_inference_engine/iri/iri.py`
- `prototyping_inference_engine/iri/normalization.py`
- `prototyping_inference_engine/iri/test/test_iri_ref.py`
