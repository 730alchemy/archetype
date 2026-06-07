"""Example: Embedding a markdown format specification in an LLM system prompt.

Declare a Pydantic model for the shape of a markdown document. Call
render_template() to produce a skeleton. Embed that skeleton in a system
prompt to define the markdown contract — the structure the LLM must produce
or consume.

This example does not call an LLM.
"""

import inspect
from typing import Annotated

from rich.console import Console
from rich.rule import Rule
from rich.syntax import Syntax

from archetype.markdown import (
    AsBulletList,
    AsCodeBlock,
    AsHeading,
    MarkdownDocument,
    MarkdownHeader,
    TextTemplate,
    render_template,
)

console = Console()


class Finding(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    # Non-heading fields first:
    affected_code: Annotated[str, AsCodeBlock(language="python")]
    recommendations: Annotated[list[str], AsBulletList()]
    # Heading fields after:
    description: Annotated[str, AsHeading()]
    impact: Annotated[str, AsHeading()]


class SecurityAuditReport(MarkdownDocument):
    heading: Annotated[str, TextTemplate("{value}")]
    # Non-heading fields first:
    next_steps: Annotated[list[str], AsBulletList()]
    # Heading fields after:
    executive_summary: Annotated[str, AsHeading()]
    findings: list[Finding]


console.print(
    "\n[bold]Embedding a markdown format specification in an LLM system prompt[/bold]\n\n"
    "[dim]Step 1:[/dim] Declare a Pydantic model for the shape of a markdown document.\n"
    "[dim]Step 2:[/dim] Call [cyan]render_template()[/cyan] to produce a markdown skeleton.\n"
    "[dim]Step 3:[/dim] Embed that skeleton in a system prompt to define the markdown contract"
    " — the structure the LLM must produce or consume.\n"
)
console.input("[dim]Press Enter to see the model code that defines the markdown contract...[/dim]")

model_code = inspect.getsource(Finding) + "\n\n" + inspect.getsource(SecurityAuditReport)

console.print()
console.print(Rule("markdown contract"))
console.print(Syntax(model_code, "python", theme="monokai"))

# --- Generate the format spec ---

format_spec = render_template(SecurityAuditReport)

console.input("\n[dim]Press Enter to see the format spec embedded in a system prompt...[/dim]")

# --- How to embed it in a system prompt ---

system_prompt = f"""You are a security auditor. Analyse the code provided by the user
and produce a security audit report.

You MUST respond in the following markdown format exactly:

{format_spec}

Do not add any sections not listed above. Do not omit any sections."""

console.print()
console.print(Rule("system prompt with embedded contract"))
console.print(Syntax(system_prompt, "text", theme="monokai"))
