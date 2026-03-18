The line is roughly: **does it affect production, security, or trust?**

## Annoying (easy to recover from)
- Wrong variable names, style inconsistencies
- Inefficient algorithm when performance isn't critical
- Unnecessary abstraction or over-engineering
- Tests that don't compile on the first try
- Hallucinated API method names you catch in review
- Missing edge cases in non-critical paths

## Career-threatening (hard to recover from)

**Security**
- SQL injection, XSS, command injection shipped to production
- Hardcoded credentials committed to a public repo
- Broken auth/authorization logic (users seeing other users' data)
- Insecure deserialization, path traversal

**Data**
- Destructive migrations without backups (`DROP TABLE`, data overwrites)
- Silently wrong data (off-by-one in financial calculations, incorrect aggregations)
- GDPR/PII violations — logging or exposing personal data

**Reliability**
- Deleting or corrupting production data
- Taking down a service during high-traffic or critical windows
- Infinite loops or memory leaks that cascade into an outage

**Trust**
- Confidently presenting AI-generated output as your own reviewed work when it's wrong
- Shipping code you don't understand and can't explain or defend
- Bypassing review processes (skipping tests, `--no-verify`, force-pushing main)

## The real pattern

Annoying mistakes are **visible before they matter**. Dangerous ones are **invisible until they do damage** — in prod, in a customer's data, or in a security audit.

The compounding factor with AI tools specifically: AI can be *confidently wrong at scale*. A human might write one bad SQL query; an AI can generate an entire data access layer with the same flaw throughout. The mistake multiplies before anyone notices.

The mitigation is the same as always: understand the code you're shipping, treat security-sensitive paths with extra skepticism, and never skip review just because it "looks right."