"""Code analysis functions for different review perspectives."""

from langchain.messages import HumanMessage, SystemMessage

from ai_toolkit.commands.review.prompts import (
    PERFORMANCE_REVIEW_TEMPLATE,
    MAINTAINABILITY_REVIEW_TEMPLATE,
    SECURITY_REVIEW_TEMPLATE,
)
from ai_toolkit.commands.review.review_models import ReviewResult
from ai_toolkit.model_helper import get_model

def persona_analyzer(diff: str, persona: str, model: str) -> ReviewResult:
    """Analyze the provided diff for performance issues and optimizations.

    Call the LLM completion API to analyze the provided diff.
    """

    analyzer_prompt_dictionary = {
        "performance": PERFORMANCE_REVIEW_TEMPLATE,
        "maintainability": MAINTAINABILITY_REVIEW_TEMPLATE,
        "security": SECURITY_REVIEW_TEMPLATE,
    }

    if persona not in analyzer_prompt_dictionary:
        raise ValueError(f"Invalid persona '{persona}'. Valid options are: {list(analyzer_prompt_dictionary.keys())}")
    
    system_prompt = analyzer_prompt_dictionary[persona]

    messages = [
        SystemMessage(system_prompt),
        HumanMessage(content=f"Here are the code changes:\n<diff>\n{diff}\n</diff>"),
    ]

    llm = get_model(model)
    llm_with_output = llm.with_structured_output(ReviewResult) 
    result = llm_with_output.invoke(messages)
    return result # type: ignore