import json
import re
import tomllib
from pathlib import Path

import tk_script_agent_lab


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"


def load_json(name: str):
    with (GOLDEN_CASE_DIR / name).open(encoding="utf-8") as file:
        return json.load(file)


def parse_env_example() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def test_package_import_and_version():
    assert tk_script_agent_lab.__version__ == "0.1.0"


def test_phase0_dependency_boundary():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["requires-python"] == ">=3.12"
    assert pyproject["project"]["dependencies"] == ["pydantic>=2,<3"]
    assert pyproject["project"]["optional-dependencies"] == {
        "dev": ["pytest>=8.0"],
    }
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12"


def test_golden_case_json_loads():
    assert load_json("product_profile.json")
    assert load_json("product_facts.json")
    assert load_json("selling_points.json")
    assert load_json("reference_videos.json")


def test_golden_case_references_are_consistent():
    profile = load_json("product_profile.json")
    facts = load_json("product_facts.json")
    selling_points = load_json("selling_points.json")
    references = load_json("reference_videos.json")

    product_version_id = profile["product_version_id"]
    fact_ids = [fact["fact_id"] for fact in facts]
    selling_point_ids = [point["selling_point_id"] for point in selling_points]
    reference_ids = [reference["reference_id"] for reference in references]

    assert len(fact_ids) == len(set(fact_ids))
    assert len(selling_point_ids) == len(set(selling_point_ids))
    assert len(reference_ids) == len(set(reference_ids))
    assert all(fact["product_version_id"] == product_version_id for fact in facts)
    assert {
        fact_id
        for point in selling_points
        for fact_id in point["fact_ids"]
    }.issubset(set(fact_ids))


def test_golden_case_is_marked_as_placeholder():
    profile = load_json("product_profile.json")
    references = load_json("reference_videos.json")

    assert "Template case" in profile["notes"]
    assert all(reference["url"].startswith("https://example.com/") for reference in references)
    assert all(reference["creator_or_source"] == "manual_placeholder" for reference in references)


def test_env_example_has_no_real_secret_and_safe_defaults():
    values = parse_env_example()
    api_key = values["OPENAI_API_KEY"]

    assert api_key == "" or "placeholder" in api_key.lower()
    assert not re.search(r"sk-[A-Za-z0-9_-]{20,}", api_key)
    assert values["ENABLE_REAL_MODEL_CALLS"] == "false"
    assert values["ENABLE_BATCH_RUNS"] == "false"
    assert values["ENABLE_EXTERNAL_WRITES"] == "false"
