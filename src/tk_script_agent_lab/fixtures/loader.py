import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tk_script_agent_lab.domain.errors import (
    OutputFixtureFileError,
    OutputFixtureJsonError,
    OutputFixturePathError,
    OutputReferenceError,
    OutputSchemaError,
    OutputValidationError,
)
from tk_script_agent_lab.domain.models import (
    CreativeIdea,
    GoldenCase,
    OutputFixtureSet,
    ReferenceInsight,
    ScriptDraft,
    SourceUsage,
)


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

    _validate_against_golden_case(output, golden_case)
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


def _validate_against_golden_case(
    output: OutputFixtureSet,
    golden_case: GoldenCase,
) -> None:
    reference_ids = {video.reference_id for video in golden_case.reference_videos}
    fact_ids = {fact.fact_id for fact in golden_case.product_facts}
    selling_point_ids = {point.selling_point_id for point in golden_case.selling_points}
    selling_points_by_id = {
        point.selling_point_id: point for point in golden_case.selling_points
    }
    insight_ids = {insight.insight_id for insight in output.reference_insights}
    ideas_by_id = {idea.idea_id: idea for idea in output.creative_ideas}
    idea_ids = set(ideas_by_id)

    for insight in output.reference_insights:
        _require_existing_id(
            "ReferenceInsight.reference_id",
            insight.reference_id,
            reference_ids,
        )

    for idea in output.creative_ideas:
        for selling_point_id in idea.selected_selling_point_ids:
            _require_existing_id(
                f"CreativeIdea({idea.idea_id}).selected_selling_point_ids",
                selling_point_id,
                selling_point_ids,
            )
        for insight_id in idea.source_insight_ids:
            _require_existing_id(
                f"CreativeIdea({idea.idea_id}).source_insight_ids",
                insight_id,
                insight_ids,
            )

    script = output.script_draft
    if script.product_version_id != golden_case.product_profile.product_version_id:
        raise OutputReferenceError(
            "ScriptDraft product_version_id must match Golden Case "
            f"product_version_id={golden_case.product_profile.product_version_id}; "
            f"got {script.product_version_id}"
        )
    _require_existing_id("ScriptDraft.creative_idea_id", script.creative_idea_id, idea_ids)
    selected_idea = ideas_by_id[script.creative_idea_id]
    selected_selling_point_ids = set(selected_idea.selected_selling_point_ids)
    selected_insight_ids = set(selected_idea.source_insight_ids)

    for usage in script.source_usages:
        _validate_source_usage(usage, fact_ids, selling_point_ids, insight_ids)
        if (
            usage.source_type == "reference_insight"
            and usage.source_id not in selected_insight_ids
        ):
            raise OutputReferenceError(
                "ScriptDraft.source_usages reference_insight must belong to selected "
                f"CreativeIdea({selected_idea.idea_id}); source_id={usage.source_id}"
            )

    for scene in script.scenes:
        for selling_point_id in scene.selling_point_ids:
            _require_existing_id(
                f"ScriptScene({scene.scene_id}).selling_point_ids",
                selling_point_id,
                selling_point_ids,
            )
            if selling_point_id not in selected_selling_point_ids:
                raise OutputReferenceError(
                    "ScriptScene selling_point_ids must belong to selected "
                    f"CreativeIdea({selected_idea.idea_id}); scene_id={scene.scene_id}; "
                    f"selling_point_id={selling_point_id}"
                )

        supported_fact_ids = {
            fact_id
            for selling_point_id in scene.selling_point_ids
            for fact_id in selling_points_by_id[selling_point_id].fact_ids
        }
        for fact_id in scene.fact_ids:
            _require_existing_id(
                f"ScriptScene({scene.scene_id}).fact_ids",
                fact_id,
                fact_ids,
            )
            if fact_id not in supported_fact_ids:
                raise OutputReferenceError(
                    "ScriptScene fact_ids must be supported by its selling_point_ids; "
                    f"scene_id={scene.scene_id}; fact_id={fact_id}; "
                    f"selling_point_ids={scene.selling_point_ids}"
                )


def _validate_source_usage(
    usage: SourceUsage,
    fact_ids: set[str],
    selling_point_ids: set[str],
    insight_ids: set[str],
) -> None:
    source_ids_by_type = {
        "product_fact": fact_ids,
        "selling_point": selling_point_ids,
        "reference_insight": insight_ids,
    }
    valid_source_ids = source_ids_by_type[usage.source_type]
    if usage.source_id not in valid_source_ids:
        raise OutputReferenceError(
            f"SourceUsage({usage.usage_id}) source_type={usage.source_type} "
            f"does not match an existing source_id={usage.source_id}"
        )


def _require_existing_id(label: str, value: str, allowed_values: set[str]) -> None:
    if value not in allowed_values:
        raise OutputReferenceError(f"{label} references missing id={value}")
