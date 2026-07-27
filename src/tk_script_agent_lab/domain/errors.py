class GoldenCaseError(Exception):
    """Base error for Golden Case loading and validation failures."""


class GoldenCasePathError(GoldenCaseError):
    """Raised when the Golden Case directory is missing or invalid."""


class GoldenCaseFileError(GoldenCaseError):
    """Raised when a required Golden Case file is missing."""


class GoldenCaseJsonError(GoldenCaseError):
    """Raised when a Golden Case JSON file cannot be decoded."""


class GoldenCaseValidationError(GoldenCaseError):
    """Raised when Golden Case data fails deterministic validation."""


class OutputFixtureError(Exception):
    """Base error for fixed output fixture loading and validation failures."""


class OutputFixturePathError(OutputFixtureError):
    """Raised when the output fixture directory is missing or invalid."""


class OutputFixtureFileError(OutputFixtureError):
    """Raised when a required output fixture file is missing or unreadable."""


class OutputFixtureJsonError(OutputFixtureError):
    """Raised when an output fixture JSON file cannot be decoded."""


class OutputValidationError(OutputFixtureError):
    """Base error for output fixture schema and deterministic validation failures."""


class OutputSchemaError(OutputValidationError):
    """Raised when output fixture data fails model or root-shape validation."""


class OutputReferenceError(OutputValidationError):
    """Raised when output fixture data references missing or mismatched IDs."""
