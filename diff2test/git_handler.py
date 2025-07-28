import glob
import subprocess
from typing import List, Optional
import os

from diff2test.logger import logger
from diff2test.models import DiffInfo


def get_diff_between_commits(commit_a: str, commit_b: str, target: Optional[str]) -> List[DiffInfo]:
    """
    Gets the diff for Python files between two specified commit hashes.
    """
    logger.info(
        f"[GitHandler] Getting diff between {commit_a} and {commit_b} for Python files..."
    )
    git_command_base = ["git", "diff", "--unified=3", commit_a, commit_b]
    
    effective_pathspecs = _get_effective_pathspecs(target)
    git_command = git_command_base
    if effective_pathspecs:
        git_command.extend(["--"] + effective_pathspecs)

    raw_diff = _run_git_command(git_command)
    return _parse_diff_output(raw_diff)


def get_current_changes(target: Optional[str]) -> List[DiffInfo]:
    """
    Gets the diff for Python files from HEAD to the current working directory/staging area.
    This shows all uncommitted changes (staged and unstaged combined) for Python files.
    """
    logger.info(
        f"[GitHandler] Getting current uncommitted changes (HEAD vs. working tree/index) for Python files..."
    )
    git_command_base = ["git", "diff", "--unified=3", "HEAD"]
    
    effective_pathspecs = _get_effective_pathspecs(target)
    git_command = git_command_base
    if effective_pathspecs:
        git_command.extend(["--"] + effective_pathspecs)

    raw_diff = _run_git_command(git_command)
    return _parse_diff_output(raw_diff)


def _run_git_command(command: List[str]) -> str:
    """
    Runs a Git command and returns its standard output.
    Raises CalledProcessError if the command fails.
    """
    try:
        # Ensure the command targets the current working directory explicitly if needed,
        # or rely on the script being run from the repo root.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,  # Raises CalledProcessError for non-zero exit codes
            encoding="utf-8",  # Specify encoding for consistency
        )
        return result.stdout
    except FileNotFoundError:
        # This happens if 'git' command is not found
        logger.info("Error: 'git' command not found. Is Git installed and in your PATH?")
        raise
    except subprocess.CalledProcessError as e:
        logger.info(f"Error executing Git command: {' '.join(command)}")
        logger.info(f"Return code: {e.returncode}")
        logger.info(f"Stderr: {e.stderr.strip()}")
        raise


def _parse_diff_output(raw_diff_output: str) -> List[DiffInfo]:
    """
    Parses the raw output of 'git diff' into a list of DiffInfo objects.
    This parser assumes the unified diff format.
    """
    diffs_info: List[DiffInfo] = []
    if not raw_diff_output.strip():
        return diffs_info

    # Each file's diff in unified format typically starts with "diff --git a/..."
    # We add a newline at the beginning to make the split consistent
    # in case the raw_diff_output doesn't start with one.
    # Then split by this delimiter. The first element of the split will be empty.
    individual_file_diffs = ("\n" + raw_diff_output.strip()).split("\ndiff --git a/")[
        1:
    ]

    for file_diff_section in individual_file_diffs:
        lines = file_diff_section.strip().splitlines()
        if not lines:
            continue

        # The first line of file_diff_section (now lines[0]) is like "old_path b/new_path"
        # We need to reconstruct the full diff header for the content passed to AI
        full_diff_content_for_ai = "diff --git a/" + file_diff_section.strip()

        file_path_a = None
        file_path_b = None

        # Try to find file paths from '--- a/...' and '+++ b/...' lines
        for line_content in lines:
            if line_content.startswith("--- a/"):
                file_path_a = line_content[len("--- a/") :].strip()
            elif line_content.startswith("+++ b/"):
                file_path_b = line_content[len("+++ b/") :].strip()

            # Optimization: if both found relatively early, can break.
            # However, some diffs (e.g. binary) might not have these lines in the same way,
            # but our '*.py' filter should mostly give us text files.
            if file_path_a is not None and file_path_b is not None:
                break

        # Determine the effective file path.
        # For new files, path_a is /dev/null. For deleted files, path_b is /dev/null.
        # We prefer path_b if it's a valid path, otherwise path_a.
        # The '-- '*.py'' filter in the git command itself helps ensure we only get Python files.
        effective_path = None
        if file_path_b and file_path_b != "/dev/null":
            effective_path = file_path_b
        elif file_path_a and file_path_a != "/dev/null":  # Covers deleted files
            effective_path = file_path_a

        if effective_path:  # The '*.py' filter is in the git command, so we assume it's a .py file
            diffs_info.append(
                DiffInfo(
                    file_path=effective_path, diff_content=full_diff_content_for_ai
                )
            )
        # else:
        # Could log if a diff section couldn't be parsed for a file path,
        # but the git filter should prevent non-.py files from appearing.

    return diffs_info


