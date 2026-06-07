"""Example: Composing a markdown contract into an agent instruction template.

resolve() renders a Jinja template against a context. Two globals are
available inside every template:

  - generate_contract(ModelClass)  — the markdown contract string
  - template_fields(ModelClass)  — per-section heading and description metadata

template_fields() only works on models whose body fields are all AsHeading
(or MarkdownHeader subclasses). It returns heading text and field description
for each section — useful for injecting semantic context into instructions.

This example shows two patterns:
  1. Embed the markdown contract via generate_contract.
  2. Inject per-section semantic context via template_fields on an all-heading model.
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
)
from archetype.templating import resolve

console = Console()


# Full model — defines the markdown contract.
# Non-heading fields (AsCodeBlock, AsBulletList) must precede heading fields (AsHeading).
class Finding(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    affected_code: Annotated[str, AsCodeBlock(language="python")]
    recommendations: Annotated[list[str], AsBulletList()]
    description: Annotated[str, AsHeading()]
    impact: Annotated[str, AsHeading()]


class SecurityAuditReport(MarkdownDocument):
    heading: Annotated[str, TextTemplate("{value}")]
    next_steps: Annotated[list[str], AsBulletList()]
    executive_summary: Annotated[str, AsHeading()]
    findings: list[Finding]


# Guidance model — all body fields are AsHeading so template_fields() can
# iterate them and inject per-section semantic context into instructions.
class FindingGuidance(MarkdownHeader):
    heading: str = "Finding"
    description: Annotated[str, AsHeading()] = Field(
        description="Clear explanation of the vulnerability and how it could be exploited."
    )
    impact: Annotated[str, AsHeading()] = Field(
        description="Rate as Critical, High, Medium, or Low. Explain the business impact."
    )


INSTRUCTION_TEMPLATE = """\
# Security Auditor

You are an expert security auditor specialising in Python application security.

## Your task

Analyse the code the user provides. Identify security vulnerabilities and produce
a structured audit report.

## Output format

Respond in the following markdown format exactly. Do not add or omit sections.

{{ generate_contract(Report) }}

## Field guidance

Pay close attention to the intent of each section:

{% for field in template_fields(Guidance) %}
**{{ field.heading }}** — {{ field.description }}
{% endfor %}

## Rules

- Report only genuine vulnerabilities — do not pad with low-confidence findings.
- Every finding must include affected code and at least two recommendations.
- Severity ratings must follow the scale defined in the Field guidance above.
"""

console.print(
    "\n[bold]Composing a markdown contract into an agent instruction template[/bold]\n\n"
    "[dim]Step 1:[/dim] Declare a Pydantic model that defines the markdown contract.\n"
    "[dim]Step 2:[/dim] Declare a guidance model — all [cyan]AsHeading[/cyan] fields — so"
    " [cyan]template_fields()[/cyan] can inject per-section semantic context.\n"
    "[dim]Step 3:[/dim] Write a Jinja template that embeds the markdown contract and the"
    " per-section guidance via [cyan]resolve()[/cyan].\n"
)
console.input("[dim]Press Enter to see the model code that defines the markdown contract...[/dim]")

contract_code = inspect.getsource(Finding) + "\n\n" + inspect.getsource(SecurityAuditReport)

console.print()
console.print(Rule("markdown contract"))
console.print(Syntax(contract_code, "python", theme="monokai"))

console.input("\n[dim]Press Enter to see the guidance model...[/dim]")

console.print()
console.print(Rule("guidance model"))
console.print(Syntax(inspect.getsource(FindingGuidance), "python", theme="monokai"))

console.input("\n[dim]Press Enter to see the Jinja instruction template...[/dim]")

console.print()
console.print(Rule("instruction template"))
console.print(Syntax(INSTRUCTION_TEMPLATE, "text", theme="monokai"))

console.input("\n[dim]Press Enter to see the resolved agent instructions...[/dim]")

instructions = resolve(
    INSTRUCTION_TEMPLATE,
    Report=SecurityAuditReport,
    Guidance=FindingGuidance,
)

console.print()
console.print(Rule("resolved agent instructions"))
console.print(Syntax(instructions, "text", theme="monokai"))
