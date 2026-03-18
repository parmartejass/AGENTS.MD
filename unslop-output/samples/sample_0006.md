A few core reasons:

1. **They test the implementation, not the behavior.** AI reads your code and writes tests that verify what the code *does*, rather than what it *should* do. If the code has a bug, the test often encodes that bug as the expected output.

2. **They chase coverage, not confidence.** AI tends to write many shallow tests that hit lines of code without exercising meaningful edge cases, error paths, or invariants that actually matter.

3. **Tautological assertions.** Tests often just call the function and assert the result equals... calling the function again, or hardcode a value that was copy-pasted from a debugger run rather than reasoned about.

4. **No understanding of intent.** AI doesn't know *why* a function exists or what contract it's supposed to uphold. Good tests are a specification; AI tests are a description of observed behavior.

5. **Mocking everything.** Over-mocking is common — AI isolates so aggressively that tests pass even when the real integration is broken.

The fundamental issue is that good tests require understanding the **requirements**, not just the **code**. AI works from the code, so it produces tests that are structurally valid but semantically weak.