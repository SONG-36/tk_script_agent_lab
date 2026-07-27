import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tk_script_agent_lab.domain.errors import (
    GoldenCaseFileError,
    GoldenCaseJsonError,
    GoldenCasePathError,
    GoldenCaseValidationError,
)
from tk_script_agent_lab.domain.models import (
    GoldenCase,
    ProductFact,
    ProductProfile,
    ReferenceVideo,
    SellingPoint,
)


REQUIRED_JSON_FILES = {
    "product_profile": "product_profile.json",
    "product_facts": "product_facts.json",
    "selling_points": "selling_points.json",
    "reference_videos": "reference_videos.json",
}


def load_golden_case(path: Path) -> GoldenCase:
    case_dir = Path(path)
    if not case_dir.exists():
        raise GoldenCasePathError(f"Golden Case directory does not exist: {case_dir}")
    if not case_dir.is_dir():
        raise GoldenCasePathError(f"Golden Case path is not a directory: {case_dir}")

    raw_profile = _read_json_file(case_dir / REQUIRED_JSON_FILES["product_profile"])
    raw_facts = _read_json_file(case_dir / REQUIRED_JSON_FILES["product_facts"])
    raw_points = _read_json_file(case_dir / REQUIRED_JSON_FILES["selling_points"])
    raw_references = _read_json_file(case_dir / REQUIRED_JSON_FILES["reference_videos"])

    _require_object("product_profile.json", raw_profile)
    _require_array("product_facts.json", raw_facts)
    _require_array("selling_points.json", raw_points)
    _require_array("reference_videos.json", raw_references)

    try:
        return GoldenCase(
            product_profile=ProductProfile.model_validate(raw_profile),
            product_facts=[ProductFact.model_validate(item) for item in raw_facts],
            selling_points=[SellingPoint.model_validate(item) for item in raw_points],
            reference_videos=[
                ReferenceVideo.model_validate(item) for item in raw_references
            ],
        )
    except ValidationError as exc:
        raise GoldenCaseValidationError(
            f"Golden Case field validation failed: {exc}"
        ) from exc


def _read_json_file(path: Path) -> Any:
    if not path.exists():
        raise GoldenCaseFileError(f"Required Golden Case file is missing: {path}")
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except UnicodeDecodeError as exc:
        raise GoldenCaseJsonError(
            f"Invalid text encoding in {path}: expected UTF-8 JSON"
        ) from exc
    except json.JSONDecodeError as exc:
        raise GoldenCaseJsonError(f"Invalid JSON in {path}: {exc.msg}") from exc
    except OSError as exc:
        raise GoldenCaseFileError(f"Could not read Golden Case file {path}: {exc}") from exc


def _require_object(file_name: str, value: Any) -> None:
    if not isinstance(value, dict):
        raise GoldenCaseValidationError(
            f"{file_name} root must be a JSON object, got {type(value).__name__}"
        )


def _require_array(file_name: str, value: Any) -> None:
    if not isinstance(value, list):
        raise GoldenCaseValidationError(
            f"{file_name} root must be a JSON array, got {type(value).__name__}"
        )
