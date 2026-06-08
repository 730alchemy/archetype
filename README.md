# Archetype - Schema-driven Markdown

[![PyPI](https://img.shields.io/pypi/v/archetype-md)](https://pypi.org/project/archetype-md/)
[![CI](https://github.com/monkeynaut-ai/archetype/actions/workflows/ci.yml/badge.svg)](https://github.com/monkeynaut-ai/archetype/actions/workflows/ci.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/archetype-md)](https://pypi.org/project/archetype-md/)
[![License: MIT](https://img.shields.io/pypi/l/archetype-md)](https://github.com/monkeynaut-ai/archetype/blob/main/LICENSE)

Markdown contracts at every agent boundary.

Run the interactive examples described in [examples/README.md](examples/README.md) to better understand the capabilities and benefits of Archetype.

Archetype gives you the tools — backed by Pydantic models — to validate data at agent boundaries and guide agent behavior. In agentic systems, structured data moves between agents as LLM-generated markdown — patient assessments, contract analyses, audit findings, software designs. Because this data is generated and non-deterministic, producers and consumers diverge silently: a required section gets dropped, a heading gets renamed, a field comes back in the wrong format. Nothing catches it, so the error propagates through the system.

Archetype makes the Pydantic model the contract at every agent boundary. At boundaries, it injects the markdown contract into agent instructions and validates markdown the agent generates. Inside agents, field descriptions from the model provide semantic context in prompts. One change to the Pydantic model propagates to every touchpoint of the corresponding markdown file.

## Capabilities

| Capability | Description |
|---|---|
| **Contract generation** | Embed markdown contracts into any text an agent reads: instructions, prompts, skills, etc. |
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

Given this model:

```python
from typing import Annotated

from archetype.markdown import (
    AsBulletList,
    AsHeading,
    MarkdownDocument,
    MarkdownHeader,
    TextTemplate,
    generate_contract,
    parse_markdown_as,
    render_markdown,
)

class Finding(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    recommendations: Annotated[list[str], AsBulletList()]
    description: Annotated[str, AsHeading()]

class Review(MarkdownDocument):
    heading: Annotated[str, TextTemplate("{value}")]
    summary: Annotated[str, AsHeading()]
    findings: list[Finding]

# Generate the markdown contract to embed in an agent instruction
contract = generate_contract(Review)

# Parse markdown back into a validated model instance
review = parse_markdown_as(produced_markdown, Review)

# Render a populated instance back to markdown
output = render_markdown(review)
```

A populated document — what `render_markdown` produces and `parse_markdown_as` consumes — looks like this:

```markdown
# Q4 Code Review

## Summary

Two issues found, both fixable with minor changes.

## Findings

### Finding 1 — SQL Injection in login handler

- Use parameterised queries
- Validate all user input at the controller layer

#### Description

The login handler at auth.py:42 builds SQL by string concatenation,
allowing an attacker to inject arbitrary SQL.

### Finding 2 — Missing rate limit on password reset

- Add a rate limit of 5 requests per minute per IP
- Return a generic error message to avoid user enumeration

#### Description

The password reset endpoint accepts unlimited requests,
enabling brute-force and enumeration attacks.
```

## Modules

### `archetype.markdown`

Typed markdown documents backed by Pydantic models.

| Symbol | Purpose |
|--------|---------|
| `MarkdownDocument` | Base class for top-level documents (adds optional YAML frontmatter) |
| `MarkdownHeader` | Base class for heading-shaped sub-documents |
| `generate_contract(cls)` | Generate the markdown contract — annotated structure with placeholder comments and inline field descriptions |
| `render_markdown(obj)` | Render a populated instance to markdown |
| `parse_markdown_as(text, cls)` | Parse markdown and return a validated instance |
| `template_fields(cls)` | Return heading text and description for each heading-shaped field; non-heading fields are skipped |
| `extract_subtree(text, *, heading_level, title_match)` | Extract a uniquely named heading subtree and rebase it to level 1 |

**Field annotations** (attached via `Annotated[T, ...]`):

| Annotation | Field type | Renders as |
|-----------|-----------|-----------|
| `AsHeading()` | `str` | Markdown heading section |
| `AsCodeBlock(language=...)` | `str` | Fenced code block |
| `AsBulletList()` | `list[str]` | Bullet list |
| `AsNumberedList()` | `list[str]` | Numbered list |
| `AsTable()` | `list[BaseModel]` | Markdown table |
| `TextTemplate("{value}")` | `str` (heading field) | Formatted heading text |

### `archetype.templating`

Jinja-based template resolution with markdown-aware globals.

```python
from archetype.templating import resolve

instructions = resolve(
    template_text,
    feature=state.feature_definition,
)
```

`resolve` runs with strict undefined semantics — any missing variable raises `jinja2.UndefinedError` immediately. Two globals are available inside every template: `template_fields(ModelClass)` and `generate_contract(ModelClass)`.

## Design

**The model is the contract.** Annotations on fields drive all rendering and parsing behaviour. No separate config, no code generation — change the model, everything updates.

**Strict by default.** `parse_markdown_as` raises `MarkdownValidationError` with field-localized messages on any mismatch. `resolve` raises on undefined template paths. Silent partial results are not produced.

## Development

```bash
pdm install
pdm run test
pdm run lint
pdm run check-format
pdm run typecheck
```
