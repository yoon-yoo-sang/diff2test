from typing import List, Optional

from diff2test.ai_client import generate_text_from_prompt
from diff2test.file_writer import save_test_code_to_file
from diff2test.git_handler import get_current_changes, get_diff_between_commits
from diff2test.logger import logger
from diff2test.models import AIConfig, DiffInfo
from diff2test.prompt_builder import create_test_prompt_for_diff
from diff2test.response_parser import extract_python_code_from_response


__all__ = [
    "process_current_changes",
    "process_commit_range",
]


def process_current_changes(
    project_id: str | None,
    region: str | None,
    output_dir: Optional[str] = None,
    interactive: bool = False,
    target: Optional[str] = None,
):
    """
    Generates tests for changes from the last commit to the current state (simulation).
    """
    logger.info(f"[Library] Processing current changes...")
    logger.info(f"[Library] Using Vertex AI Project ID: {project_id}, Region: {region}")
    diff_infos = get_current_changes(target=target)
    _process_diff_infos(project_id, region, diff_infos, output_dir, interactive)


def process_commit_range(
    commit_a: str,
    commit_b: str,
    project_id: str | None,
    region: str | None,
    output_dir: Optional[str] = None,
    interactive: bool = False,
    target: Optional[str] = None,
):
    """
    Generates tests for changes between two commits (simulation).
    """
    logger.info(f"[Library] Processing changes between {commit_a} and {commit_b}...")
    logger.info(f"[Library] Using Vertex AI Project ID: {project_id}, Region: {region}")
    diff_infos = get_diff_between_commits(commit_a, commit_b, target=target)
    _process_diff_infos(project_id, region, diff_infos, output_dir, interactive)


def _process_diff_infos(
    project_id: str,
    region: str,
    diff_infos: List[DiffInfo],
    output_dir: str | None = None,
    interactive: bool = False,
):
    """
    Processes a list of DiffInfo objects and generates test code for each diff.
    This is a utility function that can be used internally or by other modules.
    """
    ai_config = AIConfig(
        project_id=project_id,
        region=region,
        model_name="gemini-2.0-flash-001",  # Default model, can be changed
    )
    orchestrate_test_generation(
        diff_infos, ai_config, output_dir=output_dir, interactive=interactive
    )


def orchestrate_test_generation(
    diff_infos: List[DiffInfo],
    ai_config: AIConfig,
    output_dir: Optional[str],
    interactive: bool = False,
):
    processed_files_count = 0
    saved_file_paths = []

    for i, diff_info in enumerate(diff_infos):
        logger.info(
            f"\n--- Processing file {i + 1}/{len(diff_infos)}: {diff_info.file_path} ---"
        )

        if interactive:
            logger.info("\nDiff content:")
            logger.info("--------------------------------------------------")
            logger.info(diff_info.diff_content)
            logger.info("--------------------------------------------------")

            while True:
                choice = input(
                    "Generate unit tests for this file? (y/N/q)uit: "
                ).lower()
                if choice in ["y", "n", "q", ""]:
                    if choice == "":
                        choice = "n"
                    break
                logger.info("Invalid input. Please enter 'y', 'n', or 'q'.")

            if choice == "n":
                logger.info(f"Skipping test generation for {diff_info.file_path}")
                continue
            elif choice == "q":
                logger.info("Operation aborted by user.")
                break

        prompt = create_test_prompt_for_diff(diff_info)
        raw_ai_text = generate_text_from_prompt(prompt, ai_config)
        generated_code = None
        if raw_ai_text:
            generated_code = extract_python_code_from_response(raw_ai_text)

        if generated_code:
            processed_files_count += 1
            if output_dir:
                saved_path = save_test_code_to_file(
                    diff_info.file_path, generated_code, output_dir
                )
                if saved_path:
                    saved_file_paths.append(saved_path)
            else:
                logger.info(f"\n# Suggested tests for: {diff_info.file_path}")
                logger.info("# --------------------------------------------------")
                logger.info(generated_code)
                logger.info("# --------------------------------------------------\n")
        else:
            logger.info(f"No test code could be generated for: {diff_info.file_path}")

    if output_dir:
        logger.info(
            f"\nProcessed {processed_files_count} files. Tests saved to '{output_dir}'."
        )
    else:
        logger.info(f"\nProcessed {processed_files_count} files.")
