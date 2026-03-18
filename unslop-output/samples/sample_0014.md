# AI Coding Assistants: What They Get Wrong and Why
**30-minute talk outline for intermediate developers**

---

## Structure (30 min)

| Section | Time |
|---|---|
| Hook + framing | 3 min |
| The 5 failure modes | 18 min |
| Why these failures happen | 5 min |
| How to work with them better | 3 min |
| Q&A setup / close | 1 min |

---

## 1. Hook + Framing (3 min)

- Open with a relatable war story: a confidently wrong AI suggestion that made it to production (or nearly did)
- Establish credibility: "I use these tools daily and think they're genuinely useful — but their failure modes are specific and learnable"
- Thesis: **AI assistants fail in predictable ways. Once you see the patterns, you can work around them.**

---

## 2. The 5 Failure Modes (18 min, ~3.5 min each)

**① Hallucinated APIs and deprecated signatures**
- Confidently invents method names, parameters, library versions
- Blends real APIs from memory with plausible-sounding fabrications
- *Demo*: ask for a library function from a niche or fast-moving package

**② Context blindness**
- Solves the stated problem, ignores the surrounding system
- Doesn't know your auth layer, your error conventions, your team's patterns
- Example: generates a perfectly valid SQL query that bypasses your ORM's soft-delete logic

**③ Overfit to common patterns**
- Produces the "textbook answer" even when your constraints require something different
- Will rewrite your clever-but-unusual code into standard-but-wrong code
- Example: normalizing away an intentional denormalization

**④ Test theater**
- Writes tests that pass trivially or test nothing meaningful
- Mocks everything, asserts the mock was called, ships with 100% "coverage"
- The test suite becomes a confidence trap

**⑤ Confident degradation under complexity**
- Quality drops sharply as task complexity increases — but the confidence doesn't
- Multi-file refactors, stateful workflows, cross-cutting concerns
- The model doesn't signal when it's out of its depth

---

## 3. Why These Failures Happen (5 min)

Keep this conceptual, not a deep ML lecture:

- **Training distribution**: models reflect what's common on the internet — Stack Overflow answers, not your codebase
- **No execution loop**: the model can't run the code, only predict what plausible code looks like
- **Context window limits**: it can't hold your entire system in mind simultaneously
- **Calibration problem**: next-token prediction doesn't naturally produce well-calibrated uncertainty — the model doesn't "know what it doesn't know"

One key takeaway: **these aren't bugs being fixed in the next version — they're structural properties of the approach.**

---

## 4. How to Work With Them Better (3 min)

Frame this as *changing your workflow*, not fixing the tool:

- **Verify against docs, not the model** — for any library call, check the actual source
- **Give context explicitly** — paste your interfaces, your conventions, your constraints
- **Treat generated tests as a starting point** — rewrite assertions yourself
- **Use it for the boring middle** — boilerplate, scaffolding, first drafts; own the edges
- **Increase skepticism proportionally to complexity** — the more moving parts, the more you review

---

## 5. Close (1 min)

- Restate the thesis: failure modes are predictable, therefore manageable
- One memorable line to leave them with, e.g.: *"The tool is most dangerous when it's most fluent."*
- Invite questions

---

## Slide suggestions

- Keep slides sparse — 1 idea per slide, code examples in large font
- For each failure mode: a brief bad example, then the "tell" that should have flagged it
- Avoid vendor-specific bashing; keep examples tool-agnostic