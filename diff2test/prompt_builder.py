from diff2test.logger import logger
from diff2test.models import DiffInfo

DEFAULT_TEST_FRAMEWORK = "pytest"


def create_test_prompt_for_diff(
    diff_info: DiffInfo, test_framework: str = DEFAULT_TEST_FRAMEWORK
) -> str:
    """
    Creates a prompt for an AI model to generate unit tests based on a code diff.

    Args:
        diff_info: A DiffInfo object containing the file path and diff content.
        test_framework: The testing framework to be used (e.g., "pytest", "unittest").

    Returns:
        A string representing the prompt to be sent to the AI model.
    """

    prompt_lines = [
        f"You are an expert AI programming assistant specializing in Python and the {test_framework} testing framework.",
        "Your task is to generate unit tests for the provided code changes.",
        "If the code changes are not sufficient to write tests, respond with 'NO_TESTS_NEEDED'.",
        "",
        f"The code changes are in the file: `{diff_info.file_path}`",
        "",
        "Please analyze the following diff carefully:",
        "```diff",
        diff_info.diff_content,
        "```",
        "",
        f"Based on these changes, please write concise and effective unit tests using {test_framework}.",
        "The tests should specifically target the modified or newly introduced behavior.",
        f"Follow standard testing conventions and best practices for {test_framework}.",
        "",
        "Instructions for your response:",
        "- Provide only the Python code for the tests.",
        "- Do not include any explanatory text, introductions, or summaries before or after the code block.",
        "- If you need to include comments, place them within the Python code itself (e.g., `# This test checks...`).",
        # Future prompt enhancements could include:
        # "- Consider edge cases related to the changes."
        # "- If applicable, suggest tests for both positive and negative scenarios."
        # "- Ensure tests are independent and can be run (idempotent if possible)."
    ]

    return "\n".join(prompt_lines)


# --- Example Usage (for testing this module directly) ---
if __name__ == "__main__":
    # Create a dummy DiffInfo object for testing
    sample_diff_info = DiffInfo(
        file_path="src/calculator.py",
        diff_content=(
            "--- a/src/calculator.py\n"
            "+++ b/src/calculator.py\n"
            "@@ -5,7 +5,9 @@\n"
            " class Calculator:\n"
            "     def add(self, x: int, y: int) -> int:\n"
            "-        # Simple addition\n"
            "-        return x + y\n"
            "+        # Addition with a type check for safety\n"
            "+        if not (isinstance(x, int) and isinstance(y, int)):\n"
            '+            raise TypeError("Both inputs must be integers.")\n'
            "+        return x + y + 0 # Deliberate minor change for diff\n"
            " \n"
            "     def subtract(self, x: int, y: int) -> int:\n"
        ),
    )

    logger.info("--- Generating Prompt for Pytest ---")
    pytest_prompt = create_test_prompt_for_diff(sample_diff_info)
    logger.info(pytest_prompt)

    # logger.info("\n--- Generating Prompt for Unittest (example) ---")
    # unittest_prompt = create_test_prompt_for_diff(sample_diff_info, test_framework="unittest")
    # logger.info(unittest_prompt)
