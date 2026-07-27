from dataclasses import dataclass

from tk_script_agent_lab.domain.errors import (
    CreativeSelectionError,
    OutputValidationError,
    PipelineValidationError,
    ProviderOutputError,
)
from tk_script_agent_lab.domain.models import (
    CreativeIdea,
    GoldenCase,
    ReferenceInsight,
    ScriptDraft,
)
from tk_script_agent_lab.domain.validators import (
    validate_creative_ideas,
    validate_reference_insights,
    validate_script_draft,
)
from tk_script_agent_lab.providers.protocols import (
    CreativeIdeaProvider,
    ReferenceInsightProvider,
    ScriptDraftProvider,
)


@dataclass(frozen=True)
class CreativeOptions:
    reference_insights: list[ReferenceInsight]
    creative_ideas: list[CreativeIdea]


def prepare_creative_options(
    golden_case: GoldenCase,
    insight_provider: ReferenceInsightProvider,
    idea_provider: CreativeIdeaProvider,
) -> CreativeOptions:
    insights = insight_provider.generate(golden_case)
    try:
        validate_reference_insights(golden_case, insights)
    except OutputValidationError as exc:
        raise ProviderOutputError(
            f"ReferenceInsightProvider returned invalid output: {exc}"
        ) from exc

    ideas = idea_provider.generate(golden_case, insights)
    try:
        validate_creative_ideas(golden_case, insights, ideas)
    except OutputValidationError as exc:
        raise ProviderOutputError(
            f"CreativeIdeaProvider returned invalid output: {exc}"
        ) from exc

    return CreativeOptions(
        reference_insights=[insight.model_copy(deep=True) for insight in insights],
        creative_ideas=[idea.model_copy(deep=True) for idea in ideas],
    )


def generate_selected_script(
    golden_case: GoldenCase,
    options: CreativeOptions,
    selected_idea_id: str,
    script_provider: ScriptDraftProvider,
) -> ScriptDraft:
    try:
        selected_idea = select_creative_idea(
            options.creative_ideas,
            selected_idea_id,
        )
    except CreativeSelectionError:
        raise
    except Exception as exc:
        raise PipelineValidationError(
            f"Creative options failed deterministic validation: {exc}"
        ) from exc

    script = script_provider.generate(
        golden_case,
        selected_idea,
        options.reference_insights,
    )
    try:
        validate_script_draft(
            golden_case,
            options.reference_insights,
            options.creative_ideas,
            script,
            selected_idea_id=selected_idea.idea_id,
        )
    except OutputValidationError as exc:
        raise ProviderOutputError(
            f"ScriptDraftProvider returned invalid output: {exc}"
        ) from exc

    return script.model_copy(deep=True)


def select_creative_idea(
    ideas: list[CreativeIdea],
    selected_idea_id: str,
) -> CreativeIdea:
    if not selected_idea_id or not selected_idea_id.strip():
        raise CreativeSelectionError("selected_idea_id must be explicitly provided")

    matches = [idea for idea in ideas if idea.idea_id == selected_idea_id]
    if not matches:
        raise CreativeSelectionError(
            f"selected_idea_id references missing CreativeIdea id={selected_idea_id}"
        )
    if len(matches) > 1:
        raise CreativeSelectionError(
            f"selected_idea_id must identify one CreativeIdea; "
            f"duplicate id={selected_idea_id}"
        )
    return matches[0].model_copy(deep=True)
