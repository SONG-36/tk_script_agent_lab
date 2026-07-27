from pathlib import Path

import pytest

from tk_script_agent_lab.domain import (
    CreativeSelectionError,
    OutputSchemaError,
    ProviderOutputError,
)
from tk_script_agent_lab.domain.validators import validate_script_draft
from tk_script_agent_lab.fixtures import load_output_fixtures
from tk_script_agent_lab.golden_case import load_golden_case
from tk_script_agent_lab.pipeline import (
    CreativeOptions,
    generate_selected_script,
    prepare_creative_options,
    select_creative_idea,
)
from tk_script_agent_lab.providers import (
    FakeCreativeIdeaProvider,
    FakeReferenceInsightProvider,
    FakeScriptDraftProvider,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE_DIR = ROOT / "data" / "golden_cases" / "car_vacuum_v1"
FIXTURE_DIR = ROOT / "data" / "fixtures" / "car_vacuum_v1"


@pytest.fixture
def golden_case():
    return load_golden_case(GOLDEN_CASE_DIR)


@pytest.fixture
def fixtures(golden_case):
    return load_output_fixtures(FIXTURE_DIR, golden_case)


def test_pipeline_normal_path_matches_fixture_and_is_deterministic(
    golden_case,
    fixtures,
):
    first_options = prepare_creative_options(
        golden_case,
        FakeReferenceInsightProvider(fixtures),
        FakeCreativeIdeaProvider(fixtures),
    )
    first_script = generate_selected_script(
        golden_case,
        first_options,
        "ci_001",
        FakeScriptDraftProvider(fixtures),
    )
    second_options = prepare_creative_options(
        golden_case,
        FakeReferenceInsightProvider(fixtures),
        FakeCreativeIdeaProvider(fixtures),
    )
    second_script = generate_selected_script(
        golden_case,
        second_options,
        "ci_001",
        FakeScriptDraftProvider(fixtures),
    )

    assert [item.model_dump() for item in first_options.reference_insights] == [
        item.model_dump() for item in fixtures.reference_insights
    ]
    assert [item.model_dump() for item in first_options.creative_ideas] == [
        item.model_dump() for item in fixtures.creative_ideas
    ]
    assert first_script.model_dump() == fixtures.script_draft.model_dump()
    assert first_options == second_options
    assert first_script == second_script


def test_select_creative_idea_requires_explicit_existing_unique_id(fixtures):
    selected = select_creative_idea(fixtures.creative_ideas, "ci_001")

    assert selected.idea_id == "ci_001"
    with pytest.raises(CreativeSelectionError, match="missing CreativeIdea id=ci_missing"):
        select_creative_idea(fixtures.creative_ideas, "ci_missing")
    with pytest.raises(CreativeSelectionError, match="explicitly provided"):
        select_creative_idea(fixtures.creative_ideas, " ")

    duplicate_ideas = fixtures.creative_ideas + [
        fixtures.creative_ideas[0].model_copy(deep=True)
    ]
    with pytest.raises(CreativeSelectionError, match="duplicate id=ci_001"):
        select_creative_idea(duplicate_ideas, "ci_001")


def test_prepare_options_rejects_empty_insight_output(golden_case, fixtures):
    class EmptyInsightProvider:
        def generate(self, golden_case):
            return []

    with pytest.raises(ProviderOutputError, match="ReferenceInsight output"):
        prepare_creative_options(
            golden_case,
            EmptyInsightProvider(),
            FakeCreativeIdeaProvider(fixtures),
        )


def test_prepare_options_rejects_duplicate_insight_ids(golden_case, fixtures):
    class DuplicateInsightProvider:
        def generate(self, golden_case):
            return [
                fixtures.reference_insights[0],
                fixtures.reference_insights[1].model_copy(
                    update={"insight_id": fixtures.reference_insights[0].insight_id}
                ),
            ]

    with pytest.raises(ProviderOutputError, match="ReferenceInsight.insight_id"):
        prepare_creative_options(
            golden_case,
            DuplicateInsightProvider(),
            FakeCreativeIdeaProvider(fixtures),
        )


def test_prepare_options_rejects_missing_reference_id(golden_case, fixtures):
    class MissingReferenceInsightProvider:
        def generate(self, golden_case):
            return [
                fixtures.reference_insights[0].model_copy(
                    update={"reference_id": "ref_missing"}
                )
            ]

    with pytest.raises(ProviderOutputError, match="ref_missing"):
        prepare_creative_options(
            golden_case,
            MissingReferenceInsightProvider(),
            FakeCreativeIdeaProvider(fixtures),
        )


def test_prepare_options_rejects_empty_idea_output(golden_case, fixtures):
    class EmptyIdeaProvider:
        def generate(self, golden_case, insights):
            return []

    with pytest.raises(ProviderOutputError, match="CreativeIdea output"):
        prepare_creative_options(
            golden_case,
            FakeReferenceInsightProvider(fixtures),
            EmptyIdeaProvider(),
        )


def test_prepare_options_rejects_duplicate_idea_ids(golden_case, fixtures):
    class DuplicateIdeaProvider:
        def generate(self, golden_case, insights):
            return [
                fixtures.creative_ideas[0],
                fixtures.creative_ideas[1].model_copy(
                    update={"idea_id": fixtures.creative_ideas[0].idea_id}
                ),
            ]

    with pytest.raises(ProviderOutputError, match="CreativeIdea.idea_id"):
        prepare_creative_options(
            golden_case,
            FakeReferenceInsightProvider(fixtures),
            DuplicateIdeaProvider(),
        )


def test_prepare_options_rejects_missing_selling_point_id(golden_case, fixtures):
    class MissingSellingPointIdeaProvider:
        def generate(self, golden_case, insights):
            return [
                fixtures.creative_ideas[0].model_copy(
                    update={"selected_selling_point_ids": ["sp_missing"]}
                )
            ]

    with pytest.raises(ProviderOutputError, match="sp_missing"):
        prepare_creative_options(
            golden_case,
            FakeReferenceInsightProvider(fixtures),
            MissingSellingPointIdeaProvider(),
        )


def test_prepare_options_rejects_idea_insight_not_returned_by_provider(
    golden_case,
    fixtures,
):
    class MissingInsightIdeaProvider:
        def generate(self, golden_case, insights):
            return [
                fixtures.creative_ideas[0].model_copy(
                    update={"source_insight_ids": ["ri_missing"]}
                )
            ]

    with pytest.raises(ProviderOutputError, match="ri_missing"):
        prepare_creative_options(
            golden_case,
            FakeReferenceInsightProvider(fixtures),
            MissingInsightIdeaProvider(),
        )


def test_prepare_options_revalidates_creative_idea_schema(golden_case, fixtures):
    class BlankHookIdeaProvider:
        def generate(self, golden_case, insights):
            return [
                fixtures.creative_ideas[0].model_copy(update={"hook": " "})
            ]

    with pytest.raises(ProviderOutputError, match="hook"):
        prepare_creative_options(
            golden_case,
            FakeReferenceInsightProvider(fixtures),
            BlankHookIdeaProvider(),
        )


def test_generate_script_rejects_wrong_product_version(golden_case, fixtures):
    class WrongVersionScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            return fixtures.script_draft.model_copy(
                update={"product_version_id": "other_version"}
            )

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="product_version_id"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            WrongVersionScriptProvider(),
        )


