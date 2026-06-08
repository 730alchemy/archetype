# Examples

Run any example with `pdm run python examples/<script>`.

Each example is interactive — press Enter to step through the output.
<br><br>

| Script | Demonstrates | Why it's useful |
|--------|-------------|-----------------|
| `01_round_trip.py` | Render a model instance to markdown with `render_markdown()`, parse it back with `parse_markdown_as()`, assert the recovered instance is identical | Agent-to-agent handoffs are lossless — structured data written by one agent is fully recoverable by the next, with types intact |
| `02_compose_instruction.py` | Use `resolve()` to render a Jinja template that calls `template_fields()` for a prose section briefing and `generate_contract()` for the full contract | Instructions stay in sync with the model automatically — add a field and the briefing and contract both update without touching the prompt |
| `03_embed_format_spec.py` | Declare a model, call `generate_contract()`, embed the result in a system prompt with a plain f-string | The LLM sees the exact structure it must produce, so downstream parsing is reliable — not dependent on the model guessing the right format |
| `04_frontmatter.py` | Attach a `BaseModel` as `frontmatter` on a `MarkdownDocument`; show that `render_markdown()` emits a YAML block and `parse_markdown_as()` recovers it as a typed object | Metadata — document ID, status, provenance — travels with the document through the pipeline and arrives as a typed object, not a raw string to be parsed again |
| `05_tables.py` | Attach `AsTable()` to a `list[BaseModel]` field; each model instance becomes a row, each field a column; includes pipe character escaping | Structured lists in agent output — findings, test results, comparisons — arrive as validated model instances rather than text the consumer has to re-parse |
