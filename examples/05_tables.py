r"""Example: Markdown tables backed by typed Pydantic row models.

Attach AsTable() to a list of BaseModel instances to render structured data as
a markdown table. Each row model field becomes a column, and each model
instance becomes a row. Literal pipe characters in cell values are escaped in
the markdown output and restored when parsed back into the Pydantic model.

This example does not call an LLM.
"""

import inspect
from typing import Annotated

from pydantic import BaseModel, Field
from rich.console import Console
from rich.rule import Rule
from rich.syntax import Syntax

from archetype.markdown import AsTable, MarkdownHeader, parse_markdown_as, render_markdown

console = Console()


class Component(BaseModel):
    name: str = Field(description="Component name.")
    owner: str = Field(description="Team responsible for the component.")
    status: str = Field(description="Current operational status.")


class ServiceInventory(MarkdownHeader):
    components: Annotated[list[Component], AsTable()] = Field(
        description="One row per deployed component."
    )


console.print(
    "\n[bold]Markdown tables — typed rows rendered from Pydantic models[/bold]\n\n"
    "[dim]Step 1:[/dim] Define a [cyan]BaseModel[/cyan] for one table row. Each field"
    " becomes a column.\n"
    "[dim]Step 2:[/dim] Declare [cyan]list[Component][/cyan] with"
    " [cyan]AsTable()[/cyan] on a [cyan]MarkdownHeader[/cyan].\n"
    "[dim]Step 3:[/dim] Create a Pydantic model instance containing table rows.\n"
    "[dim]Step 4:[/dim] Call [cyan]render_markdown()[/cyan] to produce a markdown table.\n"
    "[dim]Step 5:[/dim] Call [cyan]parse_markdown_as()[/cyan] to recover the typed rows.\n"
)
console.input("[dim]Press Enter to see the model...[/dim]")

console.print()
console.print(Rule("model"))
console.print(
    Syntax(
        inspect.getsource(Component) + "\n\n" + inspect.getsource(ServiceInventory),
        "python",
        theme="monokai",
    )
)

console.input("\n[dim]Press Enter to see the Pydantic model instance...[/dim]")

inventory = ServiceInventory(
    heading="Production Service Inventory",
    components=[
        Component(name="api|worker", owner="Platform", status="healthy"),
        Component(name="billing", owner="Payments", status="degraded"),
    ],
)

console.print()
console.print(Rule("Pydantic model instance"))
display_json = inventory.model_dump_json(indent=2).replace(
    '"name": "api|worker",',
    '"name": "api|worker",  // Archetype handles literal pipe characters.',
)
console.print(Syntax(display_json, "jsonc", theme="monokai"))

console.input("\n[dim]Press Enter to see the rendered markdown table...[/dim]")

rendered = render_markdown(inventory)

console.print()
console.print(Rule("rendered markdown"))
console.print(Syntax(rendered, "text", theme="monokai"))

console.input(
    "[dim]Press Enter to parse the markdown back into typed table rows and verify"
    " round-trip...[/dim]"
)

recovered = parse_markdown_as(rendered, ServiceInventory)

assert recovered == inventory, "Round-trip failed — instances are not equal."

console.print()
console.print(Rule("result"))
console.print(
    Syntax(
        "# inventory is the Pydantic model instance we created in step 3\n"
        "rendered = render_markdown(inventory)\n"
        "\n"
        "recovered = parse_markdown_as(rendered, ServiceInventory)\n"
        "\n"
        "recovered.components[0].name  # 'api|worker'\n"
        "recovered == inventory",
        "python",
        theme="monokai",
    )
)
console.print(
    "\n[green]✓[/green] [bold]True[/bold] — table rows parsed back into typed Pydantic"
    " models, including the literal pipe character.\n"
)
