import random
import socket
import time
from pathlib import Path

from tk_script_agent_lab.fixtures import load_output_fixtures
from tk_script_agent_lab.golden_case import load_golden_case
from tk_script_agent_lab.providers import (
    FakeCreativeIdeaProvider,
    FakeReferenceInsightProvider,
    FakeScriptDraftProvider,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"
FIXTURE_DIR = ROOT / "data" / "fixtures" / "car_vacuum_v1"


def load_case_and_fixtures():
    golden_case = load_golden_case(GOLDEN_CASE_DIR)
    fixtures = load_output_fixtures(FIXTURE_DIR, golden_case)
    return golden_case, fixtures


def test_fake_providers_return_fixture_objects_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    golden_case, fixtures = load_case_and_fixtures()

    insights = FakeReferenceInsightProvider(fixtures).generate(golden_case)
    ideas = FakeCreativeIdeaProvider(fixtures).generate(golden_case, insights)
    script = FakeScriptDraftProvider(fixtures).generate(
        golden_case,
        ideas[0],
        insights,
    )

    assert [insight.model_dump() for insight in insights] == [
        insight.model_dump() for insight in fixtures.reference_insights
    ]
    assert [idea.model_dump() for idea in ideas] == [
        idea.model_dump() for idea in fixtures.creative_ideas
    ]
    assert script.model_dump() == fixtures.script_draft.model_dump()


def test_fake_provider_output_is_repeatable_and_isolated():
    golden_case, fixtures = load_case_and_fixtures()
    provider = FakeReferenceInsightProvider(fixtures)

    first = provider.generate(golden_case)
    first[0].summary = "mutated outside provider"
    second = provider.generate(golden_case)

    assert second[0].summary == fixtures.reference_insights[0].summary
    assert [item.model_dump() for item in second] == [
        item.model_dump() for item in provider.generate(golden_case)
    ]


def test_fake_providers_do_not_use_network_random_or_current_time(monkeypatch):
    golden_case, fixtures = load_case_and_fixtures()

    def fail(*args, **kwargs):
        raise AssertionError("external boundary should not be used")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(random, "random", fail)
    monkeypatch.setattr(time, "time", fail)

    insights = FakeReferenceInsightProvider(fixtures).generate(golden_case)
    ideas = FakeCreativeIdeaProvider(fixtures).generate(golden_case, insights)
    script = FakeScriptDraftProvider(fixtures).generate(
        golden_case,
        ideas[0],
        insights,
    )

    assert len(insights) == 3
    assert len(ideas) == 3
    assert script.script_id == "sd_001"
