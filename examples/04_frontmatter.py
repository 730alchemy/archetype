"""Example: YAML frontmatter — structured metadata on a MarkdownDocument.

MarkdownDocument supports an optional frontmatter field typed as a Pydantic
BaseModel. When present, it renders as a YAML block at the top of the document
and is parsed back into the typed model by validate_markdown.

Frontmatter is useful for metadata that travels with the document but is not
part of its narrative structure: author, status, version, timestamps, IDs.

This example does not call an LLM.
"""

import inspect
from typing import Annotated

from pydantic import BaseModel, Field
from rich.console import Console
from rich.rule import Rule
from rich.syntax import Syntax

from archetype.markdown import (
    AsBulletList,
    AsHeading,
    MarkdownDocument,
    MarkdownHeader,
    TextTemplate,
    generate_contract,
    render_instance,
    validate_markdown,
)

console = Console()


class ReviewMeta(BaseModel):
    change_set: str = Field(description="Identifier for the change set under review.")
    commit_range: str = Field(description="Git commit range, e.g. 'abc123..def456'.")
    status: str = Field(description="One of: draft, approved, rejected.")


class Finding(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    recommendations: Annotated[list[str], AsBulletList()] = Field(
        description="Concrete remediation steps."
    )
    description: Annotated[str, AsHeading()] = Field(
        description="What the vulnerability is and how it could be exploited."
    )


class CodeReview(MarkdownDocument):
    frontmatter: ReviewMeta | None = None
    heading: Annotated[str, TextTemplate("{value}")]
    summary: Annotated[str, AsHeading()] = Field(description="Overall assessment in one paragraph.")
    findings: list[Finding]


console.print(
    "\n[bold]YAML frontmatter — structured metadata on a MarkdownDocument[/bold]\n\n"
    "[dim]Step 1:[/dim] Define a [cyan]BaseModel[/cyan] for the frontmatter schema.\n"
    "[dim]Step 2:[/dim] Declare [cyan]frontmatter: FrontmatterModel | None = None[/cyan]"
    " as the first field on a [cyan]MarkdownDocument[/cyan] subclass.\n"
    "[dim]Step 3:[/dim] Create a Pydantic model instance with data.\n"
    "[dim]Step 4:[/dim] Call [cyan]render_instance()[/cyan] — frontmatter renders as a YAML"
    " block.\n"
    "[dim]Step 5:[/dim] Call [cyan]validate_markdown()[/cyan] to parse the markdown back into"
    " a Pydantic model instance — frontmatter is recovered as a typed object.\n"
)
console.input("[dim]Press Enter to see the model...[/dim]")

console.print()
console.print(Rule("model"))
console.print(
    Syntax(
        inspect.getsource(ReviewMeta)
        + "\n\n"
        + inspect.getsource(Finding)
        + "\n\n"
        + inspect.getsource(CodeReview),
        "python",
        theme="monokai",
    )
)

console.input("\n[dim]Press Enter to see the markdown contract...[/dim]")

console.print()
console.print(Rule("markdown contract"))
console.print(Syntax(generate_contract(CodeReview), "text", theme="monokai"))

console.input("[dim]Press Enter to see the Pydantic model instance...[/dim]")

review = CodeReview(
    frontmatter=ReviewMeta(
        change_set="cs-42",
        commit_range="a1b2c3..d4e5f6",
        status="approved",
    ),
    heading="Code Review — Authentication Refactor",
    summary="Two findings, both addressed. The refactor is safe to merge.",
    findings=[
        Finding(
            heading="hardcoded secret key",
            recommendations=[
                "Move SECRET_KEY to an environment variable.",
                "Rotate the key immediately in all environments.",
            ],
            description=(
                "The Django SECRET_KEY is hardcoded in settings.py and committed to "
                "version control, exposing it to anyone with repository access."
            ),
        ),
    ],
)

console.print()
console.print(Rule("Pydantic model instance"))
console.print(Syntax(review.model_dump_json(indent=2, exclude_none=True), "json", theme="monokai"))

console.input("\n[dim]Press Enter to see the rendered markdown...[/dim]")

rendered = render_instance(review)

console.print()
console.print(Rule("rendered markdown"))
console.print(Syntax(rendered, "text", theme="monokai"))

console.input(
    "\n[dim]Press Enter to parse the markdown back into a Pydantic model instance...[/dim]"
)

recovered = validate_markdown(rendered, CodeReview)

assert recovered == review, "Round-trip failed — instances are not equal."

console.print()
console.print(Rule("result"))
console.print(
    Syntax(
        "# review is the Pydantic model instance we created in step 3\n"
        "rendered = render_instance(review)\n"
        "\n"
        "recovered = validate_markdown(rendered, CodeReview)\n"
        "\n"
        "recovered.frontmatter.change_set   # 'cs-42'\n"
        "recovered.frontmatter.commit_range  # 'a1b2c3..d4e5f6'\n"
        "recovered.frontmatter.status        # 'approved'\n"
        "\n"
        "recovered == review",
        "python",
        theme="monokai",
    )
)
console.print(
    "\n[green]✓[/green] [bold]True[/bold] — frontmatter parsed back into a typed Pydantic"
    " model instance.\n"
)
