"""Review workflow orchestration and synthesis."""

import click
import textwrap
from typing import Dict
from ai_toolkit.commands.review.prompts import SYNTHESIS_TEMPLATE
from langchain.messages import HumanMessage, SystemMessage
from ai_toolkit.commands.review.analyzers import (
    persona_analyzer
)
from ai_toolkit.commands.review.review_models import ReviewResult
from ai_toolkit.model_helper import get_model


def synthesize_and_refine_review(
    specialist_reviews: Dict[str, ReviewResult],
    model: str,
) -> ReviewResult:
    """Synthesize specialist reviews and refine into polished final report.
    
    This function combines two responsibilities:
    1. Consolidates reviews from multiple specialists (performance, maintainability, security)
    2. Critiques and polishes the consolidated review for clarity, accuracy, and actionability
    
    Args:
        specialist_reviews: Dictionary with keys 'performance', 'maintainability', 'security'
                          containing the specialist reviews.
        model: The LLM model to use for synthesis and refinement.
        
    Returns:
        The synthesized and refined final review report.
    """
    click.echo("  🔄 Synthesizing all perspectives and refining recommendations...")
    
    # Format the specialist reviews for the prompt
    specialists_text = textwrap.dedent(f"""
        Performance Review:
        {specialist_reviews.get('performance').__str__() if specialist_reviews.get('performance') else 'No performance review available.'}

        Maintainability Review:
        {specialist_reviews.get('maintainability').__str__() if specialist_reviews.get('maintainability') else 'No maintainability review available.'}

        Security Review:
        {specialist_reviews.get('security').__str__() if specialist_reviews.get('security') else 'No security review available.'}
        """).strip()

    messages = [
        SystemMessage(SYNTHESIS_TEMPLATE),
        HumanMessage(content=f"<specialists_reviews>\n{specialists_text}\n</specialists_reviews>"),
    ]

    llm = get_model(model)
    llm_with_output = llm.with_structured_output(ReviewResult)
    llm_response = llm_with_output.invoke(messages)
    click.echo("  ✅ Synthesis and refinement complete")
    return llm_response # type: ignore


def perform_review(diff: str, model: str) -> ReviewResult:
    """Analyze a git diff and generate review comments using a comprehensive multi-phase workflow.

    This function implements a four-phase review process:
    1. Core Analysis: Syntax and logic review with automated tools
    2. Specialist Reviews: Performance, maintainability, and security analysis
    3. Synthesis & Refinement: Consolidate and critique all perspectives
    4. Final Report: Polished, actionable recommendations

    The workflow ensures comprehensive coverage from multiple expert perspectives,
    then synthesizes and refines them into clear, actionable recommendations.
    
    Args:
        diff: The git diff to review
        model: The LLM model to use for all analysis steps
        
    Returns:
        ReviewResult containing the final polished review
    """

    
    # Phase 2: Specialist reviews (performance, maintainability, security)
    click.echo("\n\n🎯 PHASE 1: SPECIALIST REVIEWS")
    click.echo("─" * 60)
    
    personas = ["performance", "maintainability", "security"]
    specialist_reviews = {}
    
    for persona in personas:
        click.echo(f"\n  ✓ Running {persona} analysis...")
        specialist_reviews[persona] = persona_analyzer(diff, persona=persona, model=model)
        click.echo(f"  ✓ {persona.capitalize()} analysis complete.")

    # Phase 3: Synthesis & Refinement (lead architect perspective)
    click.echo("\n\n🏗️  PHASE 2: SYNTHESIS & REFINEMENT")
    click.echo("─" * 60)
    
    final_review = synthesize_and_refine_review(specialist_reviews, model=model)
    
    click.echo("\n" + "="*60)
    click.echo("✅ CODE REVIEW COMPLETE")
    click.echo("="*60)
    # Keep behavior consistent with existing tests: return empty ReviewResult
    result = final_review
    return result
