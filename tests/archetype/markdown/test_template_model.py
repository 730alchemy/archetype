"""Tests for MarkdownHeader and MarkdownDocument base classes."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from archetype.markdown.template_model import MarkdownDocument, MarkdownHeader


class TestMarkdownHeaderHeading:
    """MarkdownHeader requires a heading field on every subclass."""

    def test_given_heading_when_constructed_then_heading_set(self):
        class SimpleHeader(MarkdownHeader):
            pass

        h = SimpleHeader(heading="My Heading")
        assert h.heading == "My Heading"

    def test_missing_heading_raises_validation_error(self):
        class SimpleHeader(MarkdownHeader):
            pass

        with pytest.raises(ValidationError, match="heading"):
            SimpleHeader()  # type: ignore[call-arg]

    def test_subclass_can_have_additional_fields(self):
        class WithBody(MarkdownHeader):
            description: str

        w = WithBody(heading="X", description="Y")
        assert w.heading == "X"
        assert w.description == "Y"


class FrontmatterSchema(BaseModel):
    name: str
    version: int


class TestMarkdownDocument:
    """MarkdownDocument extends MarkdownHeader with an optional frontmatter field."""

    def test_inherits_heading_from_markdown_header(self):
        class Doc(MarkdownDocument):
            pass

        d = Doc(heading="hello")
        assert d.heading == "hello"
        assert d.frontmatter is None

    def test_subclass_can_override_frontmatter_type(self):
        class Doc(MarkdownDocument):
            frontmatter: FrontmatterSchema | None = None

        d = Doc(heading="hello", frontmatter=FrontmatterSchema(name="x", version=1))
        assert d.frontmatter is not None
        assert d.frontmatter.name == "x"

    def test_frontmatter_optional_default_none(self):
        class Doc(MarkdownDocument):
            frontmatter: FrontmatterSchema | None = None

        d = Doc(heading="hello")
        assert d.frontmatter is None

    def test_markdown_document_is_markdown_header(self):
        assert issubclass(MarkdownDocument, MarkdownHeader)
