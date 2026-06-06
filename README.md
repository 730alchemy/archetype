# Archetype

Type safety for agents and agentic systems.

Archetype gives you the tools — backed by Pydantic models — to validate data at agent boundaries and guide agent behavior. In agentic systems, structured data moves between agents as LLM-generated markdown — patient assessments, contract analyses, audit findings, software designs. Because this data is generated and non-deterministic, producers and consumers diverge silently: a required section gets dropped, a heading gets renamed, a field comes back in the wrong format. The failure surfaces and nothing catches it, so the error propagates through the system silently.

Archetype makes the Pydantic model the contract at every agent boundary. At boundaries, it injects markdown format specifications into the agent and validates markdown files the agent generates. Inside agents, field descriptions from the model provide semantic context in instructions and prompts. One change to the Pydantic model propagates to every touchpoint of the corresponding markdown file.

## Capabilities

| Capability | Description |
|---|---|
| **Template generation** | Embed markdown format specifications into any text an agent reads: instructions, prompts, skills, etc. |
| **Markdown parsing and validation** | Validate agent-generated markdown against the model — missing sections, misnamed fields, and type mismatches surface as errors you can prompt the agent to correct. |
| **Annotation-driven layout** | Declare how each field renders — as a heading, code block, list, or table — directly on the model. No separate template files or format strings. |
| **Structural validation at class definition** | Markdown modeling errors are caught at definition time, not mid-run. |
| **Instance rendering** | Render a populated model instance to well-formed markdown — no format strings, no templates to maintain. |
| **Field descriptions as semantic context** | Field descriptions flow from the model into agent instructions, giving agents the semantic context they need to reason correctly. |

## Installation

```bash
pip install archetype-md
```

## Quickstart

```python
from typing import Annotated
from archetype.markdown import (
    MarkdownDocument,
    MarkdownHeader,
    AsHeading,
    AsBulletList,
    TextTemplate,
    render_template,
    render_instance,
    validate_markdown,
)

class Finding(MarkdownHeader):
    title: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    description: Annotated[str, AsHeading()]
    recommendations: Annotated[list[str], AsBulletList()]

class Review(MarkdownDocument):
    title: Annotated[str, TextTemplate("{value}")]
    summary: Annotated[str, AsHeading()]
    findings: list[Finding]

# Generate a blank template (e.g. to hand to an LLM)
template = render_template(Review)

# Parse markdown back into a validated model instance
review = validate_markdown(produced_markdown, Review)

# Render a populated instance back to markdown
output = render_instance(review)
```

## Modules

### `archetype.markdown`

Typed markdown documents backed by Pydantic models.

| Symbol | Purpose |
|--------|---------|
| `MarkdownDocument` | Base class for top-level documents (adds optional YAML frontmatter) |
| `MarkdownHeader` | Base class for heading-shaped sub-documents |
| `render_template(cls)` | Emit an annotated skeleton with placeholder comments |
| `render_instance(obj)` | Render a populated instance to markdown |
| `validate_markdown(text, cls)` | Parse markdown and return a validated instance |
| `template_fields(cls)` | Iterate `FieldInfo` entries for use in Jinja templates |
| `extract_subtree(text, heading)` | Extract a named section from markdown text |

**Field annotations** (attached via `Annotated[T, ...]`):

| Annotation | Field type | Renders as |
|-----------|-----------|-----------|
| `AsHeading()` | `str` | Markdown heading section |
| `AsCodeBlock(language=...)` | `str` | Fenced code block |
| `AsBulletList()` | `list[str]` | Bullet list |
| `AsNumberedList()` | `list[str]` | Numbered list |
| `AsTable()` | `list[BaseModel]` | Markdown table |
| `TextTemplate("{value}")` | `str` (title field) | Formatted heading text |

### `archetype.templating`

Jinja-based template resolution with markdown-aware globals.

```python
from archetype.templating import resolve

instructions = resolve(
    template_text,
    feature=state.feature_definition,
)
```

`resolve` runs with strict undefined semantics — any missing variable raises `jinja2.UndefinedError` immediately. Two globals are available inside every template: `template_fields(ModelClass)` and `render_template(ModelClass)`.

## Design

**The model is the contract.** Annotations on fields drive all rendering and parsing behaviour. No separate config, no code generation — change the model, everything updates.

**Strict by default.** `validate_markdown` raises `MarkdownValidationError` with field-localized messages on any mismatch. `resolve` raises on undefined template paths. Silent partial results are not produced.

## Development

```bash
pdm install
pdm run test
pdm run lint
pdm run typecheck
```
