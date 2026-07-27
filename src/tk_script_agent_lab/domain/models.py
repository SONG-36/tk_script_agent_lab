from collections import Counter
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from tk_script_agent_lab.domain.errors import (
    GoldenCaseValidationError,
    OutputValidationError,
)


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ExtraForbidModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProductProfile(ExtraForbidModel):
    product_id: NonEmptyString
    product_version_id: NonEmptyString
    product_name: NonEmptyString
    category: NonEmptyString
    target_market: NonEmptyString
    target_audience: list[NonEmptyString] = Field(min_length=1)
    primary_use_scenarios: list[NonEmptyString] = Field(min_length=1)
    tone_preferences: list[NonEmptyString] = Field(min_length=1)
    prohibited_claims: list[NonEmptyString] = Field(min_length=1)
    notes: NonEmptyString


class ProductFact(ExtraForbidModel):
    fact_id: NonEmptyString
    product_version_id: NonEmptyString
    fact_type: NonEmptyString
    fact_text: NonEmptyString
    evidence_source: NonEmptyString
    confidence: NonEmptyString
    allowed_usage: list[NonEmptyString] = Field(min_length=1)
    risk_notes: list[NonEmptyString]


class SellingPoint(ExtraForbidModel):
    selling_point_id: NonEmptyString
    title: NonEmptyString
    description: NonEmptyString
    fact_ids: list[NonEmptyString] = Field(min_length=1)
    target_pain_point: NonEmptyString
    target_audience: list[NonEmptyString] = Field(min_length=1)
    allowed_expressions: list[NonEmptyString] = Field(min_length=1)
    prohibited_expressions: list[NonEmptyString] = Field(min_length=1)
    risk_notes: list[NonEmptyString]


class ReferenceVideo(ExtraForbidModel):
    reference_id: NonEmptyString
    platform: NonEmptyString
    url: NonEmptyString
    title: NonEmptyString
    creator_or_source: NonEmptyString
    manual_summary: NonEmptyString
    borrowable_patterns: list[NonEmptyString] = Field(min_length=1)
    do_not_copy: list[NonEmptyString] = Field(min_length=1)
    risk_notes: list[NonEmptyString]


class ReferenceInsight(ExtraForbidModel):
    insight_id: NonEmptyString
    reference_id: NonEmptyString
    summary: NonEmptyString
    reusable_pattern: NonEmptyString
    risk_notes: list[NonEmptyString] = Field(min_length=1)


class CreativeIdea(ExtraForbidModel):
    idea_id: NonEmptyString
    title: NonEmptyString
    angle: NonEmptyString
    hook: NonEmptyString
    selected_selling_point_ids: list[NonEmptyString] = Field(min_length=1)
    source_insight_ids: list[NonEmptyString] = Field(min_length=1)
    risk_notes: list[NonEmptyString] = Field(min_length=1)


SourceType = Literal["product_fact", "selling_point", "reference_insight"]


class SourceUsage(ExtraForbidModel):
    usage_id: NonEmptyString
    source_type: SourceType
    source_id: NonEmptyString
    used_for: NonEmptyString


class ScriptScene(ExtraForbidModel):
    scene_id: NonEmptyString
    duration_seconds: int = Field(gt=0)
    visual: NonEmptyString
    voiceover: NonEmptyString
    selling_point_ids: list[NonEmptyString] = Field(min_length=1)
    fact_ids: list[NonEmptyString] = Field(min_length=1)


class ScriptDraft(ExtraForbidModel):
    script_id: NonEmptyString
    product_version_id: NonEmptyString
    creative_idea_id: NonEmptyString
    language: NonEmptyString
    target_duration_seconds: int = Field(gt=0)
    hook: NonEmptyString
    scenes: list[ScriptScene] = Field(min_length=1)
    cta: NonEmptyString
    source_usages: list[SourceUsage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_script_ids(self) -> "ScriptDraft":
        _require_unique_values(
            "ScriptScene.scene_id",
            [scene.scene_id for scene in self.scenes],
            OutputValidationError,
        )
        _require_unique_values(
            "ScriptDraft.source_usages.usage_id",
            [usage.usage_id for usage in self.source_usages],
            OutputValidationError,
        )
        return self


class OutputFixtureSet(ExtraForbidModel):
    reference_insights: list[ReferenceInsight] = Field(min_length=1)
    creative_ideas: list[CreativeIdea] = Field(min_length=1)
    script_draft: ScriptDraft

    @model_validator(mode="after")
    def validate_output_ids(self) -> "OutputFixtureSet":
        _require_unique_values(
            "ReferenceInsight.insight_id",
            [insight.insight_id for insight in self.reference_insights],
            OutputValidationError,
        )
        _require_unique_values(
            "CreativeIdea.idea_id",
            [idea.idea_id for idea in self.creative_ideas],
            OutputValidationError,
        )
        return self


class GoldenCase(ExtraForbidModel):
    product_profile: ProductProfile
    product_facts: list[ProductFact] = Field(min_length=1)
    selling_points: list[SellingPoint] = Field(min_length=1)
    reference_videos: list[ReferenceVideo] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_cross_references(self) -> "GoldenCase":
        self._require_unique(
            "ProductFact.fact_id",
            [fact.fact_id for fact in self.product_facts],
        )
        self._require_unique(
            "SellingPoint.selling_point_id",
            [point.selling_point_id for point in self.selling_points],
        )
        self._require_unique(
            "ReferenceVideo.reference_id",
            [video.reference_id for video in self.reference_videos],
        )

        expected_version_id = self.product_profile.product_version_id
        mismatched_fact_ids = [
            fact.fact_id
            for fact in self.product_facts
            if fact.product_version_id != expected_version_id
        ]
        if mismatched_fact_ids:
            raise GoldenCaseValidationError(
                "ProductFact product_version_id must match ProductProfile "
                f"product_version_id={expected_version_id}; mismatched fact_ids="
                f"{mismatched_fact_ids}"
            )

        existing_fact_ids = {fact.fact_id for fact in self.product_facts}
        missing_fact_refs = {
            fact_id
            for point in self.selling_points
            for fact_id in point.fact_ids
            if fact_id not in existing_fact_ids
        }
        if missing_fact_refs:
            raise GoldenCaseValidationError(
                "SellingPoint fact_ids must reference existing ProductFact ids; "
                f"missing fact_ids={sorted(missing_fact_refs)}"
            )

        return self

    @property
    def is_placeholder(self) -> bool:
        profile_note = self.product_profile.notes.lower()
        has_template_note = "template case" in profile_note or "placeholder" in profile_note
        has_placeholder_references = any(
            video.url.startswith("https://example.com/")
            or video.creator_or_source == "manual_placeholder"
            for video in self.reference_videos
        )
        return has_template_note or has_placeholder_references

    def require_production_ready(self) -> None:
        if self.is_placeholder:
            raise GoldenCaseValidationError(
                "Golden Case contains placeholder/template data and must not be "
                "treated as production-ready product data."
            )

    @staticmethod
    def _require_unique(label: str, values: list[str]) -> None:
        _require_unique_values(label, values, GoldenCaseValidationError)


def _require_unique_values(
    label: str,
    values: list[str],
    error_type: type[Exception],
) -> None:
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise error_type(f"{label} values must be unique; duplicates={duplicates}")