def _get_effective_pathspecs(target: Optional[str]) -> List[str]:
    """
    Constructs pathspecs for git diff.
    If target is provided, patterns apply within that target (AND logic).
    Otherwise, patterns apply globally.
    """
    pathspecs = []

    # General patterns for Python files and excluding test files
    python_files_glob = "**/*.py"  # Recursive from the context
    exclude_tests_glob = "**/test_*.py"  # Recursive from the context, matches test_*.py

    if target:
        clean_target = target.rstrip('/')  # Remove trailing slash for consistency

        # Heuristic: if target itself ends with .py, treat it as a specific file target.
        # Otherwise, treat it as a directory/prefix for other patterns.
        if clean_target.endswith(".py"):
            # Target is a specific Python file.
            # Add the file itself as a pathspec.
            pathspecs.append(clean_target)
            # Add the general exclusion. If clean_target is a test file, it will be excluded by Git.
            pathspecs.append(f":(exclude){exclude_tests_glob}")
        else:
            # Target is a directory or a non-Python file.
            # If clean_target is empty (e.g., target was "/" or just spaces), default to global.
            if not clean_target.strip():  # Check if effectively empty
                pathspecs.append(python_files_glob)
                pathspecs.append(f":(exclude){exclude_tests_glob}")
            else:
                # Target is treated as a directory prefix.
                # Python files within this directory:
                pathspecs.append(f"{clean_target}/{python_files_glob}")
                # Exclude test files within this directory:
                pathspecs.append(f":(exclude){clean_target}/{exclude_tests_glob}")
    else:
        # No target specified, use global recursive patterns.
        pathspecs.append(python_files_glob)
        pathspecs.append(f":(exclude){exclude_tests_glob}")

    return pathspecs


# Example usage (for testing this module directly):
if __name__ == "__main__":
    logger.info("--- Testing Git Handler ---")

    # Before running, make sure you are in a git repository
    # and have some uncommitted changes to Python files for get_current_changes()
    # or valid commit hashes for get_diff_between_commits().

    # Test 1: Current Changes
    logger.info("\nTesting get_current_changes():")
    try:
        current_diffs = get_current_changes()
        if current_diffs:
            for diff_info in current_diffs:
                logger.info(f"\nFile: {diff_info.file_path}")
        else:
            logger.info("No current Python file changes found.")
    except Exception as e:
        logger.info(f"Error in get_current_changes(): {e}")

    # Test 2: Diff between two commits
    # Replace 'COMMIT_A' and 'COMMIT_B' with actual commit hashes from your repository
    # For example, to get diff between HEAD~1 and HEAD:
    # commit_a_hash = "HEAD~1"
    # commit_b_hash = "HEAD"
    # logger.info(f"\nTesting get_diff_between_commits({commit_a_hash}, {commit_b_hash}):")
    # try:
    #     commit_diffs = get_diff_between_commits(commit_a_hash, commit_b_hash)
    #     if commit_diffs:
    #         for diff_info in commit_diffs:
    #             logger.info(f"\nFile: {diff_info.file_path}")
    #             logger.info("Diff Content (first 150 chars):")
    #             logger.info(diff_info.diff_content[:150] + "...")
    #     else:
    #         logger.info(f"No Python file changes found between {commit_a_hash} and {commit_b_hash}.")
    # except Exception as e:
    #     logger.info(f"Error in get_diff_between_commits(): {e}")
    logger.info(
        "\nNote: For 'get_diff_between_commits' test, uncomment and provide valid commit hashes."
    )