def test_generate_script_revalidates_nested_scene_schema(golden_case, fixtures):
    class InvalidSceneDurationScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            scenes = [
                scene.model_copy(deep=True) for scene in fixtures.script_draft.scenes
            ]
            scenes[0] = scenes[0].model_copy(update={"duration_seconds": 0})
            return fixtures.script_draft.model_copy(update={"scenes": scenes})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="duration_seconds"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            InvalidSceneDurationScriptProvider(),
        )


def test_generate_script_revalidates_nested_source_usage_schema(golden_case, fixtures):
    class InvalidSourceTypeScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            usages = [
                usage.model_copy(deep=True)
                for usage in fixtures.script_draft.source_usages
            ]
            usages[0] = usages[0].model_copy(update={"source_type": "web_page"})
            return fixtures.script_draft.model_copy(update={"source_usages": usages})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="source_type") as exc_info:
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            InvalidSourceTypeScriptProvider(),
        )

    assert "KeyError" not in str(exc_info.value)


def test_validate_script_draft_revalidates_nested_schema(golden_case, fixtures):
    scenes = [scene.model_copy(deep=True) for scene in fixtures.script_draft.scenes]
    scenes[0] = scenes[0].model_copy(update={"duration_seconds": 0})
    script = fixtures.script_draft.model_copy(update={"scenes": scenes})

    with pytest.raises(OutputSchemaError, match="duration_seconds"):
        validate_script_draft(
            golden_case,
            fixtures.reference_insights,
            fixtures.creative_ideas,
            script,
            selected_idea_id="ci_001",
        )


