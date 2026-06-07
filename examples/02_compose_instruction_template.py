"""Example: Composing a markdown contract into an agent instruction template.

resolve() renders a Jinja template against a context. Two globals are
available inside every template:

  - generate_contract(ModelClass)  — the markdown contract string
  - template_fields(ModelClass)    — heading and description for each section

template_fields() skips non-heading fields (AsCodeBlock, AsBulletList, etc.)
and returns only the fields that produce headings in the rendered document.
This means you can pass the real contract model directly — no separate
guidance model needed.

This example shows two patterns used together:
  1. Embed the markdown contract via generate_contract.
  2. Inject a prose section briefing via template_fields on the same model.
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


class Finding(MarkdownHeader):
    heading: Annotated[str, TextTemplate("Finding {ordinal} — {value}")]
    affected_code: Annotated[str, AsCodeBlock(language="python")] = Field(
        description="The vulnerable code snippet."
    )
    recommendations: Annotated[list[str], AsBulletList()] = Field(
        description="Concrete remediation steps. Include at least two."
    )
    description: Annotated[str, AsHeading()] = Field(
        description="Clear explanation of the vulnerability and how it could be exploited."
    )
    impact: Annotated[str, AsHeading()] = Field(
        description="Rate as Critical, High, Medium, or Low. Explain the business impact."
    )


class SecurityAuditReport(MarkdownDocument):
    heading: Annotated[str, TextTemplate("{value}")]
    next_steps: Annotated[list[str], AsBulletList()] = Field(
        description="Prioritised list of actions for the engineering team."
    )
    executive_summary: Annotated[str, AsHeading()] = Field(
        description="One paragraph suitable for a non-technical audience."
    )
    findings: list[Finding]


INSTRUCTION_TEMPLATE = """\
# Security Auditor

You are an expert security auditor specialising in Python application security.

## Your task

Analyse the code the user provides. Identify security vulnerabilities and produce
a structured audit report.

## Section guidance

Pay close attention to the intent of each section of a finding:

{% for field in template_fields(Finding) %}
**{{ field.heading }}** — {{ field.description }}
{% endfor %}

## Output format

Respond in the following markdown contract exactly. Do not add or omit sections.

{{ generate_contract(Report) }}
"""

console.print(
    "\n[bold]Composing a markdown contract into an agent instruction template[/bold]\n\n"
    "[dim]Step 1:[/dim] Declare a Pydantic model that defines the markdown contract.\n"
    "[dim]Step 2:[/dim] Write a Jinja template that embeds both a prose section briefing"
    " via [cyan]template_fields()[/cyan] and the contract via [cyan]generate_contract()[/cyan].\n"
    "[dim]Step 3:[/dim] Call [cyan]resolve()[/cyan] to produce the final instruction string.\n"
)
console.input("[dim]Press Enter to see the model code that defines the markdown contract...[/dim]")

contract_code = inspect.getsource(Finding) + "\n\n" + inspect.getsource(SecurityAuditReport)

console.print()
console.print(Rule("markdown contract"))
console.print(Syntax(contract_code, "python", theme="monokai"))

console.input("\n[dim]Press Enter to see the Jinja instruction template...[/dim]")

console.print()
console.print(Rule("instruction template"))
console.print(Syntax(INSTRUCTION_TEMPLATE, "text", theme="monokai"))

console.input("\n[dim]Press Enter to see the resolved agent instructions...[/dim]")

instructions = resolve(
    INSTRUCTION_TEMPLATE,
    Finding=Finding,
    Report=SecurityAuditReport,
)

console.print()
console.print(Rule("resolved agent instructions"))
console.print(Syntax(instructions, "text", theme="monokai"))
