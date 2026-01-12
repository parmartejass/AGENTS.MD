"""Domain errors (SSOT) so failures are searchable and consistent."""


class MyAppError(Exception):
    """Base error for the application."""


class ConfigError(MyAppError):
    """Invalid configuration or scenario file."""


class ValidationError(MyAppError):
    """Input/config validation error."""


class WorkflowError(MyAppError):
    """Workflow selection or execution error."""


class FileIOError(MyAppError):
    """File I/O error with additional context."""

