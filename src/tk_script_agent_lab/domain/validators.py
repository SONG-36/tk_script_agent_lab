from collections import Counter
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from tk_script_agent_lab.domain.errors import (
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
)


ModelT = TypeVar("ModelT", bound=BaseModel)


def validate_reference_insights(
    golden_case: GoldenCase,
    insights: list[ReferenceInsight],
) -> None:
    _require_non_empty("ReferenceInsight output", insights)
    _require_instances("ReferenceInsight output", insights, ReferenceInsight)
    revalidated_insights = [
        _revalidate_model(
            f"ReferenceInsight({insight.insight_id})",
            insight,
            ReferenceInsight,
        )
        for insight in insights
    ]
    _require_unique_values(
        "ReferenceInsight.insight_id",
        [insight.insight_id for insight in revalidated_insights],
    )

    reference_ids = {video.reference_id for video in golden_case.reference_videos}
    for insight in revalidated_insights:
        _require_existing_id(
            "ReferenceInsight.reference_id",
            insight.reference_id,
            reference_ids,
        )


def validate_creative_ideas(
    golden_case: GoldenCase,
    insights: list[ReferenceInsight],
    ideas: list[CreativeIdea],
) -> None:
    _require_non_empty("CreativeIdea output", ideas)
    _require_instances("CreativeIdea output", ideas, CreativeIdea)
    revalidated_ideas = [
        _revalidate_model(
            f"CreativeIdea({idea.idea_id})",
            idea,
            CreativeIdea,
        )
        for idea in ideas
    ]
    _require_unique_values(
        "CreativeIdea.idea_id",
        [idea.idea_id for idea in revalidated_ideas],
    )

    selling_point_ids = {point.selling_point_id for point in golden_case.selling_points}
    insight_ids = {insight.insight_id for insight in insights}
    for idea in revalidated_ideas:
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


def validate_script_draft(
    golden_case: GoldenCase,
    insights: list[ReferenceInsight],
    ideas: list[CreativeIdea],
    script: ScriptDraft,
    selected_idea_id: str | None = None,
) -> None:
    if not isinstance(script, ScriptDraft):
        raise OutputSchemaError(
            "ScriptDraft provider output must contain ScriptDraft objects; "
            f"got {type(script).__name__}"
        )
    script = _revalidate_model(
        f"ScriptDraft({script.script_id})",
        script,
        ScriptDraft,
    )

    _require_non_empty("ScriptDraft.scenes", script.scenes)
    _require_non_empty("ScriptDraft.source_usages", script.source_usages)
    _require_unique_values(
        "ScriptScene.scene_id",
        [scene.scene_id for scene in script.scenes],
    )
    _require_unique_values(
        "ScriptDraft.source_usages.usage_id",
        [usage.usage_id for usage in script.source_usages],
    )

    reference_ids = {video.reference_id for video in golden_case.reference_videos}
    fact_ids = {fact.fact_id for fact in golden_case.product_facts}
    selling_point_ids = {point.selling_point_id for point in golden_case.selling_points}
    selling_points_by_id = {
        point.selling_point_id: point for point in golden_case.selling_points
    }
    insight_ids = {insight.insight_id for insight in insights}
    ideas_by_id = {idea.idea_id: idea for idea in ideas}
    idea_ids = set(ideas_by_id)

    for insight in insights:
        _require_existing_id(
            "ReferenceInsight.reference_id",
            insight.reference_id,
            reference_ids,
        )

    if script.product_version_id != golden_case.product_profile.product_version_id:
        raise OutputReferenceError(
            "ScriptDraft product_version_id must match Golden Case "
            f"product_version_id={golden_case.product_profile.product_version_id}; "
            f"got {script.product_version_id}"
        )
    _require_existing_id("ScriptDraft.creative_idea_id", script.creative_idea_id, idea_ids)
    if selected_idea_id is not None and script.creative_idea_id != selected_idea_id:
        raise OutputReferenceError(
            "ScriptDraft.creative_idea_id must match human selected idea; "
            f"selected_idea_id={selected_idea_id}; got {script.creative_idea_id}"
        )

    selected_idea = ideas_by_id[script.creative_idea_id]
    selected_selling_point_ids = set(selected_idea.selected_selling_point_ids)
    selected_insight_ids = set(selected_idea.source_insight_ids)

    scene_fact_ids = {
        fact_id for scene in script.scenes for fact_id in scene.fact_ids
    }
    scene_selling_point_ids = {
        selling_point_id
        for scene in script.scenes
        for selling_point_id in scene.selling_point_ids
    }

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

    for usage in script.source_usages:
        if usage.source_type == "product_fact" and usage.source_id not in scene_fact_ids:
            raise OutputReferenceError(
                "ScriptDraft.source_usages product_fact must appear in "
                f"ScriptScene.fact_ids; usage_id={usage.usage_id}; "
                f"source_id={usage.source_id}"
            )
        if (
            usage.source_type == "selling_point"
            and usage.source_id not in scene_selling_point_ids
        ):
            raise OutputReferenceError(
                "ScriptDraft.source_usages selling_point must appear in "
                f"ScriptScene.selling_point_ids; usage_id={usage.usage_id}; "
                f"source_id={usage.source_id}"
            )


def validate_output_fixture_set(
    output: OutputFixtureSet,
    golden_case: GoldenCase,
) -> None:
    validate_reference_insights(golden_case, output.reference_insights)
    validate_creative_ideas(
        golden_case,
        output.reference_insights,
        output.creative_ideas,
    )
    validate_script_draft(
        golden_case,
        output.reference_insights,
        output.creative_ideas,
        output.script_draft,
    )


def _validate_source_usage(
    usage,
    fact_ids: set[str],
    selling_point_ids: set[str],
    insight_ids: set[str],
) -> None:
    source_ids_by_type = {
        "product_fact": fact_ids,
        "selling_point": selling_point_ids,
        "reference_insight": insight_ids,
    }
    valid_source_ids = source_ids_by_type.get(usage.source_type)
    if valid_source_ids is None:
        raise OutputSchemaError(
            f"SourceUsage({usage.usage_id}) has unsupported "
            f"source_type={usage.source_type}"
        )
    if usage.source_id not in valid_source_ids:
        raise OutputReferenceError(
            f"SourceUsage({usage.usage_id}) source_type={usage.source_type} "
            f"does not match an existing source_id={usage.source_id}"
        )


def _revalidate_model(
    label: str,
    value: ModelT,
    model_type: type[ModelT],
) -> ModelT:
    try:
        return model_type.model_validate(
            value.model_dump(mode="python"),
            strict=True,
        )
    except ValidationError as exc:
        raise OutputSchemaError(
            f"{label} failed Pydantic schema revalidation: {exc}"
        ) from exc


def _require_existing_id(label: str, value: str, allowed_values: set[str]) -> None:
    if value not in allowed_values:
        raise OutputReferenceError(f"{label} references missing id={value}")


def _require_non_empty(label: str, values: list[object]) -> None:
    if not values:
        raise OutputValidationError(f"{label} must not be empty")


def _require_instances(label: str, values: list[object], expected_type: type) -> None:
    invalid_types = [
        type(value).__name__ for value in values if not isinstance(value, expected_type)
    ]
    if invalid_types:
        raise OutputSchemaError(
            f"{label} must contain {expected_type.__name__} objects; "
            f"invalid_types={invalid_types}"
        )


def _require_unique_values(label: str, values: list[str]) -> None:
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise OutputValidationError(
            f"{label} values must be unique; duplicates={duplicates}"
        )
