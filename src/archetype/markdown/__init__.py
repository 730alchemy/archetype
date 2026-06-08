"""Typed markdown documents backed by Pydantic models.

Quick example:

    from typing import Annotated
    from archetype.markdown import (
        MarkdownDocument, MarkdownHeader,
        AsHeading, TextTemplate,
        generate_contract, parse_markdown_as,
        template_fields,
    )

    class Finding(MarkdownHeader):
        heading: Annotated[str, TextTemplate("Finding {ordinal} - {value}")]
        description: Annotated[str, AsHeading()]

    class Review(MarkdownDocument):
        heading: Annotated[str, TextTemplate("{value}")]
        summary: Annotated[str, AsHeading()]
        findings: list[Finding]

    template = generate_contract(Review)
    review = parse_markdown_as(produced_md, Review)
    fields = template_fields(Review)
"""

from archetype.markdown.annotations import (
    AsBulletList,
    AsCodeBlock,
    AsHeading,
    AsNumberedList,
    AsTable,
    TextTemplate,
)
from archetype.markdown.errors import (
    MarkdownError,
    MarkdownExtractionError,
    MarkdownTemplateError,
    MarkdownValidationError,
)
from archetype.markdown.extractor import extract_subtree
from archetype.markdown.introspection import FieldInfo, template_fields
from archetype.markdown.parser import parse_markdown_as
from archetype.markdown.renderer import generate_contract, render_markdown
from archetype.markdown.template_model import MarkdownDocument, MarkdownHeader

__all__ = [
    "AsBulletList",
    "AsCodeBlock",
    "AsHeading",
    "AsNumberedList",
    "AsTable",
    "FieldInfo",
    "MarkdownDocument",
    "MarkdownError",
    "MarkdownExtractionError",
    "MarkdownHeader",
    "MarkdownTemplateError",
    "MarkdownValidationError",
    "TextTemplate",
    "extract_subtree",
    "generate_contract",
    "parse_markdown_as",
    "render_markdown",
    "template_fields",
]
