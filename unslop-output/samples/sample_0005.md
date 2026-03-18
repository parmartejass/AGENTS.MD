# The Phantom API Problem: When AI Assistants Invent Code That Doesn't Exist

---

AI code assistants are genuinely useful. They reduce boilerplate, surface relevant patterns, and help you move faster. But they have a failure mode that's particularly insidious: they confidently generate calls to functions, methods, and modules that simply do not exist.

This isn't a fringe bug. It's a structural property of how large language models work, and if you're using AI-assisted development without accounting for it, you're shipping phantom code into your codebase.

---

## Why Hallucination Happens

LLMs don't have a model of "what exists." They have a model of "what patterns appear together in training data." When generating code, the model is predicting the most plausible next token given the context — not querying a database of valid API surfaces.

This creates a specific failure mode: the model has seen enough examples of `someLibrary.doThing()` patterns that it generalizes. It knows that HTTP clients have a `.get()` method with certain arguments. It knows that auth libraries have token introspection. It knows that ORMs have fluent query builders. So it confidently synthesizes a *plausible* API that fits those patterns — even if no such method exists in the actual library.

The result looks exactly like real code. It follows real naming conventions. The types line up. The arguments look reasonable. It fails only at runtime.

---

## Real-World Examples

### 1. Python `requests` — Invented Session Management

Prompt: *"Write code to make authenticated HTTP requests with automatic retry logic."*

```python
import requests

session = requests.Session()
session.configure(
    retries=3,
    backoff_factor=0.5,
    auth_token="Bearer " + token
)

response = session.get_with_retry("https://api.example.com/data")
```

**What's wrong:** `requests.Session` has no `.configure()` method and no `.get_with_retry()`. The actual retry pattern in `requests` requires the `urllib3` `Retry` object and a `HTTPAdapter`:

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.headers.update({"Authorization": "Bearer " + token})
```

The hallucinated version is *what you'd want the API to look like*. It's intuitive, fluent, and completely fabricated.

---

### 2. Node.js `fs/promises` — Invented Convenience Methods

Prompt: *"Read a JSON config file asynchronously."*

```javascript
const fs = require('fs/promises');

const config = await fs.readJSON('./config.json');
```

**What's wrong:** `fs/promises` has no `readJSON`. It has `readFile`. The model has conflated the `fs-extra` library (which *does* have `readJSON`) with Node's built-in `fs/promises`.

The correct approach:

```javascript
const fs = require('fs/promises');

const raw = await fs.readFile('./config.json', 'utf8');
const config = JSON.parse(raw);
```

This is a subtle category error: two libraries occupy the same conceptual space in the training data (`fs` vs `fs-extra`), and the model blends their APIs. The hallucinated code would throw `TypeError: fs.readJSON is not a function` at runtime.

---

### 3. Python `pandas` — Invented DataFrame Methods

Prompt: *"Filter a DataFrame to rows where any column contains a null, then get a summary."*

```python
df_nulls = df.filter_nulls(how='any')
summary = df_nulls.describe_missing()
```

**What's wrong:** Neither `.filter_nulls()` nor `.describe_missing()` exist. The real methods:

```python
df_nulls = df[df.isnull().any(axis=1)]
summary = df_nulls.isnull().sum()
```

The hallucinated names are extremely plausible — pandas does have `dropna(how='any')`, `describe()`, and `isnull()`. The model assembled a coherent-looking API from parts, but the assembled version doesn't exist.

---

### 4. Rust `tokio` — Invented Async Utilities

Prompt: *"Run two async tasks concurrently and collect both results."*

```rust
use tokio::task;

let results = task::join_all(vec![
    task::spawn(async { compute_a().await }),
    task::spawn(async { compute_b().await }),
]).await;
```

**What's wrong:** `task::join_all` doesn't exist in `tokio`. The function is `futures::future::join_all` from the `futures` crate, or you'd use `tokio::join!` macro for a fixed number of futures. The model merged two different APIs.

```rust
// Option 1: futures crate
let results = futures::future::join_all(vec![
    tokio::spawn(async { compute_a().await }),
    tokio::spawn(async { compute_b().await }),
]).await;

// Option 2: tokio macro for fixed count
let (a, b) = tokio::join!(compute_a(), compute_b());
```

This example is particularly dangerous in Rust because it won't compile — but in dynamic languages, similar errors hide until runtime.

---

### 5. LangChain — The Worst Offender

LangChain is a high-churn library that has reorganized its API multiple times. Combined with its extensive coverage in training data, it's a hallucination trap.

Prompt: *"Create a retrieval chain that uses a vector store."*

```python
from langchain.chains import RetrievalQAChain
from langchain.vectorstores import Chroma

