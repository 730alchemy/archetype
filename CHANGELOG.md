# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-06-08

First public release of `archetype-md`.

### Added

- Typed markdown documents backed by Pydantic models.
- Markdown contract generation with `generate_contract()`.
- Markdown rendering with `render_markdown()`.
- Markdown parsing and validation with `parse_markdown_as()`.
- Annotation-driven layout for headings, code blocks, bullet lists, numbered lists, and tables.
- YAML frontmatter support on top-level documents.
- Jinja-based template resolution with `resolve()`.
- Interactive examples covering round-trip parsing, prompt composition, frontmatter, and tables.

### Notes

- Requires Python 3.12 or newer.
- The published package name is `archetype-md`.
