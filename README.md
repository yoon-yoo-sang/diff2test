# diff2test

> AI-Powered Unit Test Generation from Git Diffs

`diff2test` is a command-line tool that intelligently generates unit tests by analyzing differences in your Git repository. It leverages Google's Vertex AI (Gemini models) to understand code changes and suggest relevant test cases, helping you speed up your development workflow and improve test coverage.

---

## Overview

Writing unit tests can be time-consuming. `diff2test` aims to alleviate this by:

- Analyzing code changes between commits or in your current working directory.
- Filtering for relevant source files (e.g., Python files, excluding test files themselves).
- Sending these changes to a powerful AI model (Vertex AI Gemini).
- Parsing the AI's response to extract generated unit test code.
- Providing you with these tests, which you can then review, adapt, and integrate.

Currently, `diff2test` primarily targets Python projects and generates tests in the `pytest` style (this can be expanded in the future).

## Core Features (MVP)

- **Generate tests for current uncommitted changes**: Analyzes the diff between `HEAD` and your current working directory/staging area.
  - Command: `dtt current`
- **Generate tests for a range of commits**: Analyzes the diff between two specified commit hashes or references.
  - Command: `dtt range <commit_a> <commit_b>`
- **Smart Filtering**: Automatically excludes test files (e.g., `test_*.py`) from the diff analysis for test generation.
- **AI-Powered**: Uses Vertex AI (Gemini models) for intelligent test case suggestion.
- **Python First**: Initial focus on Python code and `pytest` conventions.
- **Flexible Output**: Prints generated tests to standard output by default, with an option to save to files.

## How It Works (High-Level)

1.  **CLI Interaction**: You invoke `dtt` with a specific command (e.g., `current` or `range`) and options.
2.  **Git Diff Parsing**: The tool executes `git diff` commands based on your input to retrieve the relevant code changes, filtering for Python source files and excluding test files.
3.  **Prompt Construction**: For each identified code change (diff hunk for a file), a specialized prompt is constructed, instructing the AI on how to generate unit tests.
4.  **Vertex AI API Call**: The prompt, along with the diff, is sent to a configured Vertex AI Gemini model.
5.  **Response Parsing**: The AI's response (which should contain suggested test code) is parsed to extract the clean Python code.
6.  **Output**: The generated test code is then either printed to your console (default) or saved to test files in a specified directory (if an output option is used).

## Prerequisites

- **Python**: Version 3.9 or higher is recommended.
- **Git**: Must be installed and accessible in your system's PATH. Your project must be a Git repository.
- **Google Cloud Account & Vertex AI Setup**: This is crucial for the AI capabilities.

### Vertex AI Setup

To use `diff2test` with its AI features, you need to set up a Google Cloud Project and enable Vertex AI:

1.  **Google Cloud Project**:
    - If you don't have one, create a Google Cloud Project: [Google Cloud Console](https://console.cloud.google.com/).
    - Ensure billing is enabled for your project.
2.  **Enable Vertex AI API**:
    - In the Google Cloud Console, navigate to your project.
    - Go to "APIs & Services" > "Library".
    - Search for "Vertex AI API" and enable it for your project.
