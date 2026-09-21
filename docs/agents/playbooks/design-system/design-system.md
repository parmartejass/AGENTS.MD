---
doc_type: playbook
ssot_owner: docs/agents/playbooks/design-system/design-system.md
update_trigger: the token set, scales, interaction states, keyboard model, or accessibility floor change
---

# Design System

Jurisdiction: the declared design token set, visual scales, interaction states, keyboard and focus model, layout density and DPI basis, and the accessibility conformance floor for every user-facing surface.

```yaml
baseline:
  interface: one DTCG-format token file (Design Tokens Format Module) as the sole source of style values
  pattern: "every color, spacing, radius, type, elevation, and duration value is a named token resolved at startup; components consume semantic aliases, never raw values; themes are alias remaps of one global set"
  reason: "the DTCG format is the vendor-neutral interchange for design decisions and is plain JSON loadable with no dependency; inline literals fork the visual system per screen and make contrast unverifiable"
  exception: "a platform-owned system value (native theme color, system font metric) consumed directly when it is the accessibility-correct value and the token records that origin"
```

## Tokens
- The token set MUST be two-layer: global raw values, semantic aliases for intent.
- The token file MUST use the DTCG format with an explicit `$type` on every token.
- Spacing MUST come from one declared base-unit scale and typography from one declared type ramp with a semantic role per step.

## Contrast and color
- Text MUST meet 4.5:1 contrast against its background (3:1 at or above 18.66 px bold or 24 px); control boundaries, focus indicators, and meaning-bearing non-text elements MUST meet 3:1.
- Information MUST NOT be conveyed by color alone; every color-coded state MUST carry a text or shape witness.
- Each theme MUST satisfy every contrast obligation independently.

## States and input
- Every interactive component MUST define rest, hover, focus, pressed, selected, disabled, and error states.
- Every interactive element MUST be reachable and operable by keyboard; Tab order MUST follow reading order; focus MUST NOT be trapped, and every modal MUST define its Escape and return-focus target.
- A focused element MUST show a visible focus indicator at 3:1 that the theme does not suppress and author content does not obscure.
- Every pointer target MUST be at least 24 by 24 device-independent pixels; primary actions MUST be 44 by 44.

## Layout and scale
- Process-level DPI awareness MUST be set before the root window exists; token pixel values are device-independent pixels, and layout MUST remain usable at 200 percent text scale within a declared minimum window size.

## Conformance floor
- Operator surfaces MUST meet WCAG 2.2 AA; contrast, focus visibility, target size, and keyboard operability are the checked criteria.
- A criterion recorded as not met MUST name the blocking platform limitation.

## Design scaffold
```
- token file path and format:
- semantic aliases declared (surface, on-surface, accent, danger, warning, success, disabled):
- theme set (light, dark) and contrast verification per theme:
- type ramp roles and spacing base unit:
- state definitions per interactive component:
- keyboard map (tab order, mnemonics, Escape, return-focus target per modal):
- DPI awareness mode, minimum window size, target sizes:
- conformance floor and recorded unmet criteria with blocking limitation:
```
