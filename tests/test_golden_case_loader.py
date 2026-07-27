import json
import shutil
from pathlib import Path

import pytest

from tk_script_agent_lab.domain import (
    GoldenCase,
    GoldenCaseFileError,
    GoldenCaseJsonError,
    GoldenCasePathError,
    GoldenCaseValidationError,
)
from tk_script_agent_lab.golden_case import load_golden_case


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"


def copy_case(tmp_path: Path) -> Path:
    case_dir = tmp_path / "car_vacuum_v1"
    shutil.copytree(GOLDEN_CASE_DIR, case_dir)
    return case_dir


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def test_loads_existing_golden_case_as_models():
    golden_case = load_golden_case(GOLDEN_CASE_DIR)

    assert isinstance(golden_case, GoldenCase)
    assert golden_case.product_profile.product_version_id == "prod_car_vacuum_001_v1"
    assert golden_case.product_profile.product_name == "Portable Car Vacuum Cleaner"
    assert len(golden_case.product_facts) == 4
    assert len(golden_case.selling_points) == 3
    assert len(golden_case.reference_videos) == 3
    assert golden_case.is_placeholder is True


def test_loaded_golden_case_has_expected_ids_and_references():
    golden_case = load_golden_case(GOLDEN_CASE_DIR)

    fact_ids = {fact.fact_id for fact in golden_case.product_facts}
    selling_point_ids = {point.selling_point_id for point in golden_case.selling_points}
    reference_ids = {video.reference_id for video in golden_case.reference_videos}
    referenced_fact_ids = {
        fact_id
        for point in golden_case.selling_points
        for fact_id in point.fact_ids
    }

    assert fact_ids == {"pf_001", "pf_002", "pf_003", "pf_004"}
    assert selling_point_ids == {"sp_001", "sp_002", "sp_003"}
    assert reference_ids == {"ref_001", "ref_002", "ref_003"}
    assert referenced_fact_ids.issubset(fact_ids)


def test_duplicate_product_fact_id_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    facts_path = case_dir / "product_facts.json"
    facts = read_json(facts_path)
    facts[1]["fact_id"] = facts[0]["fact_id"]
    write_json(facts_path, facts)

    with pytest.raises(GoldenCaseValidationError, match="ProductFact.fact_id"):
        load_golden_case(case_dir)


def test_duplicate_selling_point_id_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    points_path = case_dir / "selling_points.json"
    points = read_json(points_path)
    points[1]["selling_point_id"] = points[0]["selling_point_id"]
    write_json(points_path, points)

    with pytest.raises(GoldenCaseValidationError, match="SellingPoint.selling_point_id"):
        load_golden_case(case_dir)


def test_duplicate_reference_video_id_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    references_path = case_dir / "reference_videos.json"
    references = read_json(references_path)
    references[1]["reference_id"] = references[0]["reference_id"]
    write_json(references_path, references)

    with pytest.raises(GoldenCaseValidationError, match="ReferenceVideo.reference_id"):
        load_golden_case(case_dir)


def test_missing_fact_reference_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    points_path = case_dir / "selling_points.json"
    points = read_json(points_path)
    points[0]["fact_ids"] = ["pf_missing"]
    write_json(points_path, points)

    with pytest.raises(GoldenCaseValidationError, match="missing fact_ids"):
        load_golden_case(case_dir)


def test_product_version_mismatch_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    facts_path = case_dir / "product_facts.json"
    facts = read_json(facts_path)
    facts[0]["product_version_id"] = "other_version"
    write_json(facts_path, facts)

    with pytest.raises(GoldenCaseValidationError, match="product_version_id"):
        load_golden_case(case_dir)


def test_missing_required_file_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    (case_dir / "selling_points.json").unlink()

    with pytest.raises(GoldenCaseFileError, match="selling_points.json"):
        load_golden_case(case_dir)


def test_missing_directory_fails(tmp_path):
    with pytest.raises(GoldenCasePathError, match="does not exist"):
        load_golden_case(tmp_path / "missing_case")


def test_path_that_is_not_directory_fails(tmp_path):
    file_path = tmp_path / "not_a_case_dir"
    file_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(GoldenCasePathError, match="not a directory"):
        load_golden_case(file_path)


def test_invalid_json_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    (case_dir / "product_profile.json").write_text("{invalid", encoding="utf-8")

    with pytest.raises(GoldenCaseJsonError, match="Invalid JSON"):
        load_golden_case(case_dir)


def test_invalid_utf8_json_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    (case_dir / "product_profile.json").write_bytes(b"\xff")

    with pytest.raises(GoldenCaseJsonError, match="Invalid text encoding"):
        load_golden_case(case_dir)


def test_file_read_os_error_is_wrapped(tmp_path, monkeypatch):
    case_dir = copy_case(tmp_path)
    original_open = Path.open

    def fail_product_profile_open(path, *args, **kwargs):
        if path.name == "product_profile.json":
            raise OSError("permission denied for test")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_product_profile_open)

    with pytest.raises(GoldenCaseFileError, match="Could not read"):
        load_golden_case(case_dir)


def test_wrong_json_root_type_fails(tmp_path):
    case_dir = copy_case(tmp_path)
    write_json(case_dir / "product_profile.json", [])

    with pytest.raises(GoldenCaseValidationError, match="root must be a JSON object"):
        load_golden_case(case_dir)


def test_required_string_field_must_not_be_blank(tmp_path):
    case_dir = copy_case(tmp_path)
    profile_path = case_dir / "product_profile.json"
    profile = read_json(profile_path)
    profile["product_name"] = " "
    write_json(profile_path, profile)

    with pytest.raises(GoldenCaseValidationError, match="product_name"):
        load_golden_case(case_dir)


def test_placeholder_case_is_not_production_ready():
    golden_case = load_golden_case(GOLDEN_CASE_DIR)

    with pytest.raises(GoldenCaseValidationError, match="production-ready"):
        golden_case.require_production_ready()


def test_mixed_placeholder_reference_keeps_case_non_production(tmp_path):
    case_dir = copy_case(tmp_path)
    profile_path = case_dir / "product_profile.json"
    references_path = case_dir / "reference_videos.json"
    profile = read_json(profile_path)
    references = read_json(references_path)

    profile["notes"] = "Verified product data for production use."
    references[0]["url"] = "https://real.example/reference-video-1"
    references[0]["creator_or_source"] = "verified_source"
    references[1]["url"] = "https://example.com/reference-video-2"
    references[1]["creator_or_source"] = "verified_source"
    references[2]["url"] = "https://real.example/reference-video-3"
    references[2]["creator_or_source"] = "manual_placeholder"
    write_json(profile_path, profile)
    write_json(references_path, references)

    golden_case = load_golden_case(case_dir)

    assert golden_case.is_placeholder is True
    with pytest.raises(GoldenCaseValidationError, match="production-ready"):
        golden_case.require_production_ready()
