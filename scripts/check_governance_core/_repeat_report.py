from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

from scripts.check_governance_core._documents import (
    DocumentStore, MarkdownDocument, blocks, frontmatter_end, is_quoted, router_filename,
)
from scripts.check_governance_core._inventory import RepositoryInventory


# Repeat report: one warning-only witness for two owners. Its settings and exclusions come from the
# documentation owner (Validation boundary); the constant half is the coding owner's No Duplicates witness.
DOCS_OWNER = "(documentation owner, Validation boundary)"
CODING_OWNER = "(coding owner, No Duplicates)"
_DECLARATION = re.compile(r"^([a-z][a-z0-9_]*): \S.*$")
_SENTENCE_BREAK = re.compile(r"(?<=[.;!?])\s+")
_WORD = re.compile(r"[a-z0-9][a-z0-9_'-]*")


def repeat_parameters(policy: MarkdownDocument) -> tuple[tuple[re.Pattern[str], int, int] | None, list[str]]:
    """Read the repeat-report term list, shingle size and threshold from the docs-policy owner, with no defaults."""

    terms = (policy.declaration_value("normative_repeat_terms") or "").split("|")
    errors = [] if all(terms) and len({term.casefold() for term in terms}) == len(terms) else [
        "Docs policy must declare exactly one normative_repeat_terms list of unique, non-empty, pipe-separated terms"
    ]
    words, word_errors = policy.positive_integer_declaration("normative_repeat_shingle_words", "Docs policy")
    percent, percent_errors = policy.positive_integer_declaration("normative_repeat_min_percent", "Docs policy")
    errors.extend(word_errors + percent_errors)
    if errors or words is None or percent is None:
        return None, errors
    return (re.compile(r"\b(" + "|".join(map(re.escape, terms)) + r")\b", re.IGNORECASE), words, percent), []


def _tracked(repo_root: Path, inventory: RepositoryInventory, suffix: str, owner: str) -> tuple[list[str], list[str]]:
    """Tracked paths with one suffix, or an explicit SKIPPED + reason when the root cannot list them."""

    tracked, error = inventory.tracked_paths(repo_root)
    if error:
        return [], [f"repeat: SKIPPED: {error} {owner}"]
    return sorted(relative for relative in tracked if relative.lower().endswith(suffix)), []


def _repeated(kind: str, verb: str, sites: dict[str, list[tuple[str, int]]], owner: str) -> list[str]:
    return [f"repeat: {kind} {name} {verb} " + " and ".join(f"{file}:{line}" for file, line in found) + f" {owner}"
            for name, found in sorted(sites.items()) if len({file for file, _line in found}) > 1]


def _statements(document: MarkdownDocument):
    """Yield (line, text) per operative, unquoted block after the frontmatter; wrapped lines stay one block."""

    start = frontmatter_end(document.text.splitlines())
    for block in blocks((number, line) for number, line in document.operative_lines if number > start):
        if not is_quoted(block[0][1]):
            yield block


def statement_repeats(
    repo_root: Path, store: DocumentStore, inventory: RepositoryInventory,
    parameters: tuple[re.Pattern[str], int, int], excluded: tuple[str, ...],
) -> list[str]:
    """Warn on normative sentences and declarations that repeat across tracked Markdown files."""

    terms, size, percent = parameters
    paths, warnings = _tracked(repo_root, inventory, ".md", DOCS_OWNER)
    sentences: list[tuple[str, int, set[str]]] = []
    declarations: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for relative in paths:
        path = PurePosixPath(relative)
        if relative.startswith(excluded) or path.name == router_filename(path.parent.name):
            continue
        document, read_error = store.markdown(repo_root / relative)
        if read_error:
            warnings.append(f"repeat: SKIPPED {relative}: {read_error} {DOCS_OWNER}")
            continue
        assert document is not None
        for block in _statements(document):
            starts, text = [], ""
            for number, line in block:
                declaration = _DECLARATION.match(line)
                if declaration and line == line.lstrip():
                    declarations[declaration.group(1)].append((relative, number))
                starts.append((len(text), number))
                text += line.strip() + " "
            offset = 0
            for sentence in _SENTENCE_BREAK.split(text.strip()):
                offset = text.index(sentence, offset)
                number = next(line for position, line in reversed(starts) if position <= offset)
                offset += len(sentence)
                words = _WORD.findall(sentence.lower().replace("`", "")) if terms.search(sentence) else []
                if len(words) >= size:
                    sentences.append((relative, number, {" ".join(words[i:i + size]) for i in range(len(words) - size + 1)}))
    index: dict[str, list[int]] = defaultdict(list)
    for number, (_relative, _line, shingles) in enumerate(sentences):
        for shingle in shingles:
            index[shingle].append(number)
    shared: Counter[tuple[int, int]] = Counter()
    for members in (members for members in index.values() if len(members) > 1):
        for position, first in enumerate(members):
            for second in members[position + 1:]:
                if sentences[first][0] != sentences[second][0]:
                    shared[(first, second)] += 1
    for (first, second), count in sorted(shared.items()):
        (file_a, line_a, set_a), (file_b, line_b, set_b) = sentences[first], sentences[second]
        share = count * 100 // min(len(set_a), len(set_b))
        if share >= percent:
            warnings.append(f"repeat: {file_a}:{line_a} and {file_b}:{line_b} share {share}% of their "
                            f"{size}-word phrases {DOCS_OWNER}")
    return warnings + _repeated("declaration", "in", declarations, DOCS_OWNER)


def constant_repeats(
    repo_root: Path, store: DocumentStore, inventory: RepositoryInventory, excluded_roots: frozenset[Path],
) -> list[str]:
    """Warn on module-level literal constant names bound in more than one tracked module."""

    paths, warnings = _tracked(repo_root, inventory, ".py", CODING_OWNER)
    sites: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for relative in paths:
        path = repo_root / relative
        if any(root == path or root in path.parents for root in excluded_roots):
            continue
        text, read_error = store.read_text(path)
        module, syntax_error = store.python_module(path, text) if text is not None else (None, None)
        if module is None:
            reason = read_error or f"syntax error at line {syntax_error.lineno if syntax_error else 0}"
            warnings.append(f"repeat: SKIPPED {relative}: {reason} {CODING_OWNER}")
            continue
        for binding in module.bindings:
            if (binding.name.lstrip("_").isupper() and isinstance(binding.value, ast.Constant)
                    and not isinstance(binding.value.value, bool)):
                sites[binding.name].append((relative, binding.line))
    return warnings + _repeated("constant", "bound in", sites, CODING_OWNER)
