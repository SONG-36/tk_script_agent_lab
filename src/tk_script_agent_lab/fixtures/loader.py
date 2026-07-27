import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tk_script_agent_lab.domain.errors import (
    OutputFixtureFileError,
    OutputFixtureJsonError,
    OutputFixturePathError,
    OutputSchemaError,
    OutputValidationError,
)
from tk_script_agent_lab.domain.models import (
    CreativeIdea,
    GoldenCase,
    OutputFixtureSet,
    ReferenceInsight,
    ScriptDraft,
)
from tk_script_agent_lab.domain.validators import validate_output_fixture_set


REQUIRED_OUTPUT_FIXTURE_FILES = {
    "reference_insights": "reference_insights.json",
    "creative_ideas": "creative_ideas.json",
    "script_draft": "script_draft.json",
}


def load_output_fixtures(
    fixture_dir: Path,
    golden_case: GoldenCase,
) -> OutputFixtureSet:
    path = Path(fixture_dir)
    if not path.exists():
        raise OutputFixturePathError(f"Output fixture directory does not exist: {path}")
    if not path.is_dir():
        raise OutputFixturePathError(f"Output fixture path is not a directory: {path}")

    raw_insights = _read_json_file(
        path / REQUIRED_OUTPUT_FIXTURE_FILES["reference_insights"]
    )
    raw_ideas = _read_json_file(path / REQUIRED_OUTPUT_FIXTURE_FILES["creative_ideas"])
    raw_script = _read_json_file(path / REQUIRED_OUTPUT_FIXTURE_FILES["script_draft"])

    _require_array("reference_insights.json", raw_insights)
    _require_array("creative_ideas.json", raw_ideas)
    _require_object("script_draft.json", raw_script)

    try:
        output = OutputFixtureSet(
            reference_insights=[
                ReferenceInsight.model_validate(item) for item in raw_insights
            ],
            creative_ideas=[CreativeIdea.model_validate(item) for item in raw_ideas],
            script_draft=ScriptDraft.model_validate(raw_script),
        )
    except ValidationError as exc:
        raise OutputSchemaError(f"Output fixture field validation failed: {exc}") from exc
    except OutputValidationError:
        raise

    validate_output_fixture_set(output, golden_case)
    return output


def _read_json_file(path: Path) -> Any:
    if not path.exists():
        raise OutputFixtureFileError(f"Required output fixture file is missing: {path}")
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except UnicodeDecodeError as exc:
        raise OutputFixtureJsonError(
            f"Invalid text encoding in {path}: expected UTF-8 JSON"
        ) from exc
    except json.JSONDecodeError as exc:
        raise OutputFixtureJsonError(f"Invalid JSON in {path}: {exc.msg}") from exc
    except OSError as exc:
        raise OutputFixtureFileError(
            f"Could not read output fixture file {path}: {exc}"
        ) from exc


def _require_object(file_name: str, value: Any) -> None:
    if not isinstance(value, dict):
        raise OutputSchemaError(
            f"{file_name} root must be a JSON object, got {type(value).__name__}"
        )


def _require_array(file_name: str, value: Any) -> None:
    if not isinstance(value, list):
        raise OutputSchemaError(
            f"{file_name} root must be a JSON array, got {type(value).__name__}"
        )
