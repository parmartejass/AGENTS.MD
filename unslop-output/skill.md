Unslop profile for AI coding mistakes.

---

## Phrases to never use

- "confidently wrong" / "confidently generate" / "confident tone" / "confidence in the answer"
- "plausible-looking" / "plausible-sounding" / "surface plausibility" / "plausibly good"
- "junior developer" / "junior engineer" / "intern who has read every cookbook"
- "The Confident Intern Problem" (or any variant)
- "starting point, not a final answer"
- "The fix isn't to stop using AI"
- "None of this means stop using AI tools"
- "boilerplate" as the canonical safe use case
- "Use AI for boilerplate, not for important stuff" (any variant)
- "happy path" as the label for what AI gets right
- "silently" as the adverb of horror ("Silently. No errors.")
- "insidious" applied to failure modes
- "structural property of how large language models work"
- "these aren't bugs being fixed in the next version"
- "The fundamental issue is..." / "The core problem is..." / "The broader principle..."
- "security-sensitive paths" / "security-critical calls" (the fixed compound)
- "scrutiny" collocated with "same" ("same scrutiny you'd apply to...")
- "subtle" modifying every error or bug
- "hallucinate(d/ion)" for invented APIs (find a more precise description)
- "TOCTOU" dropped in without being the specific subject of analysis
- "Stay skeptical, stay specific, and always own what ends up in your codebase."
- "Trust the output. Verify the imports."
- "The tool is most dangerous when it's most fluent."
- "It learned from millions of examples of what code looks like, not from running code"
- "Treat it like code from a junior engineer you've never met"

---

## Structural patterns to avoid

**The balancing act reflex**
- Do not open with a productivity concession: "AI tools are genuinely useful... but"
- Do not close with reassurance that cancels the critique
- Do not pair every problem with a "the fix" terminator
- Do not build the piece around: [AI is useful] → [here's the problem] → [here's the fix] → [don't stop using AI]

**The authority escalation pattern**
- Do not move from a single example to claiming it's a "fundamental" or "structural" property
- Do not use "structural" or "fundamental" as a rhetorical landing point rather than a demonstrated conclusion
- Do not stack multiple "The fundamental issue is..." claims in the same document

**The competent-but-naive actor frame**
- Do not anthropomorphize AI as a junior developer, intern, or someone who learned theory without practice
- Do not reach for the cooking/cookbook analogy or any analogy that requires the reader to feel sympathy before skepticism
- If you need to explain a failure mode, describe the mechanism, not a character

**The self-critique hedge**
- Do not front-load a methodology disclaimer before engaging with the actual question
- Do not place "I'm one of the models being evaluated here, which introduces inherent bias" before the analysis — if the bias matters, it belongs after the content, not as a shield before it

---

## Structural formats to avoid

- Numbered lists as default backbone when the content isn't actually sequential or enumerable
- Tables inserted to signal analytical rigor when bullet points carry the same information
- "**The fix:**" as a bolded terminator after every section
- Problem-then-fix as mandatory two-part structure for every observation
- Pithy closing aphorisms structured as short parallel contrasts designed to be quotable on LinkedIn
- Q&A residue: opening mid-thought with "A few core reasons:" or "Here are the most common ones:" with no introduction

---

## Vocabulary tics to stop using

- "subtle" as the default modifier for any non-obvious error
- "plausible" as the default descriptor for dangerous-but-wrong output
- "confidently" as the default adverb attached to wrong AI output
- "insidious" for anything
- "surface" as a prefix ("surface plausibility," "surface level")
- "structural" to claim failures are fundamental rather than incidental
- "scrutiny" in any security context

---

## The fixed security antipattern list — do not just enumerate these

Every piece on AI coding mistakes reaches for the same six items:
- SQL injection / parameterized queries
- Hardcoded secrets / API keys
- `chmod 777` / overly broad permissions
- Broken auth / IDOR
- MD5/SHA-1 instead of bcrypt/Argon2
- `eval()` on untrusted input

Do not use this list as a canned repertoire. If your analysis of a specific failure doesn't lead to one of these items organically, don't include it.

---

## The training data explanation cluster — do not recite in order

When explaining why AI fails, the corpus reaches for the same four points in the same order:
1. Training cutoff / stale data
2. Overrepresentation of old examples on the internet
3. Stack Overflow as the canonical bad training signal
4. No runtime feedback loop ("the model can't run the code")

If you use any of these, use the one that's actually relevant. Do not recite all four as a block.

---

## The "compiles ≠ correct" observation

This insight has been stated ten times in this corpus without adding anything new each time:
- "syntactically valid but logically wrong"
- "compiles but fails at runtime"
- "no syntax errors, wrong answer"
- "a linter can't tell you if the logic is wrong"

If you're about to write any variant of this, ask whether you're actually adding anything. If not, cut it.

---

## Instead

If you catch yourself about to use any pattern above, stop. Find the specific thing that's actually true about this failure in this context. Name the mechanism, not the feeling it produces. Make the observation that only applies here, not the one that applies everywhere. The goal is precision — the slop patterns above are all evasions of precision dressed as insight.
