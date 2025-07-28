from diff2test.models import DiffInfo
from diff2test.prompt_builder import create_test_prompt_for_diff


def test_create_test_prompt_for_diff():
    """
    주어진 DiffInfo 객체를 사용하여 완전하고 정확한 프롬프트를 생성하는지 테스트합니다.
    """
    # given
    diff_info = DiffInfo(
        file_path="src/calculator.py",
        diff_content=(
            "@@ -1,3 +1,4 @@\n"
            " def add(a, b):\n"
            "-    return a + b\n"
            "+    # A simple addition function\n"
            "+    return a + b\n"
        ),
    )

    # when
    prompt = create_test_prompt_for_diff(diff_info)

    # then
    # 프롬프트에 필수 요소들이 모두 포함되어 있는지 확인
    assert f"You are an expert AI programming assistant specializing in Python and the pytest testing framework." in prompt
    assert f"The code changes are in the file: `{diff_info.file_path}`" in prompt
    assert "Please analyze the following diff carefully:" in prompt
    assert diff_info.diff_content in prompt
    assert "Instructions for your response:" in prompt
    assert "- Provide only the Python code for the tests." in prompt


def test_prompt_with_empty_diff_content():
    """
    diff 내용이 비어있는 DiffInfo 객체가 주어졌을 때도 프롬프트를 올바르게 생성하는지 테스트합니다.
    (실제 시나리오에서는 이런 경우가 드물지만, 함수의 안정성을 확인하는 차원)
    """
    # given
    diff_info = DiffInfo(
        file_path="src/empty_file.py",
        diff_content="",
    )

    # when
    prompt = create_test_prompt_for_diff(diff_info)

    # then
    assert f"The code changes are in the file: `{diff_info.file_path}`" in prompt
    assert "```diff\n\n```" in prompt  # Empty diff content
    assert "Instructions for your response:" in prompt 