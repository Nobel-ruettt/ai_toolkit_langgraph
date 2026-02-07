"""CLI command for code review."""

import textwrap
import warnings
import click
from git import GitCommandError

from ai_toolkit.git_utils import GitHelper
from ai_toolkit.commands.review.workflow import perform_review
import os
from pathlib import Path
from datetime import datetime

# Suppress the specific ResourceWarning for subprocess on Windows
warnings.filterwarnings("ignore", category=ResourceWarning, module="subprocess")


@click.command()
@click.option("--staged", "staged", is_flag=True, default=False, help="Review staged changes")
@click.option("--uncommitted", "uncommitted", is_flag=True, default=False, help="Review uncommitted changes")
@click.pass_context
def review(ctx, staged: bool, uncommitted: bool):
    """Review code changes and provide feedback.

    Defaults to reviewing staged changes when neither option is provided.
    Analyzes the diff and provides structured review comments.
    """
    # Default to staged if no flag is provided
    if not staged and not uncommitted:
        staged = True

    try:
        # Get the appropriate diff
        # Determine mode and get diff
        mode = "staged" if staged else "uncommitted"
        diff = GitHelper.get_diff(mode)
        diff_type = mode
        
        # Check if there's anything to review
        if diff is None:
            click.echo(f"No {diff_type} changes to review.")
            return

        # Write diff to markdown file and display info
        
        click.echo(f"\n📝 Reviewing {diff_type} changes:")
        click.echo("─" * 60)
       
        # Perform the review
        model = ctx.obj["model"]
        review_result = perform_review(diff, model=model)
        # Write review to markdown file
        reviews_dir = Path("reviews")
        reviews_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        review_file = reviews_dir / f"review_{timestamp}.md"
        
        with open(review_file, "w", encoding="utf-8") as f:
            f.write(f"# Code Review - {mode.capitalize()} Changes\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(review_result.str_markdown__())

        click.echo(f"✅ Review saved to: {review_file}")

        
    except GitCommandError as e:
        click.echo(f"Git error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)
