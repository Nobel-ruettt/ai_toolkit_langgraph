import click
from dotenv import load_dotenv
from ai_toolkit.model_helper import get_model

from .commands import commit

@click.group()
@click.option(
    "--model",
    "-m",
    default="gpt-4o-mini",
    help="LLM model to use for all commands (e.g., gpt-4o-mini, gpt-4o, claude-sonnet-4-5-20250929 etc.)",
    show_default=True,
)

@click.pass_context
def cli(ctx, model: str):
    """Ai toolbox command group."""
    # Store model in context so subcommands can access it
    ctx.ensure_object(dict)
    ctx.obj["model"] = model


load_dotenv()  # Load credentials from .env

@cli.command()
@click.pass_context
def hello(ctx):
    """Print a hello message from the AI toolbox."""
    model = ctx.obj["model"]

    llm = get_model(model, temperature=0.5)
    response = llm.stream("Generate a friendly hello message from the AI toolbox.")
    for chunk in response:
        click.echo(chunk.content, nl=False)
    click.echo()  # Print newline at the end


# Register the commit command
cli.add_command(commit)

cli.add_command(hello)

if __name__ == "__main__":
    cli()
