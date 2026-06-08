"""Example: Round-trip integrity — render_instance and validate_markdown are inverses.

A populated model instance rendered to markdown and parsed back produces an
identical instance. The Pydantic model is a lossless codec: the same contract
that guides the agent also validates what it produces.

This example does not call an LLM.
"""

import inspect
from typing import Annotated

from pydantic import Field
from rich.console import Console
from rich.rule import Rule
from rich.syntax import Syntax

from archetype.markdown import (
    AsBulletList,
    AsHeading,
    MarkdownDocument,
    MarkdownHeader,
    TextTemplate,
    render_instance,
    validate_markdown,
)

console = Console()


class Requirement(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Requirement {ordinal} — {value}")]
    acceptance_criteria: Annotated[list[str], AsBulletList()] = Field(
        description="Conditions that must be true for this requirement to be considered met."
    )
    rationale: Annotated[str, AsHeading()] = Field(description="Why this requirement exists.")


class FeatureSpec(MarkdownDocument):
    heading: Annotated[str, TextTemplate("{value}")]
    overview: Annotated[str, AsHeading()] = Field(
        description="One paragraph describing what this feature does and why."
    )
    requirements: list[Requirement]


console.print(
    "\n[bold]Round-trip integrity — render and parse are inverses[/bold]\n\n"
    "[dim]Step 1:[/dim] Declare a Pydantic model that defines the markdown contract.\n"
    "[dim]Step 2:[/dim] Populate a model instance with data.\n"
    "[dim]Step 3:[/dim] Call [cyan]render_instance()[/cyan] to produce markdown.\n"
    "[dim]Step 4:[/dim] Call [cyan]validate_markdown()[/cyan] to parse it back.\n"
    "[dim]Step 5:[/dim] The recovered instance is identical to the original.\n"
)
console.input("[dim]Press Enter to see the model...[/dim]")

console.print()
console.print(Rule("model"))
console.print(
    Syntax(
        inspect.getsource(Requirement) + "\n\n" + inspect.getsource(FeatureSpec),
        "python",
        theme="monokai",
    )
)

console.input("\n[dim]Press Enter to see the populated instance...[/dim]")

original = FeatureSpec(
    heading="Offline Mode",
    overview=(
        "Allow the app to function without a network connection by caching "
        "the last known state locally and syncing when connectivity is restored."
    ),
    requirements=[
        Requirement(
            heading="local cache",
            acceptance_criteria=[
                "App loads cached data within 200ms when offline.",
                "Cache persists across app restarts.",
            ],
            rationale="Users in low-connectivity environments need a responsive experience.",
        ),
        Requirement(
            heading="sync on reconnect",
            acceptance_criteria=[
                "Changes made offline are uploaded within 30s of reconnection.",
                "Conflicts are resolved using last-write-wins.",
            ],
            rationale="Data written offline must not be silently discarded.",
        ),
    ],
)

console.print()
console.print(Rule("populated instance"))
console.print(
    Syntax(original.model_dump_json(indent=2, exclude_none=True), "json", theme="monokai")
)

console.input("\n[dim]Press Enter to see the rendered markdown...[/dim]")

rendered = render_instance(original)

console.print()
console.print(Rule("rendered markdown"))
print(rendered)

console.input("[dim]Press Enter to parse the markdown back and verify round-trip...[/dim]")

recovered = validate_markdown(rendered, FeatureSpec)

assert recovered == original, "Round-trip failed — instances are not equal."

console.print()
console.print(Rule("result"))
console.print(
    "\n[green]✓[/green] [bold]Round-trip verified.[/bold] The recovered instance is"
    " identical to the original.\n"
)
console.print("[dim]recovered == original[/dim]  →  [green]True[/green]\n")
