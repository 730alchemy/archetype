This project uses **Jig** for development workflow management.

# Archetype

Pydantic as source of truth for agentic systems. Declare a Pydantic model once; every derived artifact — markdown templates, renderers, parsers, validators, JSON schemas — updates automatically when the model changes.

## Core Idea

The model declaration is the contract. Annotations on fields drive all rendering and parsing behaviour. No hand-written templates, no hand-maintained format strings — the model is the template.

## Modules

### `archetype.markdown`

Typed markdown documents backed by Pydantic models.

- **`MarkdownHeader`** — base class for heading-shaped sub-documents. Requires a `title: str` field. Body fields follow in declaration order.
- **`MarkdownDocument`** — extends `MarkdownHeader` with an optional YAML frontmatter field.
- **Annotations** — attached via `Annotated[T, ...]` to control how a field renders and parses:
  - `AsHeading` — `str` field rendered as a markdown heading section
  - `AsCodeBlock(language=...)` — `str` field rendered as a fenced code block
  - `AsBulletList` / `AsNumberedList` — `list[str]` rendered as a list
  - `AsTable` — `list[BaseModel]` rendered as a markdown table
  - `TextTemplate(template)` — format string for the heading title (`{value}`, `{ordinal}`)
- **`generate_contract(ModelClass)`** — emit the annotated skeleton (placeholder comments)
- **`render_markdown(instance)`** — emit a populated document
- **`parse_markdown_as(text, ModelClass)`** — parse markdown and return a validated instance; raises `MarkdownValidationError` with field-localized messages on failure
- **`template_fields(ModelClass)`** — iterate `FieldInfo` entries (`.heading`, `.description`) for introspection in Jinja templates
- **`extract_subtree(text, heading)`** — extract a named heading section from markdown text

### `archetype.templating`

Jinja-based template resolution with markdown-aware globals.

- **`resolve(template_text, **context)`** — render a Jinja template against a context dict; raises `jinja2.UndefinedError` on undefined paths (strict semantics)
- **`build_environment()`** — returns a pre-configured Jinja environment with `template_fields` and `generate_contract` registered as globals

`resolve()` is the primary entry point for agent instruction providers. Templates use only `{{ path }}`, `{% for %}...{% endfor %}`, and the two registered globals — no filters, conditionals, macros, or inheritance without deliberate intent.

## Design Principles

**Model is the contract.** Annotations on the model class drive all behaviour. The renderer, parser, and introspection engine read `model_fields[name].metadata` at runtime — no separate config files, no code generation step.

**Strict by default.** `parse_markdown_as` raises on any field mismatch. `resolve` raises on any undefined template variable. Silent partial results are rejected.

**No cross-cutting state.** All functions are stateless — they accept a model class or instance and return a value. No global registries, no singletons.

## Development Practices

- **Test-Driven Development**: write tests before implementation. Red-green-refactor.
- **Trunk-based development**: work on `main` with short-lived branches.

## Tech Stack

- **Python 3.14**
- **Pydantic** — model declaration and validation
- **markdown-it-py** — markdown parsing (AST normalization layer)
- **Jinja2** — template resolution
- **PyYAML** — frontmatter serialization
- **PDM** — package manager
- **Pytest** — test framework

## Project Structure

```
src/archetype/
  markdown/          — typed markdown documents
    annotations.py   — field annotation dataclasses
    template_model.py — MarkdownHeader, MarkdownDocument bases
    renderer.py      — generate_contract, render_markdown
    parser.py        — parse_markdown_as entry point
    extractor.py     — extract_subtree
    introspection.py — template_fields, FieldInfo
    _ast_normalizer.py — markdown-it AST → NormalizedDocument
    _projector.py    — NormalizedDocument → Pydantic instance
    _shared.py       — shared annotation helpers
    meta_validation.py — structural checks at class-definition time
    elements.py      — AST element types
    errors.py        — MarkdownError hierarchy
  templating/        — Jinja resolution
    environment.py   — build_environment
    resolve.py       — resolve()
tests/archetype/     — mirrors src layout
```

## Commands

- `pdm install`: install dependencies
- `pdm run test`: run tests
- `pdm run lint`: check lint without modifying files
- `pdm run lint-fix`: apply automatic lint fixes
- `pdm run format`: format
- `pdm run check-format`: check formatting without modifying files
- `pdm run typecheck`: run Pyright

## Data Model Conventions

- **Enumerated values** → `StrEnum` if code branches on the value; free `str` with suggested taxonomy in the field description otherwise
- **`Literal` is forbidden** for enumerated values — use `StrEnum` so LSP navigation works
- **Every boundary type** is a Pydantic `BaseModel` — runtime validation, schema generation, JSON round-trip