3.  **Authentication (Application Default Credentials - ADC)**:
    - Install the Google Cloud CLI (`gcloud`): [Install gcloud CLI](https://cloud.google.com/sdk/docs/install).
    - Authenticate your user account and set up ADC by running:
      ```bash
      gcloud auth application-default login
      ```
      This command will open a browser window for you to log in with your Google account that has access to the configured project.
4.  **Set Project ID and Region**:
    `diff2test` needs to know your Google Cloud Project ID and the region where you want to run Vertex AI operations (where the Gemini models are available, e.g., `us-central1`). You can provide these via:

    - **Command-line options**: `--project <YOUR_PROJECT_ID>` and `--region <YOUR_REGION>`
    - **Environment variables**: Set `DTT_PROJECT_ID` and `DTT_REGION`.

    Example of supported regions for Gemini models: [Vertex AI Model Regions](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#gemini-models) (Check for the specific model you intend to use, e.g., `gemini-2.0-flash-001`).

## Installation

Currently, `diff2test` can be installed from source using Poetry.

1.  Clone the repository:
    ```bash
    git clone https://github.com/yoon-yoo-sang/diff2test
    cd diff2test
    ```
2.  Install dependencies and the tool itself using Poetry:

    ```bash
    poetry install
    ```

    This will create an executable `dtt` within Poetry's virtual environment.

3.  Activate the virtual environment to use the `dtt` command:
    ```bash
    poetry shell
    ```

## Usage

Once installed and your Vertex AI setup is complete, you can use `dtt` from your terminal (within the Poetry shell).

### General Help

```bash
dtt --help
```

### Commands

1. `dtt current`
   Generates tests for changes from the last commit (HEAD) to the current working directory and staging area.

```bash
dtt current --project "your-gcp-project-id" --region "us-central1"
```

Or, using environment variables:

```bash
export DTT_PROJECT_ID="your-gcp-project-id"
export DTT_REGION="us-central1"
dtt current
```

2. `dtt range <COMMIT_A> <COMMIT_B>`
   Generates tests for changes between COMMIT_A (older) and COMMIT_B (newer). COMMIT_B defaults to HEAD if omitted.

```bash
dtt range HEAD~2 HEAD~1 --project "your-gcp-project-id" --region "us-central1"
dtt range my-feature-branch main --project "your-gcp-project-id" --region "us-central1"
```

### Options (for commands like current and range)

- `--project <PROJECT_ID>`, `-p <PROJECT_ID>`: (Required unless DTT_PROJECT_ID env var is set) Your Google Cloud Project ID.
- `--region <REGION>`, `-r <REGION>`: (Required unless DTT_REGION env var is set) The Google Cloud region for Vertex AI.
- `--output-dir <DIRECTORY_PATH>`, `-o <DIRECTORY_PATH>`: (Optional) If provided, saves the generated test files to the specified base directory, mirroring the source structure. Default: prints to standard output.
  Example: `dtt current -p my-proj -r us-central1 -o generated_tests`
- `--interactive`, `-i`: (Planned Feature) Prompts for confirmation before generating tests for each changed file, showing the diff.

### Configuration

- **Vertex AI**: As mentioned, project_id and region must be supplied via CLI options or environment variables (DTT_PROJECT_ID, DTT_REGION).
- **AI Model**: Currently, the AI model (e.g., gemini-2.0-flash-001) might be configured within AIConfig in models.py. This could be exposed as a CLI option in the future.

## Limitations (Current MVP)

- **Python Only**: Primarily supports Python code and pytest conventions.
- **Test Quality**: The quality and relevance of generated tests depend heavily on the AI model's capabilities and the quality of the diff/prompt. Generated tests must be reviewed and potentially modified.
- **No Test Execution**: This tool only generates test code; it does not run the tests.
- **Cost**: Using Vertex AI APIs will incur costs on your Google Cloud bill, based on the amount of input and output tokens processed. Be mindful of this, especially with large diffs or many files. The tool will provide a warning before processing a large number of files if that feature is implemented.
- **Trivial Changes**: While efforts are made to filter out non-testable changes (like comment-only diffs), the AI might still be invoked. The tool aims to handle "NO_TEST_NEEDED" responses from the AI.

## Future Roadmap (Ideas)

- **Enhanced Interactive Mode**: More sophisticated prompts and diff display during interactive file selection.
- **Fine-tuning Support**: Allow users to fine-tune a model with their own codebase and testing conventions for more customized test generation.
- **Advanced Pre-filtering**: Use AST analysis or more complex heuristics to better identify changes that genuinely require new/updated tests.
- **Support for Other Languages & Frameworks**: Extend capabilities beyond Python/pytest.
- **Test File Management**: Smarter ways to handle existing test files (e.g., appending, updating specific test functions).
- **TUI (Text User Interface)**: For a richer interactive experience.
- **IDE Integration**.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.
(Details to be added: e.g., contribution guidelines, code of conduct).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
