## Why Blindly Trusting AI Code Suggestions Is Dangerous

AI models generate plausible-looking code based on patterns, not correctness or security. They can produce code that works functionally but contains serious vulnerabilities — and because the code *looks* reasonable, developers often accept it without scrutiny.

---

### The SQL Injection Example

Suppose you ask an AI: *"Write a Python function to get a user by username from a database."*

The AI might produce:

```python
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()
```

This works perfectly for normal input. But if an attacker passes:

```
username = "admin' OR '1'='1
```

The query becomes:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1'
```

`'1'='1'` is always true — this returns **every user in the database**. With a more targeted payload like `'; DROP TABLE users; --`, the damage can be permanent.

**The correct version** uses parameterized queries:

```python
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone()
```

The database driver now treats `username` strictly as data, never as executable SQL.

---

### Why This Happens With AI

| Problem | Explanation |
|---|---|
| **Training data bias** | The internet contains enormous amounts of insecure code. AI learns those patterns too. |
| **No runtime context** | AI doesn't know your threat model, user base, or data sensitivity. |
| **Optimizes for plausibility** | Output is shaped to look correct, not to be secure. |
| **No security linting** | Unlike a compiler or SAST tool, AI has no built-in vulnerability checker. |

---

### The Core Lesson

AI-generated code should be treated like code from a **junior developer with no security training**: useful as a starting point, but requiring the same review you'd give any untrusted code. For anything touching databases, auth, file I/O, or user input, always verify against established secure coding practices — never ship AI output without review.