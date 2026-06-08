"""Tests for the public API surface of archetype.markdown."""

from __future__ import annotations


class TestPublicAPI:
    """Importing from archetype.markdown reaches every documented symbol."""

    def test_all_documented_symbols_importable(self):
        from archetype.markdown import (
            AsBulletList,
            AsCodeBlock,
            AsHeading,
            AsNumberedList,
            AsTable,
            MarkdownDocument,
            MarkdownExtractionError,
            MarkdownHeader,
            MarkdownTemplateError,
            MarkdownValidationError,
            TextTemplate,
            extract_subtree,
            generate_contract,
            parse_markdown_as,
            render_markdown,
        )

        # Existence of each symbol is the assertion.
        assert all(
            [
                MarkdownHeader,
                MarkdownDocument,
                AsHeading,
                AsCodeBlock,
                AsTable,
                AsBulletList,
                AsNumberedList,
                TextTemplate,
                generate_contract,
                render_markdown,
                parse_markdown_as,
                extract_subtree,
                MarkdownTemplateError,
                MarkdownValidationError,
                MarkdownExtractionError,
            ]
        )
