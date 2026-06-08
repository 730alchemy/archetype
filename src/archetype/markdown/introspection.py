"""Heading-field introspection for markdown template models.

``template_fields(ModelClass)`` returns metadata about the body heading
sections of a ``MarkdownHeader`` (or ``MarkdownDocument``) subclass — the
heading text each body field renders as, paired with the field's Pydantic
description.

Intended for consumption inside Jinja templates (via ``archetype.templating``)
or any other code that needs to enumerate a model's sections without walking
``model_fields`` directly:

    {% for field in template_fields(FeatureDefinition) %}
    - **{{ field.heading }}** — {{ field.description }}
    {% endfor %}

Supported field shapes:
  - ``Annotated[str, AsHeading()]`` — heading text is Title Case of field name.
  - Field typed as a ``MarkdownHeader`` subclass — heading text is the
    subclass's ``heading`` field default value.

Structural fields ``heading`` and ``frontmatter`` are skipped. Fields that do
not introduce headings are omitted.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_core import PydanticUndefined

from archetype.markdown._shared import get_role_annotation, snake_to_title
from archetype.markdown.annotations import AsHeading
from archetype.markdown.template_model import MarkdownHeader


@dataclass(frozen=True)
class FieldInfo:
    """Metadata for one heading-shaped body section of a template model.

    - ``heading``: the rendered heading text (without the ``#`` prefix).
    - ``description``: the field's Pydantic ``Field(description=...)``
      value, or ``None`` if the field has no description.
    """

    heading: str
    description: str | None


def template_fields(model_class: type[MarkdownHeader]) -> list[FieldInfo]:
    """Return per-section heading metadata for a ``MarkdownHeader`` subclass.

    Skips structural fields (``heading``, ``frontmatter``) and any body field
    that does not produce a heading (``AsCodeBlock``, ``AsBulletList``,
    ``AsNumberedList``, ``AsTable``, plain typed fields). Only
    ``Annotated[str, AsHeading()]`` fields and ``MarkdownHeader``-typed fields
    with a ``heading`` default are returned.
    """

    result: list[FieldInfo] = []
    for name, field in model_class.model_fields.items():
        if name in ("heading", "frontmatter"):
            continue

        heading = _resolve_heading(model_class, name, field)
        if heading is None:
            continue
        description = field.description
        result.append(FieldInfo(heading=heading, description=description))

    return result


def _resolve_heading(
    model_class: type[MarkdownHeader], field_name: str, field: object
) -> str | None:
    """Resolve heading text for one body field, or return None if the field
    produces no heading. Raises ValueError only when the field is typed as a
    MarkdownHeader subclass but no heading text can be derived."""

    annotation = get_role_annotation(field)

    # Shape 1: Annotated[str, AsHeading()] → Title Case of field name.
    if isinstance(annotation, AsHeading):
        return snake_to_title(field_name)

    # Shape 2: field typed as a MarkdownHeader subclass → subclass's heading default.
    field_type = getattr(field, "annotation", None)
    if isinstance(field_type, type) and issubclass(field_type, MarkdownHeader):
        heading_field = field_type.model_fields.get("heading")
        if heading_field is None or heading_field.default is PydanticUndefined:
            raise ValueError(
                f"{model_class.__name__}.{field_name} is typed as "
                f"{field_type.__name__}, which has no default value for its "
                f"`heading` field. template_fields() derives the heading from "
                f"the subclass's heading default; give {field_type.__name__}.heading "
                f'a default (e.g. `heading: str = "Section Name"`), or use '
                f"Annotated[str, AsHeading()] instead."
            )
        default = heading_field.default
        if not isinstance(default, str):
            raise ValueError(
                f"{model_class.__name__}.{field_name}: "
                f"{field_type.__name__}.heading default is {default!r}, "
                f"expected a string."
            )
        return default

    # Non-heading field shapes (AsCodeBlock, AsBulletList, etc.) produce no heading.
    return None
