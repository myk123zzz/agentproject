"""Graph ontology — allowed entities and relationships."""

ALLOWED_ENTITIES: frozenset[str] = frozenset({
    "Tenant",
    "Document",
    "DocumentVersion",
    "Policy",
    "Clause",
    "Department",
    "Role",
    "Process",
    "ApprovalStep",
    "Requirement",
    "Form",
})

ALLOWED_RELATIONS: frozenset[str] = frozenset({
    "HAS_VERSION",
    "CONTAINS",
    "APPLIES_TO",
    "OWNED_BY",
    "REQUIRES",
    "APPROVED_BY",
    "NEXT_STEP",
    "REFERENCES",
    "SUPERSEDES",
    "CONFLICTS_WITH",
    "EXTRACTED_FROM",
})


def is_valid_entity(entity_type: str) -> bool:
    """Check if an entity type is in the ontology."""
    return entity_type in ALLOWED_ENTITIES


def is_valid_relation(relation_type: str) -> bool:
    """Check if a relation type is in the ontology."""
    return relation_type in ALLOWED_RELATIONS
