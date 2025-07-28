# diff2test/ai_client.py
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)
from google.api_core import exceptions as google_exceptions  # For specific API errors

from diff2test.logger import logger
from .models import AIConfig  # Assuming AIConfig is in models.py

# It's generally good practice to initialize Vertex AI once if possible,
# but initializing it per call (if project/location might change or for simplicity)
# is also fine as vertexai.init is idempotent for the same params.
_vertex_ai_initialized_configs = set()


def generate_text_from_prompt(prompt: str, ai_config: AIConfig) -> str | None:
    """
    Sends a prompt to the specified Vertex AI Gemini model and returns the text response.

    Args:
        prompt: The prompt string to send to the model.
        ai_config: An AIConfig object with project_id, region, and model_name.

    Returns:
        The text response from the model, or None if an error occurs.
    """
    if not prompt:
        logger.info("[AIClient] Prompt is empty. Skipping API call.")
        return None

    try:
        _initialize_vertex_ai(ai_config)  # Ensure Vertex AI is initialized
    except Exception as e:
        # Initialization already prints an error, so we just return None here
        # or re-raise if a critical failure should halt the program
        logger.info(f"[AIClient] Halting due to Vertex AI initialization failure: {e}")
        return None

    logger.info(f"[AIClient] Attempting to load model: {ai_config.model_name}")
    try:
        model = GenerativeModel(ai_config.model_name)
        logger.info(f"[AIClient] Model '{ai_config.model_name}' loaded.")
    except Exception as e:
        logger.info(f"[AIClient] Error loading model '{ai_config.model_name}': {e}")
        return None

    # Configure safety settings to be less restrictive for code generation if needed.
    # Be mindful of responsible AI practices. For this example, we'll set a common threshold.
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    # Generation Config (Optional, but can be useful)
    generation_config = GenerationConfig(
        temperature=0.2,  # Lower temperature for more deterministic/less creative code
        max_output_tokens=2048,  # Adjust as needed for test code length
        # top_p=0.9,
        # top_k=40
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
            # stream=False # Set to True if you want to stream the response
        )

        # Accessing the text:
        # The exact way to get text can vary slightly. `response.text` is often the simplest.
        # If `response.text` is not available or empty, try candidates.
        if hasattr(response, "text") and response.text:
            return response.text
        elif response.candidates and response.candidates[0].content.parts:
            # Concatenate all text parts if there are multiple
            return "".join(
                part.text
                for part in response.candidates[0].content.parts
                if hasattr(part, "text")
            )
        else:
            logger.info(
                "[AIClient] No text content found in the model's response or unexpected structure."
            )
            logger.info(f"[AIClient] Full response object: {response}")
            return None

    except google_exceptions.PermissionDenied as e:
        logger.info(
            f"[AIClient] Permission Denied for Vertex AI. Ensure API is enabled and credentials are correct: {e}"
        )
    except google_exceptions.NotFound as e:
        logger.info(
            f"[AIClient] Model or resource not found. Check model name and region: {e}"
        )
    except google_exceptions.ResourceExhausted as e:
        logger.info(f"[AIClient] Vertex AI resource quota exhausted: {e}")
    except google_exceptions.InvalidArgument as e:
        logger.info(
            f"[AIClient] Invalid argument to Vertex AI API (check prompt, model, or safety settings): {e}"
        )
    except Exception as e:
        logger.info(
            f"[AIClient] An unexpected error occurred while communicating with Vertex AI: {e}"
        )

    return None


def _initialize_vertex_ai(ai_config: AIConfig):
    """
    Initializes Vertex AI SDK if not already done for the given config.
    """
    config_tuple = (ai_config.project_id, ai_config.region)
    if config_tuple not in _vertex_ai_initialized_configs:
        try:
            logger.info(
                f"[AIClient] Initializing Vertex AI for project: {ai_config.project_id}, region: {ai_config.region}"
            )
            vertexai.init(project=ai_config.project_id, location=ai_config.region)
            _vertex_ai_initialized_configs.add(config_tuple)
            logger.info(f"[AIClient] Vertex AI initialized successfully.")
        except Exception as e:
            logger.info(f"[AIClient] Critical error initializing Vertex AI: {e}")
            # Depending on the application, you might want to raise this
            # or handle it in a way that subsequent calls will also fail clearly.
            raise  # Re-raise for now, so the caller knows init failed.


# --- Example Usage (for testing this module directly) ---
if __name__ == "__main__":
    # IMPORTANT: Replace with your actual Project ID and a region where your chosen model is available.
    # Ensure you've run `gcloud auth application-default login`
    test_ai_config = AIConfig(
        project_id="YOUR_GCP_PROJECT_ID",  # <--- REPLACE THIS
        region="us-central1",  # <--- REPLACE THIS (if needed for your model)
        model_name="gemini-2.0-flash-001",
    )

    # Ensure the configuration has valid values before running
    if "YOUR_GCP_PROJECT_ID" in test_ai_config.project_id:
        logger.info(
            "Please replace 'YOUR_GCP_PROJECT_ID' in the test_ai_config with your actual GCP Project ID."
        )
    else:
        logger.info(
            f"\n--- Testing AI Client with config: Project={test_ai_config.project_id}, Region={test_ai_config.region}, Model={test_ai_config.model_name} ---"
        )

        simple_prompt = "What is pytest in Python? Explain in one short sentence."
        logger.info(f"\nTest 1: Simple explanation prompt: '{simple_prompt}'")
        response_text = generate_text_from_prompt(simple_prompt, test_ai_config)
        if response_text:
            logger.info("\n[AIClient Test] Model Response:")
            logger.info(response_text)
        else:
            logger.info("\n[AIClient Test] Failed to get a response for the simple prompt.")

        logger.info("-" * 20)

        code_prompt = (
            "You are a Python testing expert.\n"
            "Write a simple pytest function to test `def add(a, b): return a + b`.\n"
            "Provide only the Python code for the test."
        )
        logger.info(f"\nTest 2: Code generation prompt: '{code_prompt[:50]}...'")
        code_response_text = generate_text_from_prompt(code_prompt, test_ai_config)
        if code_response_text:
            logger.info("\n[AIClient Test] Model Response (Code):")
            logger.info(code_response_text)
        else:
            logger.info(
                "\n[AIClient Test] Failed to get a response for the code generation prompt."
            )
