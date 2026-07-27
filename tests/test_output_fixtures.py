import json
import shutil
from pathlib import Path

import pytest

from tk_script_agent_lab.domain import (
    OutputFixtureSet,
    OutputFixtureFileError,
    OutputFixtureJsonError,
    OutputFixturePathError,
    OutputReferenceError,
    OutputSchemaError,
    OutputValidationError,
    ScriptDraft,
)
from tk_script_agent_lab.fixtures import load_output_fixtures
from tk_script_agent_lab.golden_case import load_golden_case


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"
FIXTURE_DIR = ROOT / "data" / "fixtures" / "car_vacuum_v1"


@pytest.fixture
def golden_case():
    return load_golden_case(GOLDEN_CASE_DIR)


def copy_fixture(tmp_path: Path) -> Path:
    fixture_dir = tmp_path / "car_vacuum_v1"
    shutil.copytree(FIXTURE_DIR, fixture_dir)
    return fixture_dir


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def test_loads_output_fixtures_as_models(golden_case):
    output = load_output_fixtures(FIXTURE_DIR, golden_case)

    assert isinstance(output, OutputFixtureSet)
    assert isinstance(output.script_draft, ScriptDraft)
    assert len(output.reference_insights) == 3
    assert len(output.creative_ideas) == 3
    assert len(output.script_draft.source_usages) == 4
    assert output.script_draft.script_id == "sd_001"
    assert output.script_draft.creative_idea_id == "ci_001"


def test_output_fixture_references_are_valid(golden_case):
    output = load_output_fixtures(FIXTURE_DIR, golden_case)
    reference_ids = {video.reference_id for video in golden_case.reference_videos}
    selling_point_ids = {point.selling_point_id for point in golden_case.selling_points}
    fact_ids = {fact.fact_id for fact in golden_case.product_facts}
    insight_ids = {insight.insight_id for insight in output.reference_insights}
    idea_ids = {idea.idea_id for idea in output.creative_ideas}

    assert {insight.reference_id for insight in output.reference_insights}.issubset(
        reference_ids
    )
    assert {
        selling_point_id
        for idea in output.creative_ideas
        for selling_point_id in idea.selected_selling_point_ids
    }.issubset(selling_point_ids)
    assert {
        insight_id
        for idea in output.creative_ideas
        for insight_id in idea.source_insight_ids
    }.issubset(insight_ids)
    assert output.script_draft.creative_idea_id in idea_ids
    assert {
        fact_id
        for scene in output.script_draft.scenes
        for fact_id in scene.fact_ids
    }.issubset(fact_ids)


def test_output_fixture_load_is_deterministic(golden_case):
    first = load_output_fixtures(FIXTURE_DIR, golden_case)
    second = load_output_fixtures(FIXTURE_DIR, golden_case)

    assert first.model_dump() == second.model_dump()


def test_reference_insight_duplicate_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "reference_insights.json"
    insights = read_json(path)
    insights[1]["insight_id"] = insights[0]["insight_id"]
    write_json(path, insights)

    with pytest.raises(OutputValidationError, match="ReferenceInsight.insight_id"):
        load_output_fixtures(fixture_dir, golden_case)


