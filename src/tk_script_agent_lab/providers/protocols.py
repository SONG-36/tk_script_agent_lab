from typing import Protocol, runtime_checkable

from tk_script_agent_lab.domain.models import (
    CreativeIdea,
    GoldenCase,
    ReferenceInsight,
    ScriptDraft,
)


@runtime_checkable
class ReferenceInsightProvider(Protocol):
    def generate(self, golden_case: GoldenCase) -> list[ReferenceInsight]:
        ...


@runtime_checkable
class CreativeIdeaProvider(Protocol):
    def generate(
        self,
        golden_case: GoldenCase,
        insights: list[ReferenceInsight],
    ) -> list[CreativeIdea]:
        ...


@runtime_checkable
class ScriptDraftProvider(Protocol):
    def generate(
        self,
        golden_case: GoldenCase,
        selected_idea: CreativeIdea,
        insights: list[ReferenceInsight],
    ) -> ScriptDraft:
        ...
