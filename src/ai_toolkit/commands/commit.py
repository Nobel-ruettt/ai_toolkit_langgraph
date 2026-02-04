import click
from typing import Optional
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from ai_toolkit.model_helper import get_model

# GitPython is a project dependency; import directly
from git import GitCommandError
from ..git_utils import GitHelper




# Prompt template for generating conventional commit messages
COMMIT_MESSAGE_PROMPT = """You are an expert software developer tasked with writing a clear, concise commit message following the Conventional Commits specification.

## Conventional Commits Format:
<type>[optional scope]: <description>

[optional body]

## Types:
- feat: A new feature
- fix: A bug fix
- docs: Documentation only changes
- style: Changes that don't affect code meaning (formatting, whitespace, etc.)
- refactor: Code change that neither fixes a bug nor adds a feature
- perf: Performance improvement
- test: Adding or updating tests
- build: Changes to build system or dependencies
- ci: Changes to CI configuration
- chore: Other changes that don't modify src or test files

## Instructions:
1. Analyze the git diff provided below
2. Determine the appropriate commit type based on the changes
3. Write a clear, imperative mood description (e.g., "add feature" not "added feature")
4. Keep the first line under 72 characters
5. If the changes are complex, include a body with:
   - Why the change was made
   - What was changed
   - Any important implementation details
6. Return ONLY the commit message text (no markdown code blocks, no explanations)
7. Use present tense, imperative mood
8. Be specific but concise

## Git Diff:
<diff>
{diff}
</diff>

## Commit Message:"""


def get_staged_diff() -> Optional[str]:
    """
    Retrieve the git diff of staged changes using GitPython.

    Returns:
        The diff output as a string, or None if there's an error or no staged changes.
    """
    try:
        diff_output = GitHelper.get_diff("staged")
        return diff_output
    except FileNotFoundError:
        click.echo("❌ Looks like Git isn't installed. Please install it first!", err=True)
        return None
    except GitCommandError as e:
        click.echo(f"❌ Hmm, couldn't retrieve your staged changes: {e}", err=True)
        return None
    except UnicodeDecodeError as e:
        click.echo(f"❌ Encountered encoding issues in your diff: {e}", err=True)
        return None


def generate_commit_message(diff: str, messages: list, model: str = "gpt-4o-mini") -> Optional[str]:
    """
    Generate a commit message using LLM based on the git diff and an existing
    conversation (messages). The messages list is expected to already contain
    the initial prompt/user message.
    
    Args:
        diff: The git diff output
        messages: The conversation history
        model: The LLM model to use for completion
    """
    click.echo("✨ Let me analyze your changes and craft a commit message...")

    llm = get_model(model, temperature=0.3)
    
    response = llm.invoke(messages)

    commit_message = str(response.content).strip()
    return commit_message


def perform_git_commit(commit_message: str) -> bool:
    """
    Perform the actual git commit with the provided message using GitPython.
    
    Args:
        commit_message: The commit message to use
        
    Returns:
        True if commit was successful, False otherwise
    """
    try:
        GitHelper.commit(commit_message)
        return True
    except FileNotFoundError:
        click.echo("❌ Looks like Git isn't installed. Please install it first!", err=True)
        return False
    except GitCommandError as e:
        click.echo(f"❌ The commit didn't go through: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"❌ The commit didn't go through: {e}", err=True)
        return False


@click.command()
@click.pass_context
def commit(ctx):
    """Generate a commit message based on staged changes with optional adjustments."""
    model = ctx.obj["model"]
    diff = get_staged_diff()
    if diff is None:
        click.echo("💡 Looks like there's nothing staged yet. Try 'git add' first!")
        return

    # Conversation messages for LLM (keeps history across adjustments)
    messages: list = [SystemMessage(COMMIT_MESSAGE_PROMPT.format(diff=diff))]

    # Initial generation
    commit_message = generate_commit_message(diff, messages=messages, model=model)
    if commit_message is None:
        return

    # Append assistant's message so the LLM conversation has history
    messages.append(AIMessage(commit_message))

    # Interactive loop: commit, adjustment, or abort
    while True:
        click.echo("\n📝 Here's what I came up with:")
        click.echo("=" * 60)
        click.echo(commit_message)
        click.echo("=" * 60)

        choice = click.prompt(
            "Choose an action",
            type=click.Choice(["commit", "adjustment", "abort"], case_sensitive=False),
            show_choices=True,
            default="commit",
        ).lower()

        if choice == "commit":
            if perform_git_commit(commit_message):
                click.echo("🎉 All done! Your changes are committed.")
            return
        elif choice == "abort":
            click.echo("👍 No worries, commit cancelled.")
            return
        else:  # adjustment
            # Ask user for feedback via CLI prompt (single-line)
            click.echo("\nPlease provide brief feedback to improve the commit message.")
            click.echo("(Leave empty to cancel and return to options.)")
            feedback_text = click.prompt("Feedback", default="", show_default=False).strip()
            if not feedback_text:
                click.echo("No feedback provided. Returning to options.")
                continue

            # Add the user's feedback as a new user message in the conversation
            user_feedback_message = (
                "The user provided the following feedback for improving the previous commit message:\n"
                + feedback_text
                + "\nPlease produce a revised commit message following Conventional Commits. Return ONLY the commit message text."
            )

            messages.append(HumanMessage(user_feedback_message))

            # Generate a revised commit message using conversation history
            revised = generate_commit_message(diff, messages=messages, model=model)
            if revised is None:
                click.echo("Failed to generate an adjusted commit message. Returning to options.")
                continue

            # Append assistant reply and update current message
            messages.append(AIMessage(revised))
            commit_message = revised
