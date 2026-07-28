import json
from pathlib import Path

from tk_script_agent_lab.domain.models import GoldenCase, ScriptDraft
from tk_script_agent_lab.domain.validators import (
    validate_creative_ideas,
    validate_reference_insights,
    validate_script_draft,
)
from tk_script_agent_lab.pipeline import CreativeOptions


def export_phase1_result(
    *,
    output_directory: Path,
    golden_case: GoldenCase,
    options: CreativeOptions,
    selected_idea_id: str,
    script: ScriptDraft,
) -> Path:
    validate_reference_insights(golden_case, options.reference_insights)
    validate_creative_ideas(
        golden_case,
        options.reference_insights,
        options.creative_ideas,
    )
    validate_script_draft(
        golden_case,
        options.reference_insights,
        options.creative_ideas,
        script,
        selected_idea_id=selected_idea_id,
    )

    payload = {
        "schema_version": "phase1_result_v1",
        "product_version_id": golden_case.product_profile.product_version_id,
        "selected_idea_id": selected_idea_id,
        "reference_insights": [
            item.model_dump(mode="json")
            for item in options.reference_insights
        ],
        "creative_ideas": [
            item.model_dump(mode="json")
            for item in options.creative_ideas
        ],
        "script_draft": script.model_dump(mode="json"),
    }

    output_path = Path(output_directory) / "phase1_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output_path