def test_reference_insight_missing_reference_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "reference_insights.json"
    insights = read_json(path)
    insights[0]["reference_id"] = "ref_missing"
    write_json(path, insights)

    with pytest.raises(OutputReferenceError, match="ref_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_reference_insight_empty_summary_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "reference_insights.json"
    insights = read_json(path)
    insights[0]["summary"] = " "
    write_json(path, insights)

    with pytest.raises(OutputSchemaError, match="summary"):
        load_output_fixtures(fixture_dir, golden_case)


def test_reference_insight_unknown_field_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "reference_insights.json"
    insights = read_json(path)
    insights[0]["unknown"] = "not allowed"
    write_json(path, insights)

    with pytest.raises(OutputSchemaError, match="unknown"):
        load_output_fixtures(fixture_dir, golden_case)


def test_creative_idea_duplicate_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "creative_ideas.json"
    ideas = read_json(path)
    ideas[1]["idea_id"] = ideas[0]["idea_id"]
    write_json(path, ideas)

    with pytest.raises(OutputValidationError, match="CreativeIdea.idea_id"):
        load_output_fixtures(fixture_dir, golden_case)


def test_creative_idea_missing_selling_point_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "creative_ideas.json"
    ideas = read_json(path)
    ideas[0]["selected_selling_point_ids"] = ["sp_missing"]
    write_json(path, ideas)

    with pytest.raises(OutputReferenceError, match="sp_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_creative_idea_missing_insight_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "creative_ideas.json"
    ideas = read_json(path)
    ideas[0]["source_insight_ids"] = ["ri_missing"]
    write_json(path, ideas)

    with pytest.raises(OutputReferenceError, match="ri_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_creative_idea_empty_hook_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "creative_ideas.json"
    ideas = read_json(path)
    ideas[0]["hook"] = ""
    write_json(path, ideas)

    with pytest.raises(OutputSchemaError, match="hook"):
        load_output_fixtures(fixture_dir, golden_case)


def test_creative_idea_empty_selling_points_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "creative_ideas.json"
    ideas = read_json(path)
    ideas[0]["selected_selling_point_ids"] = []
    write_json(path, ideas)

    with pytest.raises(OutputSchemaError, match="selected_selling_point_ids"):
        load_output_fixtures(fixture_dir, golden_case)


def test_source_usage_duplicate_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["source_usages"][1]["usage_id"] = script["source_usages"][0]["usage_id"]
    write_json(path, script)

    with pytest.raises(OutputValidationError, match="ScriptDraft.source_usages.usage_id"):
        load_output_fixtures(fixture_dir, golden_case)


def test_source_usage_invalid_source_type_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["source_usages"][0]["source_type"] = "web_page"
    write_json(path, script)

    with pytest.raises(OutputSchemaError, match="source_type"):
        load_output_fixtures(fixture_dir, golden_case)


def test_source_usage_type_mismatch_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["source_usages"][0]["source_type"] = "selling_point"
    script["source_usages"][0]["source_id"] = "pf_001"
    write_json(path, script)

    with pytest.raises(OutputReferenceError, match="source_type=selling_point"):
        load_output_fixtures(fixture_dir, golden_case)


def test_source_usage_missing_source_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["source_usages"][0]["source_id"] = "pf_missing"
    write_json(path, script)

    with pytest.raises(OutputReferenceError, match="pf_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_product_version_mismatch_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["product_version_id"] = "other_version"
    write_json(path, script)

    with pytest.raises(OutputReferenceError, match="product_version_id"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_missing_creative_idea_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["creative_idea_id"] = "ci_missing"
    write_json(path, script)

    with pytest.raises(OutputReferenceError, match="ci_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_duplicate_scene_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["scenes"][1]["scene_id"] = script["scenes"][0]["scene_id"]
    write_json(path, script)

    with pytest.raises(OutputValidationError, match="ScriptScene.scene_id"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_scene_duration_must_be_positive(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["scenes"][0]["duration_seconds"] = 0
    write_json(path, script)

    with pytest.raises(OutputSchemaError, match="duration_seconds"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_missing_selling_point_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["scenes"][0]["selling_point_ids"] = ["sp_missing"]
    write_json(path, script)

    with pytest.raises(OutputReferenceError, match="sp_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_scene_selling_point_must_belong_to_selected_idea(
    tmp_path,
    golden_case,
):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["scenes"][0]["selling_point_ids"] = ["sp_002"]
    script["scenes"][0]["fact_ids"] = ["pf_002"]
    write_json(path, script)

    with pytest.raises(OutputReferenceError) as exc_info:
        load_output_fixtures(fixture_dir, golden_case)

    message = str(exc_info.value)
    assert "scene_001" in message
    assert "ci_001" in message
    assert "sp_002" in message


def test_script_missing_fact_id_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["scenes"][0]["fact_ids"] = ["pf_missing"]
    write_json(path, script)

    with pytest.raises(OutputReferenceError, match="pf_missing"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_scene_fact_must_be_supported_by_scene_selling_points(
    tmp_path,
    golden_case,
):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["creative_idea_id"] = "ci_002"
    script["source_usages"][3]["source_id"] = "ri_002"
    script["scenes"][0]["selling_point_ids"] = ["sp_002"]
    script["scenes"][0]["fact_ids"] = ["pf_001"]
    write_json(path, script)

    with pytest.raises(OutputReferenceError) as exc_info:
        load_output_fixtures(fixture_dir, golden_case)

    message = str(exc_info.value)
    assert "scene_001" in message
    assert "pf_001" in message
    assert "sp_002" in message


def test_script_reference_insight_usage_must_belong_to_selected_idea(
    tmp_path,
    golden_case,
):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["creative_idea_id"] = "ci_002"
    script["scenes"][0]["selling_point_ids"] = ["sp_002"]
    script["scenes"][0]["fact_ids"] = ["pf_002"]
    script["scenes"][1]["selling_point_ids"] = ["sp_002"]
    script["scenes"][1]["fact_ids"] = ["pf_002"]
    script["scenes"][2]["selling_point_ids"] = ["sp_002"]
    script["scenes"][2]["fact_ids"] = ["pf_002"]
    write_json(path, script)

    with pytest.raises(OutputReferenceError) as exc_info:
        load_output_fixtures(fixture_dir, golden_case)

    message = str(exc_info.value)
    assert "ci_002" in message
    assert "ri_001" in message


def test_script_empty_scenes_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["scenes"] = []
    write_json(path, script)

    with pytest.raises(OutputSchemaError, match="scenes"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_missing_required_field_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    del script["cta"]
    write_json(path, script)

    with pytest.raises(OutputSchemaError, match="cta"):
        load_output_fixtures(fixture_dir, golden_case)


def test_script_unknown_field_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    path = fixture_dir / "script_draft.json"
    script = read_json(path)
    script["prompt_version"] = "not phase 1b"
    write_json(path, script)

    with pytest.raises(OutputSchemaError, match="prompt_version"):
        load_output_fixtures(fixture_dir, golden_case)


def test_fixture_directory_missing_fails(tmp_path, golden_case):
    with pytest.raises(OutputFixturePathError, match="does not exist"):
        load_output_fixtures(tmp_path / "missing", golden_case)


def test_fixture_path_not_directory_fails(tmp_path, golden_case):
    file_path = tmp_path / "not_a_dir"
    file_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(OutputFixturePathError, match="not a directory"):
        load_output_fixtures(file_path, golden_case)


def test_fixture_missing_file_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    (fixture_dir / "creative_ideas.json").unlink()

    with pytest.raises(OutputFixtureFileError, match="creative_ideas.json"):
        load_output_fixtures(fixture_dir, golden_case)


def test_fixture_invalid_json_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    (fixture_dir / "script_draft.json").write_text("{invalid", encoding="utf-8")

    with pytest.raises(OutputFixtureJsonError, match="Invalid JSON"):
        load_output_fixtures(fixture_dir, golden_case)


def test_fixture_wrong_json_root_fails(tmp_path, golden_case):
    fixture_dir = copy_fixture(tmp_path)
    write_json(fixture_dir / "creative_ideas.json", {})

    with pytest.raises(OutputSchemaError, match="root must be a JSON array"):
        load_output_fixtures(fixture_dir, golden_case)
