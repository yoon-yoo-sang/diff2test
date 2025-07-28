# diff2test/response_parser.py
import re

from diff2test.logger import logger


def extract_python_code_from_response(ai_response: str) -> str | None:
    """
    Extracts a Python code block from the AI's raw string response.

    It primarily looks for fenced code blocks (e.g., ```python ... ```).
    If no fenced block is found, and the response is not empty and contains no fences,
    it assumes the entire response might be code as a fallback (due to prompts
    asking for "only code").

    Args:
        ai_response: The raw string response from the AI model.

    Returns:
        The extracted Python code as a string, or None if no suitable code is found.
    """
    if not ai_response:
        logger.info("[ResponseParser] Received empty AI response.")
        return None

    # Check for "NO_TEST_NEEDED" keyword first.
    if "NO_TESTS_NEEDED" in ai_response.strip():
        logger.info("[ResponseParser] AI response indicates no tests needed.")
        return "NO_TESTS_NEEDED"

    # Regex to find Python code blocks fenced by triple backticks.
    # - Supports optional language specifiers like 'python' or 'py'.
    # - re.DOTALL allows '.' to match newlines, capturing multiline code blocks.
    # - re.IGNORECASE makes 'python' matching case-insensitive.
    # - (.*?) is a non-greedy capture of the content inside the fences.
    code_block_pattern = re.compile(
        r"```(?:python|py)?\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE
    )

    match = code_block_pattern.search(ai_response)
    extracted_code = None

    if match:
        extracted_code = match.group(1).strip()
        logger.info(
            f"[ResponseParser] Extracted fenced code block (length: {len(extracted_code)})."
        )
        return extracted_code

    # Handle cases where markdown exists but might be empty or non-python
    if "```" in ai_response:
        # If we are here, it means the regex did not match.
        # This could be an empty block like ``` ``` or a non-python block.
        # If it's just an empty block, we should return an empty string.
        # A simple check for content between backticks can be done.
        # This is a bit simplistic but covers the ` ``` ` case.
        content_between_ticks = ai_response.split("```")[1]
        if not content_between_ticks.strip() or content_between_ticks.strip().lower() == "python":
             return ""
        # Otherwise, it might be a different language block, so we return None.
        return None

    # Fallback for no markdown at all
    response_strip = ai_response.strip()
    keywords = ["def ", "import ", "class ", "assert ", "@"]
    if any(kw in response_strip for kw in keywords):
        logger.info(
            "[ResponseParser] No fenced block, but Python keywords found. Assuming entire response is code."
        )
        return response_strip

    logger.info(
        "[ResponseParser] No Python code block found or response format not recognized."
    )
    return None


# --- Example Usage (for testing this module directly) ---
if __name__ == "__main__":
    logger.info("--- Testing Response Parser ---")

    test_cases = [
        {
            "name": "Test 1: With Markdown Block (python specified)",
            "response": """
                Some introductory text from the AI.
            """,
        }
    ]


def test_example_addition():
    assert 1 + 1 == 2


# Another test function
def test_example_subtraction():
    assert 3 - 1 == 2
