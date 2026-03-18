## Why "Looks Right" Isn't "Works Right" for AI-Generated Code

Here's an analogy that captures it well:

---

### The Confident Intern Problem

Imagine you hired an intern who has read every cookbook ever written, but has never actually cooked a meal. Ask them to write a recipe for beef stew, and they'll produce something that *reads perfectly* — correct units, logical steps, plausible ingredients. It won't have obvious typos. A chef skimming it would think "yeah, that looks fine."

But until someone actually makes the stew, you don't know if it's missing a critical step, uses a ratio that makes it inedible, or assumes an oven temperature that's off by 100 degrees.

AI code has the same problem. It learned from millions of examples of *what code looks like*, not from *running code and seeing what happens*.

---

### The specific risks this creates

**1. It's fluent, not correct.**
AI produces code the way a fluent non-native speaker produces a grammatically perfect sentence with the wrong meaning. No typos. No syntax errors. Wrong answer.

**2. Edge cases are invisible in the output.**
Code that works 95% of the time and silently fails the other 5% *looks identical* to code that works 100% of the time. The bug only shows up when a real user hits that edge case.

**3. It mimics patterns without understanding constraints.**
AI might write a discount calculation that looks textbook-correct but produces negative prices for certain coupon combinations. It's modeled the *shape* of pricing logic, not *your* business rules.

**4. Logic errors hide behind correct syntax.**
A spell-checker can't tell you if your email makes a bad argument. A linter (the tool that checks code quality) can't tell you if the logic is wrong — only that it's well-formatted.

**5. Security holes look like normal code.**
A SQL query that exposes all user data looks almost identical to one that doesn't. The dangerous version isn't obviously malformed.

---

### The practical implication

> **AI code requires the same QA investment as human-written code — possibly more**, because developers may unconsciously trust it more than they should, precisely because it looks polished.

"Looks good to me" is not a safe review standard for AI output. The code needs to be tested against real scenarios, edge cases, and your specific business rules — the same bar you'd hold any code to.

The risk isn't that AI writes *obviously bad* code. It's that it writes *plausibly good* code that fails in non-obvious ways.