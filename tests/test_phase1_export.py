import json
from pathlib import Path

import pytest

from tk_script_agent_lab.domain import OutputReferenceError
from tk_script_agent_lab.exporting import export_phase1_result
from tk_script_agent_lab.fixtures import load_output_fixtures
from tk_script_agent_lab.golden_case import load_golden_case
from tk_script_agent_lab.pipeline import generate_selected_script, prepare_creative_options
from tk_script_agent_lab.providers import (
    FakeCreativeIdeaProvider,
    FakeReferenceInsightProvider,
    FakeScriptDraftProvider,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"
FIXTURE_DIR = ROOT / "data" / "fixtures" / "car_vacuum_v1"


@pytest.fixture
def phase1_result_inputs():
    golden_case = load_golden_case(GOLDEN_CASE_DIR)
    fixtures = load_output_fixtures(FIXTURE_DIR, golden_case)
    options = prepare_creative_options(
        golden_case,
        FakeReferenceInsightProvider(fixtures),
        FakeCreativeIdeaProvider(fixtures),
    )
    selected_idea_id = "ci_001"
    script = generate_selected_script(
        golden_case,
        options,
        selected_idea_id,
        FakeScriptDraftProvider(fixtures),
    )
    return golden_case, options, selected_idea_id, script


def test_export_phase1_result_writes_valid_json(tmp_path, phase1_result_inputs):
    golden_case, options, selected_idea_id, script = phase1_result_inputs

    export_path = export_phase1_result(
        output_directory=tmp_path,
        golden_case=golden_case,
        options=options,
        selected_idea_id=selected_idea_id,
        script=script,
    )

    assert export_path.exists()
    assert export_path.name == "phase1_result.json"
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "phase1_result_v1"
    assert payload["product_version_id"] == "prod_car_vacuum_001_v1"
    assert payload["selected_idea_id"] == "ci_001"
    assert payload["script_draft"]["script_id"] == "sd_001"
    assert payload["script_draft"]["creative_idea_id"] == "ci_001"
    assert len(payload["reference_insights"]) == 3
    assert len(payload["creative_ideas"]) == 3
    assert len(payload["script_draft"]["scenes"]) == 3


def test_export_phase1_result_is_byte_deterministic(
    tmp_path,
    phase1_result_inputs,
):
    golden_case, options, selected_idea_id, script = phase1_result_inputs

    first_path = export_phase1_result(
        output_directory=tmp_path / "first",
        golden_case=golden_case,
        options=options,
        selected_idea_id=selected_idea_id,
        script=script,
    )
    second_path = export_phase1_result(
        output_directory=tmp_path / "second",
        golden_case=golden_case,
        options=options,
        selected_idea_id=selected_idea_id,
        script=script,
    )

    assert first_path.read_bytes() == second_path.read_bytes()


def test_export_phase1_result_rejects_mismatched_selection_before_write(
    tmp_path,
    phase1_result_inputs,
):
    golden_case, options, selected_idea_id, script = phase1_result_inputs
    assert selected_idea_id == "ci_001"

    with pytest.raises(OutputReferenceError, match="selected_idea_id=ci_002"):
        export_phase1_result(
            output_directory=tmp_path,
            golden_case=golden_case,
            options=options,
            selected_idea_id="ci_002",
            script=script,
        )

    assert not (tmp_path / "phase1_result.json").exists()
