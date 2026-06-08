"""Property tests: parse(render(instance)) == instance for every Phase-1 shape."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from tests.archetype.markdown.fixtures.sample_models import (
    Finding,
    HeaderWithSummary,
    ReviewerMetadata,
    ReviewerOutput,
    SimpleHeader,
)

from archetype.markdown.annotations import AsHeading, AsTable
from archetype.markdown.parser import parse_markdown_as
from archetype.markdown.renderer import render_markdown
from archetype.markdown.template_model import MarkdownHeader


class TestRoundTrip:
    def test_simple_header(self):
        original = SimpleHeader(heading="hello world")
        recovered = parse_markdown_as(render_markdown(original), SimpleHeader)
        assert recovered == original

    def test_header_with_summary(self):
        original = HeaderWithSummary(heading="doc title", summary="The body content here.")
        recovered = parse_markdown_as(render_markdown(original), HeaderWithSummary)
        assert recovered.heading == original.heading
        assert original.summary in recovered.summary  # serialization may add whitespace

    def test_finding(self):
        original = Finding(
            heading="missing tests",
            code="def foo(): pass",
            tags=["a", "b"],
            description="No tests.",
            rationale="TDD required.",
        )
        # Render at level 3 (as if inside a list at level 2)
        rendered = render_markdown(original, current_level=3)
        # Need to be careful: standalone validate sees level-3 as top, but
        # parser expects level-1 top. Use extract_subtree first.
        from archetype.markdown.extractor import extract_subtree

        fragment = extract_subtree(
            rendered, heading_level=3, title_match="Finding 1 - missing tests"
        )
        recovered = parse_markdown_as(fragment, Finding)
        assert recovered.heading == "missing tests"
        assert recovered.code.strip() == "def foo(): pass"
        assert recovered.tags == ["a", "b"]
        assert "No tests" in recovered.description
        assert "TDD required" in recovered.rationale

    def test_full_reviewer_output(self):
        original = ReviewerOutput(
            heading="Review of foo",
            frontmatter=ReviewerMetadata(change_set_name="x", commit_range="a..b"),
            next_steps=["s1", "s2"],
            summary="Clean.",
            findings=[
                Finding(heading="t1", code="c", tags=["x"], description="d", rationale="r"),
                Finding(heading="t2", code="c2", tags=[], description="d2", rationale="r2"),
            ],
        )
        recovered = parse_markdown_as(render_markdown(original), ReviewerOutput)
        assert recovered.heading == original.heading
        assert recovered.frontmatter == original.frontmatter
        assert recovered.next_steps == original.next_steps
        assert original.summary in recovered.summary
        assert len(recovered.findings) == 2
        assert recovered.findings[0].heading == "t1"
        assert recovered.findings[1].heading == "t2"

    def test_empty_findings_list_round_trips(self):
        """A reviewer document with zero findings should round-trip cleanly."""
        original = ReviewerOutput(
            heading="Empty review",
            next_steps=[],
            summary="Nothing to report.",
            findings=[],
        )
        recovered = parse_markdown_as(render_markdown(original), ReviewerOutput)
        assert recovered.findings == []
        assert recovered.heading == "Empty review"

    def test_as_heading_body_with_sub_heading_round_trips(self):
        """An AsHeading-on-str body field whose value contains a sub-heading
        must survive the round-trip with sub-heading preserved (at level 2)."""

        class WithStructuredBody(MarkdownHeader):
            details: Annotated[str, AsHeading()]

        original = WithStructuredBody(
            heading="Doc",
            details="## Sub-section\n\nNested content here.",
        )
        rendered = render_markdown(original)
        recovered = parse_markdown_as(rendered, WithStructuredBody)
        # Body content survives — sub-heading text and prose both present
        assert "Sub-section" in recovered.details
        assert "Nested content here." in recovered.details

    def test_as_heading_body_with_two_level_sub_headings_round_trips(self):
        """Two-level sub-heading nesting inside an AsHeading body must be
        preserved on round-trip. Bug fix: prior recursive serialization
        emitted both levels as level 2, collapsing the hierarchy."""

        class WithDeepBody(MarkdownHeader):
            details: Annotated[str, AsHeading()]

        original = WithDeepBody(
            heading="Doc",
            details="## Sub-section\n\n### Sub-sub-section\n\nDeep content.",
        )
        rendered = render_markdown(original)
        recovered = parse_markdown_as(rendered, WithDeepBody)
        assert "## Sub-section" in recovered.details
        assert "### Sub-sub-section" in recovered.details
        assert "Deep content." in recovered.details

    def test_table_cells_containing_pipes_round_trip(self):
        class Component(BaseModel):
            name: str
            owner: str

        class Inventory(MarkdownHeader):
            components: Annotated[list[Component], AsTable()]

        original = Inventory(
            heading="Service Inventory",
            components=[
                Component(name="api|worker", owner="Platform|Infrastructure"),
                Component(name=r"literal\|separator", owner="Developer Experience"),
            ],
        )

        recovered = parse_markdown_as(render_markdown(original), Inventory)

        assert recovered == original

    def test_table_inside_heading_body_preserves_escaped_pipe(self):
        class Report(MarkdownHeader):
            details: Annotated[str, AsHeading()]

        original = Report(
            heading="Service Report",
            details=("| Name | Owner |\n|---|---|\n| api\\|worker | Platform |"),
        )

        recovered = parse_markdown_as(render_markdown(original), Report)

        assert recovered == original
