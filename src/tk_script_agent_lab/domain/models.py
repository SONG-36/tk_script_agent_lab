from collections import Counter
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from tk_script_agent_lab.domain.errors import GoldenCaseValidationError


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
        duplicates = sorted(
            value for value, count in Counter(values).items() if count > 1
        )
        if duplicates:
            raise GoldenCaseValidationError(
                f"{label} values must be unique; duplicates={duplicates}"
            )
