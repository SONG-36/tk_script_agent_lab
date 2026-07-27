from pathlib import Path

from tk_script_agent_lab.fixtures import load_output_fixtures
from tk_script_agent_lab.golden_case import load_golden_case
from tk_script_agent_lab.pipeline import (
    generate_selected_script,
    prepare_creative_options,
)
from tk_script_agent_lab.providers import (
    CreativeIdeaProvider,
    FakeCreativeIdeaProvider,
    FakeReferenceInsightProvider,
    FakeScriptDraftProvider,
    ReferenceInsightProvider,
    ScriptDraftProvider,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"
FIXTURE_DIR = ROOT / "data" / "fixtures" / "car_vacuum_v1"


def load_case_and_fixtures():
    golden_case = load_golden_case(GOLDEN_CASE_DIR)
    fixtures = load_output_fixtures(FIXTURE_DIR, golden_case)
    return golden_case, fixtures


def test_fake_providers_satisfy_protocols():
    golden_case, fixtures = load_case_and_fixtures()

    insight_provider = FakeReferenceInsightProvider(fixtures)
    idea_provider = FakeCreativeIdeaProvider(fixtures)
    script_provider = FakeScriptDraftProvider(fixtures)

    assert isinstance(insight_provider, ReferenceInsightProvider)
    assert isinstance(idea_provider, CreativeIdeaProvider)
    assert isinstance(script_provider, ScriptDraftProvider)
    assert insight_provider.generate(golden_case)
    assert idea_provider.generate(golden_case, fixtures.reference_insights)
    assert script_provider.generate(
        golden_case,
        fixtures.creative_ideas[0],
        fixtures.reference_insights,
    )


def test_pipeline_accepts_non_fake_protocol_implementations():
    golden_case, fixtures = load_case_and_fixtures()

    class StaticInsightProvider:
        def generate(self, golden_case):
            return fixtures.reference_insights

    class StaticIdeaProvider:
        def generate(self, golden_case, insights):
            return fixtures.creative_ideas

    class StaticScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            return fixtures.script_draft

    options = prepare_creative_options(
        golden_case,
        StaticInsightProvider(),
        StaticIdeaProvider(),
    )
    script = generate_selected_script(
        golden_case,
        options,
        "ci_001",
        StaticScriptProvider(),
    )

    assert [idea.idea_id for idea in options.creative_ideas] == [
        "ci_001",
        "ci_002",
        "ci_003",
    ]
    assert script.script_id == "sd_001"
