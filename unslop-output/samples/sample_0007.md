## Warning: AI-Generated Authentication and Authorization Code

> **This section applies to all authentication, authorization, session management, and cryptographic code.**

---

### Do Not Use AI-Generated Code for Auth Logic Without Rigorous Review

AI code generation tools (including LLMs, Copilot, and similar assistants) can produce authentication and authorization code that **appears correct but contains subtle, critical flaws**. These flaws are often not caught by tests, linters, or casual review because the code is structurally plausible and compiles cleanly.

---

### Specific Risks

**1. Incorrect security defaults**
AI models frequently generate examples optimized for clarity or brevity, not security. Common outputs include:
- Hardcoded secrets or weak placeholder credentials left in place
- Symmetric JWT signing (`alg: HS256`) where asymmetric signing is required
- Disabled signature verification (`verify=False`, `options={"verify_signature": False}`)
- Missing expiration (`exp`) or issuer (`iss`) claim validation

**2. Flawed authorization logic**
AI tends to generate authorization checks that pass obvious tests but fail at boundaries:
- Missing checks on indirect object references (IDOR)
- Role checks that verify role name as a string instead of a trusted claim
- Authorization evaluated before authentication is confirmed
- Privilege checks placed in the wrong layer (e.g., UI only, not API)

**3. Insecure cryptographic choices**
AI training data contains large volumes of outdated cryptographic examples:
- MD5/SHA-1 for password hashing instead of bcrypt/Argon2
- ECB mode for symmetric encryption
- Predictable IVs or nonces
- Roll-your-own token generation using `random` instead of `secrets`/`crypto`

**4. Race conditions and TOCTOU vulnerabilities**
AI-generated auth flows often check permissions and act in separate steps without atomicity guarantees, creating time-of-check to time-of-use windows.

**5. Confident but wrong**
AI tools do not flag their own uncertainty. Code with a critical authorization bypass may be presented with the same confidence as a correct implementation.

---

### Required Process for Any Auth Code

Regardless of whether AI tools were used, all authentication and authorization code **must**:

1. Be reviewed by a second engineer with security experience before merge
2. Reference an established, audited library or framework (e.g., OAuth 2.0 libraries, Passport.js, Spring Security) — do not implement auth primitives from scratch
3. Include a threat model comment block explaining what the code protects against and what it explicitly does not cover
4. Pass a dedicated security review checklist (see `docs/security-checklist.md`) before the PR is approved

---

### Acceptable Use of AI for Auth Code

AI tools **are** appropriate for:
- Drafting test cases to probe your existing auth logic
- Explaining a security concept or RFC section
- Generating boilerplate that wraps a vetted library, where the security-critical calls are not AI-generated

AI tools are **not** a substitute for understanding the security model you are implementing.

---

> **When in doubt, escalate to the security team before merging.** A delayed feature is recoverable. A broken auth boundary often is not.