chain = RetrievalQAChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)
```

**What's wrong (as of LangChain v0.2+):** `RetrievalQAChain` was deprecated and moved. The import paths changed. `from_llm` was replaced. The model is likely drawing on pre-reorganization documentation that was heavily represented in training data.

This class of error — where the function *used to exist* but has since moved or been deprecated — is among the hardest to catch because searching the old class name may return old docs that confirm the hallucination.

---

## Hallucination Taxonomy

Not all hallucinations are equal. They cluster into recognizable patterns:

| Type | Description | Example |
|---|---|---|
| **Method invention** | Calling a method that doesn't exist on a real object | `session.configure()` on `requests.Session` |
| **Cross-library contamination** | Blending APIs from two related libraries | `fs.readJSON` from `fs-extra` appearing on `fs/promises` |
| **Version drift** | Code that was valid in an older version | Deprecated LangChain chains |
| **Plausible extrapolation** | Inventing a method that *should* exist by analogy | `df.describe_missing()` by analogy with `df.describe()` |
| **Namespace confusion** | Correct function, wrong import path | `task::join_all` placed in `tokio` instead of `futures` |
| **Argument hallucination** | Real function, invented parameters | `open(file, encoding='utf-8', buffered=True)` where `buffered` isn't a real kwarg |

---

## How to Catch Them

### 1. Never trust generated imports at face value

Every import in AI-generated code is a verification target. Run:

```bash
# Python: check what's actually exported
python -c "import requests; print(dir(requests.Session()))"

# Node: check module exports
node -e "const fs = require('fs/promises'); console.log(Object.keys(fs))"

# Rust: let the compiler be your linter (it will catch this)
cargo check
```

Make this a reflex. Generated imports look plausible; verify them against the actual module.

---

### 2. Use static analysis tooling with strict settings

For Python, `pyright` in strict mode will catch most hallucinated method calls:

```json
// pyrightconfig.json
{
  "typeCheckingMode": "strict",
  "reportUnknownMemberType": "error",
  "reportAttributeAccessIssue": "error"
}
```

For TypeScript, set `"strict": true` and `"noImplicitAny": true` in `tsconfig.json`. AI-generated TypeScript with `any` types is a red flag — it often means the model was uncertain about the real type.

For Rust, `cargo check` and `cargo clippy` are essentially mandatory. The type system will surface most hallucinations at compile time.

---

### 3. Run in an isolated environment immediately

Don't review AI-generated code in an editor for 20 minutes, then run it. Run it first, in a throwaway environment:

```bash
# Python: quick isolation
python -c "
import requests
s = requests.Session()
print(hasattr(s, 'configure'))  # False
print(hasattr(s, 'get_with_retry'))  # False
"
```

The faster you get to a runtime error, the cheaper the fix. Hallucinated APIs fail immediately when called — but only if you actually call them.

---

### 4. Cross-reference against official docs, not Stack Overflow

Stack Overflow and Medium articles often contain outdated or incorrect code — the same sources that contributed to LLM training data. When verifying an AI-suggested API:

- Go to the official docs directly
- Check the version number — docs are versioned; training data isn't
- Look at the library's changelog if you're not sure about recency

For Python libraries, the authoritative reference is always the `help()` output or `inspect.getmembers()`, not third-party articles.

---

### 5. Treat fluency as a warning signal, not a confidence signal

The most dangerous hallucinations are the most fluent ones. If the AI-generated code is exceptionally clean, well-named, and intuitive, that's often because the model is generating what it *thinks* the API should look like — not what it actually is.

Real library APIs have rough edges: inconsistent naming, legacy arguments, subtle gotchas. When AI-generated code looks too smooth, verify harder.

---

### 6. Pinned-version dependency checks

```bash
# Check if the function signature matches what's actually installed
pip show requests  # check version
python -c "import inspect, requests; print(inspect.signature(requests.Session.get))"
```

If AI-generated code references a feature from a newer version than what's installed, `pip install --upgrade` might "fix" it — or you might be introducing a breaking change to an existing project. Know which version the AI is targeting.

---

### 7. Use a hallucination-check prompt

Before using AI-generated code, paste it back and ask:

> "Does `[library]` actually have a `[method]` method? Show me the exact import path and confirm this exists in version `[version]`."

Models are better at *checking* claims than generating them from scratch — they can apply more careful pattern matching when focused on verification. This won't catch everything, but it adds a useful filter layer.

---

## Patterns That Predict Higher Hallucination Risk

Some situations reliably produce more hallucinated APIs:

**High-churn libraries** — LangChain, LlamaIndex, FastAPI, Next.js. Rapid API evolution means the training data contains multiple conflicting versions of the "correct" code.

**Less popular libraries** — Training data coverage thins out. The model extrapolates from analogous libraries rather than having seen real examples.

**Convenience methods** — The model "wants" to give you a clean one-liner. It will invent helper methods to make the code look nice.

**Cross-language prompts** — If you describe a Python pattern and ask for JavaScript, the model may port the Python API naming instead of using idiomatic JS.

**Deprecated features** — If a library has deprecated something, that deprecated API was heavily documented in old tutorials. The model has seen more examples of the old way than the new way.

---

## The Broader Principle

AI code generation is autocomplete for entire abstractions, not just tokens. The model has internalized the *shape* of good APIs and will fill in that shape with plausible-sounding names. When the real library matches that shape, the code works. When it doesn't, you get phantom functions.

The fix isn't to stop using AI assistants — the productivity gains are real. The fix is to treat every generated API call as *unverified* until you've confirmed it against the actual library. That's a small discipline that prevents a large class of bugs.

Trust the output. Verify the imports.

---

*Found a good hallucination example in the wild? The [issues tracker](https://github.com/anthropics/claude-code/issues) is a good place to document them.*