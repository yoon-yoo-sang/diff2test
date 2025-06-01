# diff2test/response_parser.py
import re


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
        print("[ResponseParser] Received empty AI response.")
        return None

    if ai_response.strip() == "NO_TESTS_NEEDED":
        print("[ResponseParser] AI response indicates no tests needed.")
        return None

    # Regex to find Python code blocks fenced by triple backticks.
    # - Supports optional language specifiers like 'python' or 'py'.
    # - re.DOTALL allows '.' to match newlines, capturing multiline code blocks.
    # - re.IGNORECASE makes 'python' matching case-insensitive.
    # - (.*?) is a non-greedy capture of the content inside the fences.
    code_block_pattern = re.compile(
        r"```(?:python|py)?\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE
    )

    match = code_block_pattern.search(ai_response)

    if match:
        extracted_code = match.group(1).strip()
        print(
            f"[ResponseParser] Extracted fenced code block (length: {len(extracted_code)})."
        )
        return extracted_code
    else:
        # Fallback: If no fenced block is found, and the prompt requested "only code",
        # the entire response might be the code. This is a heuristic.
        # We check if "```" is absent to avoid partial fence matching.
        if "```" not in ai_response and ai_response.strip():
            print(
                "[ResponseParser] No fenced code block found. Assuming entire response is code as a fallback."
            )
            return ai_response.strip()

        print(
            "[ResponseParser] No Python code block found or response format not recognized."
        )
        return None


# --- Example Usage (for testing this module directly) ---
if __name__ == "__main__":
    print("--- Testing Response Parser ---")

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
