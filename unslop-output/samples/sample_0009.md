## Junior Dev Training Exercise: Bug Hunt

Below is a realistic piece of AI-generated Python code for a user analytics module. It looks correct at a glance, but contains **3 bugs**. Try to find them before reading the explanations.

---

### The Code

```python
from datetime import datetime, timedelta


def filter_active_users(users, inactive_days=30, seen={}):
    """Return users who logged in within the last `inactive_days` days."""
    cutoff = datetime.now() - timedelta(days=inactive_days)
    for user in users:
        last_login = datetime.fromisoformat(user["last_login"])
        if last_login >= cutoff:
            seen[user["id"]] = user
    return list(seen.values())


def paginate(items, page, page_size=10):
    """Return items for a given page (1-indexed)."""
    start = page * page_size
    end = start + page_size
    return items[start:end]


def average_score(scores):
    """Calculate average score, excluding zeros."""
    valid = [s for s in scores if s != 0]
    return sum(valid) / len(valid)
```

---

### Bug 1 — Mutable Default Argument (`filter_active_users`)

**Where:** `def filter_active_users(users, inactive_days=30, seen={})`

**What happens:** Python evaluates default argument values **once at function definition time**, not on each call. The `seen` dict is created once and reused across every call. Results from previous calls bleed into the next.

```python
# Call 1
result1 = filter_active_users(batch_a)  # seen = {1: ..., 2: ...}

# Call 2 — "seen" still holds data from Call 1!
result2 = filter_active_users(batch_b)  # seen = {1: ..., 2: ..., 3: ...}
```

**How to find it:** Run the function twice with different inputs and compare results — the second call returns more records than expected.

**Fix:**

```python
def filter_active_users(users, inactive_days=30, seen=None):
    if seen is None:
        seen = {}
    ...
```

---

### Bug 2 — Off-by-One in Pagination (`paginate`)

**Where:** `start = page * page_size`

**What happens:** The function is documented as **1-indexed** (page 1 = first page), but the math treats it as 0-indexed. Page 1 skips the first 10 items; page 0 returns them instead.

```python
items = list(range(25))

paginate(items, page=1)  # Returns [10..19] — wrong, should be [0..9]
paginate(items, page=0)  # Returns [0..9]  — page 0 shouldn't exist
```

**How to find it:** Call `paginate(items, page=1)` on a known list and check if you get the first items.

**Fix:**

```python
start = (page - 1) * page_size
```

---

### Bug 3 — Division by Zero (`average_score`)

**Where:** `return sum(valid) / len(valid)`

**What happens:** When every score is `0`, the filter `if s != 0` produces an empty list. `len([])` is `0`, causing `ZeroDivisionError`. The function also silently ignores legitimate zero scores (e.g., a user who scored 0 on a quiz), which may itself be a logic bug depending on intent.

```python
average_score([0, 0, 0])   # ZeroDivisionError
average_score([])           # ZeroDivisionError
```

**How to find it:** Unit test edge cases — empty input, all-zero input. These are the inputs AI-generated code most often fails to handle.

**Fix:**

```python
def average_score(scores):
    valid = [s for s in scores if s != 0]
    if not valid:
        return 0.0  # or raise ValueError, depending on requirements
    return sum(valid) / len(valid)
```

---

### Summary

| # | Bug | Category | Difficulty |
|---|-----|----------|------------|
| 1 | Mutable default argument | Python gotcha | Medium |
| 2 | Off-by-one in 1-indexed pagination | Logic error | Easy |
| 3 | Division by zero on empty/all-zero input | Missing edge case | Easy |

**Key takeaway:** AI-generated code is often syntactically correct and handles the happy path well. The bugs cluster around **Python-specific traps** (mutable defaults), **boundary conditions** (page 1 vs page 0), and **missing edge case handling** (empty collections). Always test with empty inputs, boundary values, and run functions more than once.