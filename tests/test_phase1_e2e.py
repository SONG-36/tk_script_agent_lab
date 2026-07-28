import json
import random
import socket
import time
from pathlib import Path

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


def test_phase1_golden_case_end_to_end(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fail(*args, **kwargs):
        raise AssertionError("external boundary should not be used")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(random, "random", fail)
    monkeypatch.setattr(time, "time", fail)

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
    export_path = export_phase1_result(
        output_directory=tmp_path,
        golden_case=golden_case,
        options=options,
        selected_idea_id=selected_idea_id,
        script=script,
    )
    payload = json.loads(export_path.read_text(encoding="utf-8"))

    assert golden_case.product_profile.product_version_id == "prod_car_vacuum_001_v1"
    assert len(golden_case.product_facts) == 4
    assert len(golden_case.selling_points) == 3
    assert len(golden_case.reference_videos) == 3
    assert len(options.reference_insights) == 3
    assert len(options.creative_ideas) == 3
    assert selected_idea_id == "ci_001"
    assert script.script_id == "sd_001"
    assert script.creative_idea_id == "ci_001"
    assert len(script.scenes) == 3
    assert len(script.source_usages) == 4

    selected_idea = next(
        idea for idea in options.creative_ideas if idea.idea_id == selected_idea_id
    )
    selected_selling_point_ids = set(selected_idea.selected_selling_point_ids)
    selling_points_by_id = {
        point.selling_point_id: point for point in golden_case.selling_points
    }
    for scene in script.scenes:
        assert set(scene.selling_point_ids).issubset(selected_selling_point_ids)
        supported_fact_ids = {
            fact_id
            for selling_point_id in scene.selling_point_ids
            for fact_id in selling_points_by_id[selling_point_id].fact_ids
        }
        assert set(scene.fact_ids).issubset(supported_fact_ids)

    assert export_path.exists()
    assert payload["product_version_id"] == golden_case.product_profile.product_version_id
    assert payload["selected_idea_id"] == selected_idea_id
    assert payload["script_draft"]["script_id"] == script.script_id
    assert payload["script_draft"]["creative_idea_id"] == script.creative_idea_id
    assert payload["script_draft"] == script.model_dump(mode="json")
