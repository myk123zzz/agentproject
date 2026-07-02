"""Domain errors for PolicyMind."""


class PolicyMindError(Exception):
    """Base exception with code, HTTP status, and a public-safe message."""

    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    public_message: str = "An unexpected error occurred."


class InvalidDocument(PolicyMindError):
    code = "INVALID_DOCUMENT"
    status_code = 400
    public_message = "The document is invalid."


class DependencyUnavailable(PolicyMindError):
    code = "DEPENDENCY_UNAVAILABLE"
    status_code = 503
    public_message = "A required dependency is unavailable."


class AuthorizationDenied(PolicyMindError):
    code = "AUTHORIZATION_DENIED"
    status_code = 403
    public_message = "You do not have permission to perform this action."


class AuthenticationError(PolicyMindError):
    code = "AUTHENTICATION_ERROR"
    status_code = 401
    public_message = "Authentication failed."


class EmbeddingUnavailable(PolicyMindError):
    code = "EMBEDDING_UNAVAILABLE"
    status_code = 503
    public_message = "Embedding service is unavailable."


class ApprovalRequired(PolicyMindError):
    code = "APPROVAL_REQUIRED"
    status_code = 409
    public_message = "This action requires human approval."


class AgentBudgetExceeded(PolicyMindError):
    code = "AGENT_BUDGET_EXCEEDED"
    status_code = 422
    public_message = "Agent has exceeded its step or token budget."
