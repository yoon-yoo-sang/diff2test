import typer
from typing import Optional

# For Annotated:
# from typing import Annotated # For Python 3.9+
from typing_extensions import (
    Annotated,
)  # For compatibility with older Python versions (e.g., 3.8). Or use `from typing import Annotated` for Python 3.9+.

from diff2test import process_current_changes, process_commit_range
from diff2test.logger import logger

# Import placeholder functions from the library's __init__.py

# Create Typer application
app = typer.Typer(
    name="dtt",
    help="dtt (Diff To Test): AI-powered unit test generator based on Git changes.",
    add_completion=False,  # Disable auto-completion (set to True if needed)
)

# Options that can be common to multiple commands.
# Use Typer.Option to set defaults, help text, etc.
# Here, we define them as parameters for each command explicitly.


@app.command(
    name="current",
    help="Generates tests for changes from the last commit to the current state.",
)
def cli_current(
    project_id: Annotated[
        Optional[str],
        typer.Option(
            "--project",
            "-p",
            help="Google Cloud Project ID for Vertex AI.",
            envvar="DTT_PROJECT_ID",  # Also configurable via DTT_PROJECT_ID environment variable
        ),
    ] = None,
    region: Annotated[
        Optional[str],
        typer.Option(
            "--region",
            "-r",
            help="Google Cloud Region for Vertex AI models (e.g., us-central1).",
            envvar="DTT_REGION",  # Also configurable via DTT_REGION environment variable
        ),
    ] = None,
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            "--output-dir",
            "-o",
            help="Base directory for saving generated test files.",
        ),
    ] = None,  # Default output directory
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Run in interactive mode (default: False).",
        ),
    ] = False,
    target: Annotated[
        Optional[str],
        typer.Option(
            "--target",
            "-t",
            help="Target file or directory to analyze (default: current working directory).",
        ),
    ] = None,  # Default to current working directory
):
    """
    dtt current: Analyzes changes from the last commit to the current working directory/staging area.
    """
    logger.info(f"CLI: 'current' command invoked.")
    if not project_id or not region:
        logger.info(
            "Vertex AI Project ID and Region are required. "
            "Use --project and --region options or environment variables (DTT_PROJECT_ID, DTT_REGION)."
        )
        # In a real scenario, you might prompt for input here, use default values,
        # or make these options mandatory.
        # For now, we'll proceed, but actual AI calls would fail.
        # Consider adding: raise typer.Exit(code=1)
        return

    logger.info(f"CLI: Project ID: {project_id}, Region: {region}")
    result_message = process_current_changes(
        project_id=project_id,
        region=region,
        output_dir=output_dir,
        interactive=interactive,
        target=target,
    )
    logger.info(f"CLI: Task complete. Result:\n{result_message}")


@app.command(
    name="range", help="Generates tests for changes between two specified commits."
)
def cli_range(
    commit_a: Annotated[
        str, typer.Argument(help="The older commit hash or reference to compare.")
    ],
    commit_b: Annotated[
        str, typer.Argument(help="The newer commit hash or reference (default: HEAD).")
    ] = "HEAD",
    project_id: Annotated[
        Optional[str],
        typer.Option(
            "--project",
            "-p",
            help="Google Cloud Project ID for Vertex AI.",
            envvar="DTT_PROJECT_ID",
        ),
    ] = None,
    region: Annotated[
        Optional[str],
        typer.Option(
            "--region",
            "-r",
            help="Google Cloud Region for Vertex AI models (e.g., us-central1).",
            envvar="DTT_REGION",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            "--output-dir",
            "-o",
            help="Base directory for saving generated test files.",
        ),
    ] = None,  # Default output directory
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Run in interactive mode (default: False).",
        ),
    ] = False,
    target: Annotated[
        Optional[str],
        typer.Option(
            "--target",
            "-t",
            help="Target file or directory to analyze (default: current working directory).",
        ),
    ] = None,  # Default to current working directory
):
    """
    dtt range <COMMIT_A> [COMMIT_B]: Analyzes changes between commit_A and commit_B.
    If COMMIT_B is omitted, HEAD will be used.
    """
    logger.info(f"CLI: 'range' command invoked. Range: {commit_a}..{commit_b}")
    if not project_id or not region:
        logger.info(
            "Vertex AI Project ID and Region are required. "
            "Use --project and --region options or environment variables (DTT_PROJECT_ID, DTT_REGION)."
        )
        # Consider adding: raise typer.Exit(code=1)
        return

    logger.info(f"CLI: Project ID: {project_id}, Region: {region}")
    result_message = process_commit_range(
        commit_a,
        commit_b,
        project_id=project_id,
        region=region,
        output_dir=output_dir,
        interactive=interactive,
        target=target,
    )
    logger.info(f"CLI: Task complete. Result:\n{result_message}")


# Used for testing when running this file directly
# e.g., python -m diff2test.cli_parser current --help
if __name__ == "__main__":
    app()
