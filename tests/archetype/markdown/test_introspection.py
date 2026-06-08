"""Tests for the template_fields() accessor — heading-field metadata extraction."""

from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel, Field

from archetype.markdown.annotations import (
    AsBulletList,
    AsCodeBlock,
    AsHeading,
    AsNumberedList,
    AsTable,
)
from archetype.markdown.introspection import FieldInfo, template_fields
from archetype.markdown.template_model import MarkdownDocument, MarkdownHeader


class TestTemplateOnAsHeadingFields:
    """For AsHeading-annotated str body fields, template_fields() returns heading
    derived from the field name (snake_case → Title Case) plus the field's
    Pydantic description."""

    def test_single_as_heading_field_returns_one_field_info(self):
        class Doc(MarkdownHeader):
            summary: Annotated[str, AsHeading()] = Field(description="A short summary.")

        result = template_fields(Doc)

        assert len(result) == 1
        assert isinstance(result[0], FieldInfo)

    def test_heading_is_title_case_from_field_name(self):
        class Doc(MarkdownHeader):
            problem_statement: Annotated[str, AsHeading()] = Field(description="The problem.")

        (info,) = template_fields(Doc)

        # snake_to_title capitalizes each word, matching the renderer convention.
        assert info.heading == "Problem Statement"

    def test_description_comes_from_field_description(self):
        class Doc(MarkdownHeader):
            summary: Annotated[str, AsHeading()] = Field(description="A one-liner.")

        (info,) = template_fields(Doc)

        assert info.description == "A one-liner."

    def test_missing_description_yields_none(self):
        class Doc(MarkdownHeader):
            summary: Annotated[str, AsHeading()]

        (info,) = template_fields(Doc)

        assert info.description is None

    def test_multiple_fields_in_declaration_order(self):
        class Doc(MarkdownHeader):
            first: Annotated[str, AsHeading()] = Field(description="First section.")
            second: Annotated[str, AsHeading()] = Field(description="Second section.")
            third: Annotated[str, AsHeading()] = Field(description="Third section.")

        result = template_fields(Doc)

        assert [f.heading for f in result] == ["First", "Second", "Third"]


class TestTemplateOnNestedMarkdownHeader:
    """For body fields typed as a MarkdownHeader subclass, template_fields() uses
    the subclass's `heading` field default as the heading text."""

    def test_nested_header_uses_subclass_heading_default(self):
        class NestedSection(MarkdownHeader):
            heading: str = "Desired outcomes"
            inner: Annotated[str, AsHeading()] = Field(description="Inner body.")

        class Doc(MarkdownHeader):
            section: NestedSection = Field(description="A nested section.")

        (info,) = template_fields(Doc)

        assert info.heading == "Desired outcomes"
        assert info.description == "A nested section."

    def test_nested_header_without_heading_default_raises(self):
        """If the nested MarkdownHeader subclass lacks a heading default,
        template_fields() cannot derive a heading — raises ValueError."""

        class NestedSection(MarkdownHeader):
            inner: Annotated[str, AsHeading()]

        class Doc(MarkdownHeader):
            section: NestedSection = Field(description="...")

        with pytest.raises(ValueError, match="section"):
            template_fields(Doc)


class TestTemplateSkipsStructuralFields:
    """template_fields() must skip 'heading' and 'frontmatter' — they are the document's
    structural heading and metadata, not body sections."""

    def test_heading_is_skipped(self):
        class Doc(MarkdownHeader):
            summary: Annotated[str, AsHeading()] = Field(description="Summary.")

        result = template_fields(Doc)

        # Only 'summary' should appear; 'heading' (inherited from MarkdownHeader) is skipped.
        assert len(result) == 1
        assert result[0].heading == "Summary"

    def test_frontmatter_is_skipped(self):
        class FM(BaseModel):
            slug: str

        class Doc(MarkdownDocument):
            frontmatter: FM | None = None
            summary: Annotated[str, AsHeading()] = Field(description="Summary.")

        result = template_fields(Doc)

        headings = [f.heading for f in result]
        assert "Frontmatter" not in headings
        assert headings == ["Summary"]


class TestTemplateSkipsNonHeadingFields:
    """Non-heading fields (AsCodeBlock, AsBulletList, AsNumberedList, AsTable,
    plain typed fields) are silently skipped — they produce no heading in the
    rendered document so have nothing to contribute to template_fields()."""

    def test_as_bullet_list_is_skipped(self):
        class Doc(MarkdownHeader):
            items: Annotated[list[str], AsBulletList()] = Field(description="Items.")

        assert template_fields(Doc) == []

    def test_as_code_block_is_skipped(self):
        class Doc(MarkdownHeader):
            snippet: Annotated[str, AsCodeBlock()] = Field(description="Code.")

        assert template_fields(Doc) == []

    def test_as_numbered_list_is_skipped(self):
        class Doc(MarkdownHeader):
            steps: Annotated[list[str], AsNumberedList()] = Field(description="Steps.")

        assert template_fields(Doc) == []

    def test_as_table_is_skipped(self):
        class Row(BaseModel):
            a: str

        class Doc(MarkdownHeader):
            rows: Annotated[list[Row], AsTable()] = Field(description="Rows.")

        assert template_fields(Doc) == []

    def test_plain_typed_field_is_skipped(self):
        class Doc(MarkdownHeader):
            raw: str = Field(description="Raw text.")

        assert template_fields(Doc) == []

    def test_mixed_model_returns_only_heading_fields(self):
        """A real contract model with both heading and non-heading fields returns
        only the heading-shaped ones."""

        class Doc(MarkdownHeader):
            code: Annotated[str, AsCodeBlock(language="python")] = Field(description="Code.")
            tags: Annotated[list[str], AsBulletList()] = Field(description="Tags.")
            summary: Annotated[str, AsHeading()] = Field(description="Summary section.")
            detail: Annotated[str, AsHeading()] = Field(description="Detail section.")

        result = template_fields(Doc)

        assert [f.heading for f in result] == ["Summary", "Detail"]


class TestTemplateOnMarkdownDocumentSubclass:
    """template_fields() works on MarkdownDocument subclasses too — same semantics
    as MarkdownHeader, with the inherited frontmatter field also skipped."""

    def test_markdown_document_frontmatter_and_heading_skipped(self):
        class FM(BaseModel):
            slug: str

        class Doc(MarkdownDocument):
            frontmatter: FM | None = None
            summary: Annotated[str, AsHeading()] = Field(description="Summary.")
            detail: Annotated[str, AsHeading()] = Field(description="Detail.")

        result = template_fields(Doc)

        assert [f.heading for f in result] == ["Summary", "Detail"]


class TestFieldInfoShape:
    """FieldInfo is a frozen dataclass with heading and description attributes."""

    def test_field_info_is_hashable_and_immutable(self):
        fi = FieldInfo(heading="X", description="Y")

        # Hashable — usable as a dict key or set member.
        _ = {fi}

        # Frozen — attributes can't be reassigned.
        with pytest.raises((AttributeError, Exception)):
            fi.heading = "Z"  # type: ignore[misc]

    def test_field_info_equality_by_value(self):
        assert FieldInfo(heading="X", description="Y") == FieldInfo(heading="X", description="Y")

    def test_field_info_description_may_be_none(self):
        fi = FieldInfo(heading="X", description=None)
        assert fi.description is None
