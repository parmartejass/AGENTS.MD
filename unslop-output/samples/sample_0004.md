Here are the most common ones:

## Subtle Async Bugs AI Tools Frequently Introduce

### 1. Unhandled promise rejections
```js
// AI generates this — no catch, no await error handling
async function fetchData() {
  const result = await fetch(url); // throws? silently dies
  return result.json();
}
```

### 2. Sequential awaits instead of parallel
```js
// AI defaults to this (slow — waits for each)
const a = await fetchA();
const b = await fetchB();

// Should be:
const [a, b] = await Promise.all([fetchA(), fetchB()]);
```

### 3. `await` inside a non-async callback
```js
// AI forgets the inner callback needs async too
items.forEach(async (item) => {
  await process(item); // forEach doesn't await this — fires and forgets
});
// Use: for...of loop, or Promise.all(items.map(...))
```

### 4. Error swallowing in try/catch
```js
try {
  await riskyOp();
} catch (e) {
  console.log(e); // logs and continues as if nothing happened
  // Missing: throw e, return, or proper recovery
}
```

### 5. Race conditions with shared state
```js
// AI generates this without noting the race
async function increment() {
  const val = await getValue(); // two callers can read same val
  await setValue(val + 1);      // both write val+1, one increment lost
}
```

### 6. Missing `await` on cleanup/teardown
```js
async function test() {
  const conn = await openConnection();
  const result = await query(conn);
  conn.close(); // forgot await — test ends before close completes
  return result;
}
```

### 7. `Promise.all` failing silently on partial results
```js
// If any promise rejects, ALL results are lost — not just the one
const results = await Promise.all(requests);
// Should use Promise.allSettled() when partial success is acceptable
```

### 8. Returning a promise from an async function unnecessarily
```js
async function getUser() {
  return await fetchUser(); // redundant await — adds a microtask tick
  // but worse: wrapping in try/catch changes error behavior subtly
}
```

### 9. Not handling `AbortController` / cancellation
AI tools rarely generate cancellation logic, so long-running fetches continue after components unmount or operations are cancelled, causing state updates on dead references.

### 10. Event listener async handlers
```js
button.addEventListener('click', async () => {
  await doSomething(); // double-clicks fire concurrent executions
  // No debounce, no in-flight guard
});
```

---

The two most dangerous are **#3** (silent fire-and-forget in `forEach`) and **#5** (race conditions on shared state) — they produce no errors and are hard to spot in review.