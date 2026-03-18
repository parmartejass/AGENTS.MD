# AI-Generated Code Review Checklist

## Security
- [ ] No secrets, API keys, or credentials hardcoded in the code
- [ ] User inputs are validated and sanitized at system boundaries
- [ ] No SQL/command/shell injection vulnerabilities (parameterized queries, no `eval`, no `shell=True` with user input)
- [ ] No path traversal risks (user-controlled file paths without sanitization)
- [ ] Dependencies added are real, current, and from official sources (AI hallucinates package names)
- [ ] Auth checks are present and placed *before* the protected logic, not after

## Correctness
- [ ] Off-by-one errors in loops, slices, and index math
- [ ] Edge cases handled: empty input, null/None, zero, negative numbers, single-element collections
- [ ] Async/await used correctly — no missing `await`, no blocking calls inside async context
- [ ] Error paths return or raise, not silently fall through
- [ ] Conditions use the right operator (`==` vs `is`, `&&` vs `&`, `>=` vs `>`)
- [ ] The algorithm actually solves the stated problem — AI often solves a *similar* but subtly different one

## Hallucinations & Made-Up APIs
- [ ] Every library, module, or package imported actually exists
- [ ] Every method/function called exists in the version of the library being used
- [ ] Optional parameters and their defaults are verified against actual docs
- [ ] No invented environment variables, config keys, or file paths

## Completeness
- [ ] Error handling is present, not just the happy path
- [ ] Resource cleanup happens (files closed, connections released, locks freed) even on failure
- [ ] The code handles concurrent access if it will run in a multi-threaded or multi-process context
- [ ] Logging/observability is sufficient to debug failures in production

## Integration
- [ ] Function signatures match how callers will actually invoke them
- [ ] Return types and shapes match what downstream code expects
- [ ] New dependencies are compatible with existing versions (no conflicts)
- [ ] Database schema changes, migrations, or seeders are included if needed
- [ ] Environment-specific behavior (dev vs. prod) is correct

## Performance
- [ ] No N+1 queries (database calls inside loops)
- [ ] No unbounded operations on large datasets (missing pagination, limits, or streaming)
- [ ] No unnecessary re-computation inside hot loops (move invariants out)

## Tests
- [ ] Tests cover the actual behavior, not just what the AI assumed the behavior should be
- [ ] Tests don't mock so heavily that they only test the mocks
- [ ] Edge cases above are tested, not just the happy path

---

**Rule of thumb:** AI code is often *plausible-looking but wrong in a subtle way*. Read it as if a junior engineer wrote it confidently — assume good structure, but verify every assumption about APIs, logic, and security boundaries.