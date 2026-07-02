"""Graph extraction — LLM-based entity/relation extraction with validation."""

import json
import re
from typing import Any

from pydantic import BaseModel, ValidationError

from policymind.graph.ontology import is_valid_entity, is_valid_relation


class ExtractedEntity(BaseModel):
    name: str
    type: str
    tenant_id: int = 1
    confidence: float = 0.5
    source_document_version_id: int | None = None


class ExtractedRelation(BaseModel):
    source: str
    target: str
    type: str
    tenant_id: int = 1
    confidence: float = 0.5
    source_document_version_id: int | None = None


class GraphExtraction(BaseModel):
    entities: list[ExtractedEntity] = []
    relations: list[ExtractedRelation] = []


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first valid JSON object from text (regex-based).

    Priority: Markdown ```json code block → plain JSON → balanced brace scan.
    """
    # Try Markdown code block
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return dict(json.loads(m.group(1)))

    # Try plain JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return dict(json.loads(m.group(0)))

    raise ValueError("No JSON object found in text")


async def parse_llm_json(
    text: str,
    schema: type[BaseModel],
    repair: Any = None,
) -> BaseModel:
    """Extract JSON → parse → Pydantic validate; one format-fix retry."""
    try:
        raw = extract_json_object(text)
        return schema.model_validate(raw)
    except (ValueError, ValidationError) as e:
        if repair:
            repaired_text = await repair(str(e), text)
            raw = extract_json_object(repaired_text)
            return schema.model_validate(raw)
        raise


class GraphExtractor:
    """Extract entities and relations from chunks, validating against ontology."""

    def validate_extraction(self, extraction: GraphExtraction) -> GraphExtraction:
        """Filter out invalid entities/relations not in the ontology."""
        valid_entities = [
            e for e in extraction.entities if is_valid_entity(e.type)
        ]
        valid_relations = [
            r for r in extraction.relations
            if is_valid_relation(r.type)
            and any(e.name == r.source for e in valid_entities)
            and any(e.name == r.target for e in valid_entities)
        ]
        return GraphExtraction(entities=valid_entities, relations=valid_relations)

    async def extract(self, text: str, source_version_id: int) -> GraphExtraction:
        """Simulate extraction — in production, calls an LLM with a prompt."""
        # Stub extraction for now — real LLM call in Task 7
        extraction = GraphExtraction(
            entities=[],
            relations=[],
        )
        return self.validate_extraction(extraction)
