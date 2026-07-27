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
