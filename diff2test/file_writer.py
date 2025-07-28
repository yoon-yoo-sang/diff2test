from pathlib import Path

from diff2test.logger import logger


def save_test_code_to_file(
    original_file_path_str: str,
    generated_test_code: str,
    base_output_dir_str: str = "tests",  # Base directory for all test files
) -> str | None:
    """
    Saves the generated test code to a Python file.

    The test file will be named by prepending "test_" to the original file's name.
    It attempts to mirror the original file's directory structure under the base_output_dir.
    For example, if original_file_path is "src/module/component.py" and base_output_dir is "tests",
    the test file will be saved as "tests/src/module/test_component.py".

    Args:
        original_file_path_str: The path string of the original source file.
        generated_test_code: The string content of the test code to save.
        base_output_dir_str: The base directory where test files will be stored.

    Returns:
        The path string of the saved test file, or None if saving failed or test code is empty.
    """
    if not generated_test_code:
        logger.info(
            f"[FileWriter] No test code provided for '{original_file_path_str}'. Skipping file save."
        )
        return None

    original_file_path = Path(original_file_path_str)
    base_output_dir = Path(base_output_dir_str)

    # Construct the test file name (e.g., "test_original_filename.py")
    test_file_name = f"test_{original_file_path.name}"

    # Determine the relative path from the original file's parent to maintain structure
    # e.g., if original is "src/module/component.py", relative_parent_dir is "src/module"
    relative_parent_dir = original_file_path.parent

    # Construct the full output path for the test file
    # e.g., tests/src/module/test_component.py
    test_file_output_path = base_output_dir / relative_parent_dir / test_file_name

    try:
        # Create the directory structure if it doesn't exist
        test_file_output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the test code to the file
        with open(test_file_output_path, "w", encoding="utf-8") as f:
            f.write(generated_test_code)

        saved_path_str = str(test_file_output_path.resolve())
        logger.info(f"[FileWriter] Successfully saved test code to: {saved_path_str}")
        return saved_path_str
    except IOError as e:
        logger.info(f"[FileWriter] Error saving test file '{test_file_output_path}': {e}")
    except Exception as e:  # Catch any other unexpected errors
        logger.info(
            f"[FileWriter] An unexpected error occurred while saving '{test_file_output_path}': {e}"
        )

    return None


# --- Example Usage (for testing this module directly) ---
if __name__ == "__main__":
    logger.info("--- Testing File Writer ---")

    # Dummy data for testing
    dummy_original_file1 = "src/my_module/utils.py"
    dummy_test_code1 = (
        "import pytest\n\n" "def test_something_in_utils():\n" "    assert True\n"
    )

    dummy_original_file2 = "app/main_component.py"
    dummy_test_code2 = (
        "import unittest\n\n"
        "class TestMainComponent(unittest.TestCase):\n"
        "    def test_initialization(self):\n"
        "        self.assertEqual(1, 1)\n"
    )

    dummy_original_file3 = "single_file.py"  # Test file in root of output_dir
    dummy_test_code3 = "assert 1 == 1 # Simple test"

    logger.info(f"\nAttempting to save test for: {dummy_original_file1}")
    path1 = save_test_code_to_file(
        dummy_original_file1, dummy_test_code1, "generated_tests_output"
    )
    if path1:
        logger.info(f"Test 1 saved at: {path1}")
        # You can check the "generated_tests_output" directory in your project

    logger.info(f"\nAttempting to save test for: {dummy_original_file2}")
    path2 = save_test_code_to_file(
        dummy_original_file2, dummy_test_code2, "generated_tests_output"
    )
    if path2:
        logger.info(f"Test 2 saved at: {path2}")

    logger.info(f"\nAttempting to save test for: {dummy_original_file3}")
    path3 = save_test_code_to_file(
        dummy_original_file3, dummy_test_code3, "generated_tests_output"
    )
    if path3:
        logger.info(f"Test 3 saved at: {path3}")

    logger.info(f"\nAttempting to save empty test code:")
    path_empty = save_test_code_to_file(
        "src/another_module.py", "", "generated_tests_output"
    )
    if path_empty is None:
        logger.info("Correctly handled empty test code.")

    logger.info(
        "\nCheck the 'generated_tests_output' directory in your project for the created files."
    )
