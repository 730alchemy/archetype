"""End-to-end tests for the public markdown-to-model parser."""

from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel, Field
from tests.archetype.markdown.fixtures.sample_models import (
    Finding,
    HeaderWithSummary,
    ReviewerMetadata,
    ReviewerOutput,
)

from archetype.markdown.annotations import AsCodeBlock, AsTable, TextTemplate
from archetype.markdown.errors import MarkdownValidationError
from archetype.markdown.parser import parse_markdown_as
from archetype.markdown.renderer import render_markdown
from archetype.markdown.template_model import MarkdownHeader


class TestValidateMarkdown:
    def test_simple_header_with_summary_round_trip(self):
        original = HeaderWithSummary(heading="Doc", summary="The work is good.")
        rendered = render_markdown(original)
        parsed = parse_markdown_as(rendered, HeaderWithSummary)
        assert parsed.heading == "Doc"
        assert "The work is good." in parsed.summary

    def test_full_reviewer_output_round_trip(self):
        original = ReviewerOutput(
            heading="Review of cs7-plan4",
            frontmatter=ReviewerMetadata(change_set_name="cs7", commit_range="abc..def"),
            next_steps=["A", "B"],
            summary="Looks good.",
            findings=[
                Finding(
                    heading="t1",
                    code="x = 1",
                    tags=["x"],
                    description="d",
                    rationale="r",
                ),
            ],
        )
        rendered = render_markdown(original)
        parsed = parse_markdown_as(rendered, ReviewerOutput)
        assert parsed.heading == "Review of cs7-plan4"
        assert parsed.frontmatter is not None
        assert parsed.frontmatter.change_set_name == "cs7"
        assert parsed.next_steps == ["A", "B"]
        assert len(parsed.findings) == 1
        assert parsed.findings[0].heading == "t1"

    def test_invalid_markdown_raises_validation_error(self):
        with pytest.raises(MarkdownValidationError):
            parse_markdown_as("just text\n", HeaderWithSummary)

    def test_malformed_frontmatter_yaml_raises_markdown_validation_error(self):
        bad = "---\nkey: [unclosed\n---\n\n# Doc\n\n## Summary\n\ntext\n"
        with pytest.raises(MarkdownValidationError, match=r"[Ff]rontmatter"):
            parse_markdown_as(bad, HeaderWithSummary)

    def test_frontmatter_schema_mismatch_raises_markdown_validation_error(self):
        # ReviewerMetadata requires both change_set_name and commit_range.
        # Omit commit_range to force a pydantic.ValidationError at the boundary.
        bad = (
            "---\nchange_set_name: cs7\n---\n\n# Doc\n\n1. step\n\n## Summary\n\nx\n\n## Findings\n"
        )
        with pytest.raises(MarkdownValidationError, match=r"[Ff]rontmatter"):
            parse_markdown_as(bad, ReviewerOutput)

    @pytest.mark.parametrize("yaml_value", ["hello", "- one\n- two"])
    def test_non_mapping_frontmatter_raises_markdown_validation_error(self, yaml_value: str):
        bad = f"---\n{yaml_value}\n---\n\n# Doc\n\n## Summary\n\ntext\n"

        with pytest.raises(
            MarkdownValidationError,
            match=r"Frontmatter.*mapping",
        ):
            parse_markdown_as(bad, HeaderWithSummary)

    def test_invalid_table_cell_raises_field_localized_markdown_validation_error(self):
        class Component(BaseModel):
            name: str
            replicas: int

        class Inventory(MarkdownHeader):
            components: Annotated[list[Component], AsTable()]

        bad = "# Inventory\n\n| Name | Replicas |\n|---|---|\n| api | not-an-integer |\n"

        with pytest.raises(
            MarkdownValidationError,
            match=r"Inventory\.components row 1.*replicas",
        ):
            parse_markdown_as(bad, Inventory)

    def test_repeated_value_placeholder_round_trips(self):
        class RepeatedHeading(MarkdownHeader):
            heading: Annotated[str, TextTemplate("{value} / {value}")]

        original = RepeatedHeading(heading="Summary")

        recovered = parse_markdown_as(render_markdown(original), RepeatedHeading)

        assert recovered == original

    def test_table_column_mismatch_raises_markdown_validation_error(self):
        class Row(BaseModel):
            name: str
            value: str

        class WithTable(MarkdownHeader):
            items: Annotated[list[Row], AsTable()]

        bad = "# Doc\n\n| Name | Wrong |\n|---|---|\n| foo | bar |\n"

        with pytest.raises(MarkdownValidationError, match=r"column mismatch"):
            parse_markdown_as(bad, WithTable)

    def test_missing_required_element_raises_markdown_validation_error(self):
        class WithCode(MarkdownHeader):
            snippet: Annotated[str, AsCodeBlock()]

        with pytest.raises(MarkdownValidationError, match=r"snippet"):
            parse_markdown_as("# Heading\n\nNo code block here.\n", WithCode)

    def test_text_template_with_no_value_placeholder(self):
        class FixedHeading(MarkdownHeader):
            heading: Annotated[str, TextTemplate("Fixed Title")]

        instance = parse_markdown_as("# Fixed Title\n", FixedHeading)

        assert instance.heading == "Fixed Title"

    def test_model_field_constraint_raises_markdown_validation_error(self):
        class ConstrainedHeading(MarkdownHeader):
            heading: str = Field(min_length=10)

        with pytest.raises(
            MarkdownValidationError,
            match=r"ConstrainedHeading.*heading",
        ):
            parse_markdown_as("# Short\n", ConstrainedHeading)
