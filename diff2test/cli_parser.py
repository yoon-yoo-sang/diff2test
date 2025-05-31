# diff2test/cli_parser.py
import typer
from typing import Optional
# For Annotated:
# from typing import Annotated # For Python 3.9+
from typing_extensions import Annotated # For compatibility with older Python versions (e.g., 3.8). Or use `from typing import Annotated` for Python 3.9+.

from diff2test.git_handler import get_current_changes, get_diff_between_commits
# Import placeholder functions from the library's __init__.py
from . import process_current_changes, process_commit_range
# from .models import AIConfig # AIConfig model can be used later

# Create Typer application
app = typer.Typer(
    name="dtt",
    help="dtt (Diff To Test): AI-powered unit test generator based on Git changes.",
    add_completion=False  # Disable auto-completion (set to True if needed)
)

# Options that can be common to multiple commands.
# Use Typer.Option to set defaults, help text, etc.
# Here, we define them as parameters for each command explicitly.

@app.command(name="current", help="Generates tests for changes from the last commit to the current state.")
def cli_current(
        project_id: Annotated[Optional[str], typer.Option(
            "--project", "-p",
            help="Google Cloud Project ID for Vertex AI.",
            envvar="DTT_PROJECT_ID"  # Also configurable via DTT_PROJECT_ID environment variable
        )] = None,
        region: Annotated[Optional[str], typer.Option(
            "--region", "-r",
            help="Google Cloud Region for Vertex AI models (e.g., us-central1).",
            envvar="DTT_REGION"  # Also configurable via DTT_REGION environment variable
        )] = None,
):
    """
    dtt current: Analyzes changes from the last commit to the current working directory/staging area.
    """
    print(f"CLI: 'current' command invoked.")
    if not project_id or not region:
        print(
            "Vertex AI Project ID and Region are required. "
            "Use --project and --region options or environment variables (DTT_PROJECT_ID, DTT_REGION)."
        )
        # In a real scenario, you might prompt for input here, use default values,
        # or make these options mandatory.
        # For now, we'll proceed, but actual AI calls would fail.
        # Consider adding: raise typer.Exit(code=1)

    print(f"CLI: Project ID: {project_id}, Region: {region}")

    # Call library function
    result_message = process_current_changes(project_id=project_id, region=region)
    print(f"CLI: Task complete. Result:\n{result_message}")
    print(get_current_changes())


@app.command(name="range", help="Generates tests for changes between two specified commits.")
def cli_range(
        commit_a: Annotated[str, typer.Argument(help="The older commit hash or reference to compare.")],
        commit_b: Annotated[str, typer.Argument(help="The newer commit hash or reference (default: HEAD).")] = "HEAD",
        project_id: Annotated[Optional[str], typer.Option(
            "--project", "-p",
            help="Google Cloud Project ID for Vertex AI.",
            envvar="DTT_PROJECT_ID"
        )] = None,
        region: Annotated[Optional[str], typer.Option(
            "--region", "-r",
            help="Google Cloud Region for Vertex AI models (e.g., us-central1).",
            envvar="DTT_REGION"
        )] = None,
):
    """
    dtt range <COMMIT_A> [COMMIT_B]: Analyzes changes between commit_A and commit_B.
    If COMMIT_B is omitted, HEAD will be used.
    """
    print(f"CLI: 'range' command invoked. Range: {commit_a}..{commit_b}")
    if not project_id or not region:
        print(
            "Vertex AI Project ID and Region are required. "
            "Use --project and --region options or environment variables (DTT_PROJECT_ID, DTT_REGION)."
        )
        # Consider adding: raise typer.Exit(code=1)

    print(f"CLI: Project ID: {project_id}, Region: {region}")

    # Call library function
    result_message = process_commit_range(commit_a, commit_b, project_id=project_id, region=region)
    print(f"CLI: Task complete. Result:\n{result_message}")
    print(get_diff_between_commits(commit_a, commit_b))

# Used for testing when running this file directly
# e.g., python -m diff2test.cli_parser current --help
if __name__ == "__main__":
    app()
