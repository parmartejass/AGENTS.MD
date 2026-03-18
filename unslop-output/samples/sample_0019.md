# Coding Mistakes in C++ Memory Management: GPT-4 vs Claude vs Copilot

A disclaimer upfront: I'm one of the models being evaluated here, which introduces inherent bias. I'll be as honest as I can, drawing on published research, community benchmarks, and documented failure patterns. Treat this as informed analysis, not ground truth.

---

## Framework: Categories of C++ Memory Errors

| Category | Description |
|---|---|
| **Use-after-free** | Accessing memory after it's been deallocated |
| **Double-free** | Calling `delete` on the same pointer twice |
| **Buffer overflow** | Writing past the end of an allocated region |
| **Memory leak** | Allocating without paired deallocation |
| **Dangling pointers** | Pointers to objects whose lifetime has ended |
| **Ownership confusion** | Unclear or incorrect ownership semantics |
| **RAII violations** | Failing to tie resource lifetime to object lifetime |
| **Smart pointer misuse** | Incorrect use of `unique_ptr`, `shared_ptr`, `weak_ptr` |

---

## GitHub Copilot

### Characteristic Failure Mode: Training Distribution Bias

Copilot is heavily shaped by the statistical patterns in its training corpus (public GitHub code). This creates specific, reproducible failure patterns.

### 1. Raw Pointer Proliferation

Copilot autocompletes toward what it has seen most — and pre-C++11 code is massively overrepresented in public repos. It frequently suggests:

```cpp
// Copilot tends to suggest this
Foo* obj = new Foo();
// ... many lines later, maybe a delete, maybe not
```

Rather than:

```cpp
auto obj = std::make_unique<Foo>();
```

The failure isn't that Copilot doesn't *know* about smart pointers — if you prompt in a smart-pointer context, it'll use them. It's that its default completion under ambiguity reaches for the older pattern.

### 2. Missing `delete[]` for Array Allocations

A well-documented Copilot failure:

```cpp
// Copilot often suggests new[] but completes with delete
int* arr = new int[100];
// ... later
delete arr;  // UB: should be delete[]
```

This is a subtle distinction that appears inconsistently in training data.

### 3. `memcpy`/`memset` on Non-Trivial Types

Copilot will suggest `memcpy` for struct copying even when the struct contains non-trivially-copyable members (strings, vectors, objects with custom destructors):

```cpp
struct Node {
    std::string name;
    int value;
};

Node a, b;
memcpy(&a, &b, sizeof(Node));  // Copilot may suggest this — it's UB
```

This bypasses copy constructors and can corrupt internal state of `std::string` (which typically uses SSO with an internal pointer).

### 4. Ownership Unclear in Returned Raw Pointers

Copilot frequently generates functions that return raw pointers with no indication of whether the caller owns them:

```cpp
// Does the caller free this? Is it a view into internal state?
Foo* getOrCreate(int id);
```

No `[[nodiscard]]`, no documentation, no `unique_ptr`. This is a systemic ownership ambiguity that leads to leaks or double-frees downstream.

### 5. `shared_ptr` Overuse

When it does use smart pointers, Copilot over-applies `shared_ptr` where `unique_ptr` would be correct. This is likely because `shared_ptr` appears more in training data in generic utility code. The result is unnecessary reference-counting overhead and, more dangerously, cycles that cause leaks:

```cpp
struct Node {
    std::shared_ptr<Node> next;  // Copilot suggestion
    // In a doubly-linked list, this creates cycles → leak
};
```

### 6. `std::vector::operator[]` Without Bounds Checking

Copilot almost never suggests `.at()` and almost always uses `[]`, even in contexts where bounds checking is clearly needed. This is a training bias — most code on GitHub uses `[]`.

---

## GPT-4

### Characteristic Failure Mode: Plausible-Sounding but Semantically Wrong

GPT-4 tends to produce code that *looks* more modern and thoughtful than Copilot, but makes more subtle semantic errors, particularly around lifetime and move semantics.

### 1. Move Semantics Misunderstanding

GPT-4 understands `std::move` syntactically but misapplies it semantically:

```cpp
std::unique_ptr<Foo> a = std::make_unique<Foo>();
std::unique_ptr<Foo> b = std::move(a);
a->doSomething();  // GPT-4 sometimes generates this: use-after-move
```

It will move a value and then use the moved-from object, which for `unique_ptr` is a null dereference.

### 2. `weak_ptr` Lock Pattern Errors

GPT-4 knows `weak_ptr` exists but misuses the lock pattern:

```cpp
// GPT-4 version — incorrect
std::weak_ptr<Foo> wp = sharedFoo;
if (!wp.expired()) {
    wp.lock()->doSomething();  // TOCTOU: expired() and lock() are not atomic
}

// Correct
if (auto sp = wp.lock()) {
    sp->doSomething();
}
```

The expired-then-lock pattern is a classic TOCTOU race. GPT-4 generates it frequently.

### 3. Self-Assignment in Custom Copy Operators

GPT-4 writes copy assignment operators that fail on self-assignment:

```cpp
// GPT-4 generated
MyClass& operator=(const MyClass& other) {
    delete[] data_;
    data_ = new char[other.size_];  // If other == *this, data_ is now freed
    memcpy(data_, other.data_, other.size_);  // UB
    return *this;
}
```

The self-assignment guard (`if (this == &other) return *this;`) or the copy-and-swap idiom is frequently missing.

### 4. Exception Safety in Resource Acquisition

GPT-4 will write code that leaks if a constructor throws after some allocations:

