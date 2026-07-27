from dataclasses import dataclass

from tk_script_agent_lab.domain.models import (
    CreativeIdea,
    GoldenCase,
    OutputFixtureSet,
    ReferenceInsight,
    ScriptDraft,
)


@dataclass(frozen=True)
class FakeReferenceInsightProvider:
    fixtures: OutputFixtureSet

    def generate(self, golden_case: GoldenCase) -> list[ReferenceInsight]:
        return [
            insight.model_copy(deep=True)
            for insight in self.fixtures.reference_insights
        ]


@dataclass(frozen=True)
class FakeCreativeIdeaProvider:
    fixtures: OutputFixtureSet

    def generate(
        self,
        golden_case: GoldenCase,
        insights: list[ReferenceInsight],
    ) -> list[CreativeIdea]:
        return [idea.model_copy(deep=True) for idea in self.fixtures.creative_ideas]


@dataclass(frozen=True)
class FakeScriptDraftProvider:
    fixtures: OutputFixtureSet

    def generate(
        self,
        golden_case: GoldenCase,
        selected_idea: CreativeIdea,
        insights: list[ReferenceInsight],
    ) -> ScriptDraft:
        return self.fixtures.script_draft.model_copy(deep=True)
