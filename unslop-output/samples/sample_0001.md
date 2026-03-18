1. **Insecure defaults / missing validation** — AI often omits input sanitization, boundary checks, or authentication guards, especially for "internal" functions it assumes are safe.

2. **Outdated or vulnerable dependencies** — Models trained on older data suggest libraries with known CVEs, or use deprecated APIs that lack modern security patches.

3. **Hardcoded secrets** — AI frequently embeds API keys, passwords, or tokens directly in code (especially in examples), which get committed to repos.

4. **Prompt-influenced injection** — When AI-generated code builds queries or commands from user input, it commonly skips parameterization, leaving SQL injection, command injection, or SSRF vectors open.

5. **Overly broad permissions / trust** — AI tends to grant excessive privileges (e.g., `chmod 777`, `*` in CORS/IAM policies, `eval()` on untrusted input) to make things "work" without scoping to least privilege.

**Key pattern:** AI optimizes for functional correctness over security posture — always review generated code with the same scrutiny you'd apply to untrusted third-party code.