```cpp
// GPT-4 version — not exception-safe
class Manager {
    Foo* a_;
    Bar* b_;
public:
    Manager() {
        a_ = new Foo();
        b_ = new Bar();  // If this throws, a_ leaks
    }
};
```

Modern C++ solves this with member initialization using smart pointers. GPT-4 knows this when asked directly but doesn't apply it automatically.

### 5. Incorrect `reinterpret_cast` for Type Punning

GPT-4 often suggests `reinterpret_cast` for type punning (reading a float's bits as an int, etc.), which is undefined behavior in C++:

```cpp
float f = 3.14f;
int i = *reinterpret_cast<int*>(&f);  // UB: strict aliasing violation
```

The correct approach (`memcpy` into an `int`, or `std::bit_cast` in C++20) is rarely suggested.

### 6. Over-Reliance on `shared_ptr` Cycles

Similar to Copilot but with a twist: GPT-4 will often create parent-child relationships using `shared_ptr` for both directions, creating reference cycles:

```cpp
struct Parent {
    std::vector<std::shared_ptr<Child>> children;
};
struct Child {
    std::shared_ptr<Parent> parent;  // Cycle! Should be weak_ptr
};
```

GPT-4 often knows to use `weak_ptr` if you ask it to explain ownership, but the default generated code doesn't apply it.

---

## Claude (this model)

### Characteristic Failure Mode: Over-Cautiousness and Abstraction Errors

Based on documented failure cases and my own honest assessment:

### 1. Over-Qualification Leading to Verbose, Error-Prone Code

I tend to add excessive wrapping and abstraction that can introduce ownership confusion:

```cpp
// I might generate this unnecessarily
template<typename T>
std::optional<std::shared_ptr<T>> safeGet(/* ... */);
```

Indirection through `optional<shared_ptr<T>>` is almost never correct — a null `shared_ptr` and an empty `optional<shared_ptr<T>>` have different semantics and I conflate them.

### 2. `std::initializer_list` Dangling Reference

A subtle failure I reproduce: `std::initializer_list` has reference semantics to a temporary array:

```cpp
auto il = {1, 2, 3};  // type: std::initializer_list<int>
// Underlying array may be gone by now — dangling
auto& first = *il.begin();  // Potentially UB
```

I understand `initializer_list` at a surface level but miss the lifetime subtleties in generated code.

### 3. Incorrect `enable_shared_from_this` Usage

When generating code with `enable_shared_from_this`, I sometimes call `shared_from_this()` in a constructor — which throws `std::bad_weak_ptr` because no `shared_ptr` to the object exists yet:

```cpp
struct Foo : std::enable_shared_from_this<Foo> {
    Foo() {
        register(shared_from_this());  // Throws: no shared_ptr exists yet
    }
};
```

### 4. Placement New Lifecycle Errors

I generate placement new without consistent manual destructor calls:

```cpp
alignas(Foo) char buf[sizeof(Foo)];
Foo* p = new (buf) Foo();
// ... I sometimes forget:
p->~Foo();  // Must call destructor explicitly
```

### 5. Conservative Use of Raw Pointers — Sometimes Overcorrected

I tend to reach for smart pointers even in contexts where raw observer pointers are the correct choice (iterating a container, temporary views, FFI boundaries), which can cause unnecessary `shared_ptr` overhead and API awkwardness.

---

## Side-by-Side Summary

| Error Type | Copilot | GPT-4 | Claude |
|---|---|---|---|
| Raw pointer default | **High** | Medium | Low |
| `delete` vs `delete[]` confusion | **High** | Low | Low |
| `memcpy` on non-trivial types | **High** | Medium | Low |
| Move semantics (use-after-move) | Low | **High** | Medium |
| `weak_ptr` lock TOCTOU | Low | **High** | Medium |
| Self-assignment in copy op | Medium | **High** | Medium |
| Exception-unsafe constructors | Medium | **High** | Medium |
| `reinterpret_cast` aliasing UB | Low | **High** | Low |
| `shared_ptr` cycles | Medium | **High** | Medium |
| `shared_from_this` in ctor | Low | Medium | **High** |
| Placement new lifecycle | Low | Low | **High** |
| Ownership clarity in APIs | **High** | Medium | Low |

---

## Patterns and Root Causes

**Copilot** errors are **distributional**: they reflect what's common in public code, not what's correct. Raw pointers, `delete` mismatches, and `memcpy` misuse are legacy patterns that outnumber modern alternatives in its training data.

**GPT-4** errors are **reasoning errors**: it understands abstractions but misapplies them in edge cases. Move semantics, TOCTOU with `weak_ptr`, and exception safety require careful sequential reasoning about object state that it consistently gets slightly wrong.

**Claude** errors tend toward **abstraction boundary failures**: misunderstanding the contract of standard library components (`initializer_list` lifetimes, `shared_from_this` preconditions, placement new lifecycle).

---

## Practical Recommendations

1. **For all models**: Always validate generated C++ with ASan + UBSan + Valgrind before trusting it
2. **Against Copilot output**: Audit all raw pointers, verify `new[]`/`delete[]` pairing, check `memcpy` target types
3. **Against GPT-4 output**: Audit move semantics, `weak_ptr` lock patterns, copy assignment operators, and exception safety
4. **Against Claude output**: Audit smart pointer choices at API boundaries, `shared_from_this` usage, and placement new

No model reliably catches all of these. Human review — or static analysis with clang-tidy, cppcheck, or Clang's `-fsanitize=address,undefined` — remains necessary.