**Twitter Thread: AI Coding Tools & The Confidence Tax 🧵**

---

**1/**
AI coding assistants are incredible. They're also occasionally confident liars that will cost you an entire afternoon. A thread on the greatest hits of "I trusted the bot and paid for it." 🧵

---

**2/**
"Here's how to fix your CORS error" — proceeds to add `Access-Control-Allow-Origin: *` to the *client*. Explained it with such authority that the engineer spent 2 hours debugging before realizing: the client doesn't set CORS headers. The server does. Classic.

---

**3/**
Asked Copilot to write a regex for email validation. It produced 8 lines of beautifully commented, completely wrong pattern. Passed "notanemail" and rejected half of RFC 5322-valid addresses. The comments were the most accurate part.

---

**4/**
"This API endpoint accepts a `user_id` parameter." It does not. It never did. The model hallucinated a parameter from a different version of a different library. The docs URL it cited? 404. The confidence? 10/10.

---

**5/**
A senior engineer asked an AI to help optimize a SQL query. The AI rewrote it, added an index suggestion, and explained the performance gains. The rewritten query returned different results. Silently. No errors. Just... wrong data in production for 6 hours.

---

**6/**
"In Python 3.11, you can use `dict.merge()` to combine dictionaries." You cannot. `dict.merge()` doesn't exist. The correct answer is `|`. The AI invented a method, named it plausibly, and even showed example output. The output was fabricated too.

---

**7/**
Asked for help with a React bug. Got a solution using a hook that "was added in React 18.2." The hook was made up. Not deprecated — *never existed*. The name was so believable that the dev spent an hour checking if their React version was wrong.

---

**8/**
The AI confidently told a dev their memory leak was caused by a missing `useEffect` cleanup. It wasn't. The real cause was a third-party library. The AI's fix *did* something — it just didn't fix *that*. Two days of red herrings.

---

**9/**
Common pattern across all of these:
- Confident tone ✓
- Plausible-sounding explanation ✓
- Code that compiles ✓
- Actually correct ✗

Compiling is not the same as correct. The model doesn't know the difference.

---

**10/**
None of this means stop using AI tools. It means: **verify outputs like you'd review a junior dev's PR.** The tool is fast. You still have to be right. The confidence in the answer is not a signal of accuracy — it's a constant. Treat it that way.