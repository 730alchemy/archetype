"""Example: Embedding a markdown contract in an LLM system prompt.

Declare a Pydantic model that defines the markdown contract. Call
generate_contract() to produce the contract string. Embed it in a system
prompt so the LLM knows exactly what structure to produce or consume.

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
    AsCodeBlock,
    AsHeading,
    MarkdownDocument,
    MarkdownHeader,
    TextTemplate,
    generate_contract,
)

console = Console()


class Finding(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    # Non-heading fields first:
    affected_code: Annotated[str, AsCodeBlock(language="python")] = Field(
        description="The vulnerable code snippet."
    )
    recommendations: Annotated[list[str], AsBulletList()] = Field(
        description="Concrete remediation steps. Include at least two."
    )
    # Heading fields after:
    description: Annotated[str, AsHeading()] = Field(
        description="Clear explanation of the vulnerability and how it could be exploited."
    )
    impact: Annotated[str, AsHeading()] = Field(
        description="Rate as Critical, High, Medium, or Low. Explain the business impact."
    )


class SecurityAuditReport(MarkdownDocument):
    heading: Annotated[str, TextTemplate("{value}")]
    # Non-heading fields first:
    next_steps: Annotated[list[str], AsBulletList()] = Field(
        description="Prioritised list of actions for the engineering team."
    )
    # Heading fields after:
    executive_summary: Annotated[str, AsHeading()] = Field(
        description="One paragraph suitable for a non-technical audience."
    )
    findings: list[Finding]


console.print(
    "\n[bold]Embedding a markdown contract in an LLM system prompt[/bold]\n\n"
    "[dim]Step 1:[/dim] Declare a Pydantic model that defines the markdown contract.\n"
    "[dim]Step 2:[/dim] Call [cyan]generate_contract()[/cyan] to produce the contract string.\n"
    "[dim]Step 3:[/dim] Embed the contract in a system prompt — the LLM must produce or consume"
    " exactly that structure.\n"
)
console.input("[dim]Press Enter to see the model code that defines the markdown contract...[/dim]")

model_code = inspect.getsource(Finding) + "\n\n" + inspect.getsource(SecurityAuditReport)

console.print()
console.print(Rule("markdown contract"))
console.print(Syntax(model_code, "python", theme="monokai"))

# --- Generate the contract ---

contract = generate_contract(SecurityAuditReport)

console.input("\n[dim]Press Enter to see the contract embedded in a system prompt...[/dim]")

# --- How to embed it in a system prompt ---

system_prompt = f"""You are a security auditor. Analyse the code provided by the user
and produce a security audit report.

You MUST follow this markdown contract exactly:

{contract}

Do not add any sections not listed above. Do not omit any sections."""

console.print()
console.print(Rule("system prompt with embedded contract"))
console.print(Syntax(system_prompt, "text", theme="monokai"))
