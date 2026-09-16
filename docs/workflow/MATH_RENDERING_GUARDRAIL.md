# Math Rendering Guardrail

On 2026-09-15, a Markdown display equation written with LaTeX-style `\[ ... \]` delimiters reached a CodeBinder PDF. In the CodeBinder → nbsphinx → Sphinx path, that syntax leaked internal `nbsphinx-math` role markup into reader-visible text.

The failure passed earlier validation because the Markdown checker only checked `$` / `$$` balance, while PDF validation checked structure and LaTeX build failures but did not inspect rendered text.

The canonical ART guardrail now prevents recurrence at two independent layers:

1. Markdown validation rejects `\[` and `\]` outside code and requires standalone `$$ ... $$` blocks for display math.
2. PDF validation extracts final PDF text and fails if `nbsphinx-math` leakage is present.

ART consumers that use the CodeBinder/nbsphinx PDF path should preserve these two checks when synchronizing generic workflow infrastructure.