def test_generate_script_rejects_script_for_different_selected_idea(
    golden_case,
    fixtures,
):
    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)

    with pytest.raises(ProviderOutputError, match="selected_idea_id=ci_002"):
        generate_selected_script(
            golden_case,
            options,
            "ci_002",
            FakeScriptDraftProvider(fixtures),
        )


def test_generate_script_rejects_scene_selling_point_outside_selected_idea(
    golden_case,
    fixtures,
):
    class OutOfBoundsSellingPointScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            scenes = [
                scene.model_copy(deep=True) for scene in fixtures.script_draft.scenes
            ]
            scenes[0].selling_point_ids = ["sp_002"]
            scenes[0].fact_ids = ["pf_002"]
            return fixtures.script_draft.model_copy(update={"scenes": scenes})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="sp_002"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            OutOfBoundsSellingPointScriptProvider(),
        )


def test_generate_script_rejects_fact_not_supported_by_scene_selling_point(
    golden_case,
    fixtures,
):
    class UnsupportedFactScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            scenes = [
                scene.model_copy(deep=True) for scene in fixtures.script_draft.scenes
            ]
            scenes[0].fact_ids = ["pf_004"]
            return fixtures.script_draft.model_copy(update={"scenes": scenes})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="pf_004"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            UnsupportedFactScriptProvider(),
        )


def test_generate_script_rejects_source_usage_fact_not_used_in_scenes(
    golden_case,
    fixtures,
):
    class UnusedFactUsageScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            usages = [
                usage.model_copy(deep=True)
                for usage in fixtures.script_draft.source_usages
            ]
            usages[0].source_id = "pf_004"
            return fixtures.script_draft.model_copy(update={"source_usages": usages})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="ScriptScene.fact_ids"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            UnusedFactUsageScriptProvider(),
        )


def test_generate_script_rejects_source_usage_selling_point_not_used_in_scenes(
    golden_case,
    fixtures,
):
    class UnusedSellingPointUsageScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            usages = [
                usage.model_copy(deep=True)
                for usage in fixtures.script_draft.source_usages
            ]
            usages[2].source_id = "sp_002"
            return fixtures.script_draft.model_copy(update={"source_usages": usages})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="ScriptScene.selling_point_ids"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            UnusedSellingPointUsageScriptProvider(),
        )


def test_generate_script_rejects_reference_insight_outside_selected_idea(
    golden_case,
    fixtures,
):
    scenes = [
        scene.model_copy(update={"selling_point_ids": ["sp_002"], "fact_ids": ["pf_002"]})
        for scene in fixtures.script_draft.scenes
    ]
    usages = [
        usage.model_copy(deep=True) for usage in fixtures.script_draft.source_usages
    ]
    usages[0].source_id = "pf_002"
    usages[1].source_id = "pf_002"
    usages[2].source_id = "sp_002"
    script = fixtures.script_draft.model_copy(
        update={"creative_idea_id": "ci_002", "scenes": scenes, "source_usages": usages}
    )

    class WrongInsightUsageScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            return script

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="ri_001"):
        generate_selected_script(
            golden_case,
            options,
            "ci_002",
            WrongInsightUsageScriptProvider(),
        )


def test_generate_script_rejects_duplicate_scene_ids(golden_case, fixtures):
    class DuplicateSceneScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            scenes = [
                scene.model_copy(deep=True) for scene in fixtures.script_draft.scenes
            ]
            scenes[1].scene_id = scenes[0].scene_id
            return fixtures.script_draft.model_copy(update={"scenes": scenes})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="ScriptScene.scene_id"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            DuplicateSceneScriptProvider(),
        )


def test_generate_script_rejects_empty_scene_or_usage_lists(golden_case, fixtures):
    class EmptyScenesScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            return fixtures.script_draft.model_copy(update={"scenes": []})

    class EmptyUsagesScriptProvider:
        def generate(self, golden_case, selected_idea, insights):
            return fixtures.script_draft.model_copy(update={"source_usages": []})

    options = CreativeOptions(fixtures.reference_insights, fixtures.creative_ideas)
    with pytest.raises(ProviderOutputError, match="scenes"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            EmptyScenesScriptProvider(),
        )
    with pytest.raises(ProviderOutputError, match="source_usages"):
        generate_selected_script(
            golden_case,
            options,
            "ci_001",
            EmptyUsagesScriptProvider(),
        )
