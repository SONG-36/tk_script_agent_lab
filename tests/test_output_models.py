import pytest
from pydantic import ValidationError

from tk_script_agent_lab.domain import (
    CreativeIdea,
    ReferenceInsight,
    ScriptDraft,
    SourceUsage,
)


def test_output_models_reject_unknown_fields():
    with pytest.raises(ValidationError, match="extra"):
        ReferenceInsight.model_validate(
            {
                "insight_id": "ri_extra",
                "reference_id": "ref_001",
                "summary": "summary",
                "reusable_pattern": "pattern",
                "risk_notes": ["risk"],
                "unexpected": "not allowed",
            }
        )


def test_output_models_require_non_empty_text():
    with pytest.raises(ValidationError, match="hook"):
        CreativeIdea.model_validate(
            {
                "idea_id": "ci_blank",
                "title": "title",
                "angle": "angle",
                "hook": " ",
                "selected_selling_point_ids": ["sp_001"],
                "source_insight_ids": ["ri_001"],
                "risk_notes": ["risk"],
            }
        )


def test_source_usage_restricts_source_type():
    with pytest.raises(ValidationError, match="source_type"):
        SourceUsage.model_validate(
            {
                "usage_id": "su_bad",
                "source_type": "web_page",
                "source_id": "pf_001",
                "used_for": "not allowed",
            }
        )


def test_script_draft_requires_positive_durations():
    with pytest.raises(ValidationError, match="duration_seconds"):
        ScriptDraft.model_validate(
            {
                "script_id": "sd_bad",
                "product_version_id": "prod_car_vacuum_001_v1",
                "creative_idea_id": "ci_001",
                "language": "en-US",
                "target_duration_seconds": 24,
                "hook": "hook",
                "scenes": [
                    {
                        "scene_id": "scene_001",
                        "duration_seconds": 0,
                        "visual": "visual",
                        "voiceover": "voiceover",
                        "selling_point_ids": ["sp_001"],
                        "fact_ids": ["pf_001"],
                    }
                ],
                "cta": "cta",
                "source_usages": [
                    {
                        "usage_id": "su_001",
                        "source_type": "product_fact",
                        "source_id": "pf_001",
                        "used_for": "script support",
                    }
                ],
            }
        )
