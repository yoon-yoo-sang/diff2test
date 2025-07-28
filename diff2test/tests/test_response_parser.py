from diff2test.response_parser import extract_python_code_from_response


def test_extract_code_with_standard_markdown():
    """
    표준 파이썬 마크다운 코드 블록이 있을 때, 코드를 정확히 추출하는지 테스트합니다.
    """
    # given
    response_text = "Here is the test code:\n```python\ndef test_example():\n    assert True\n```\nThis test covers the basic case."
    expected_code = "def test_example():\n    assert True"

    # when
    extracted_code = extract_python_code_from_response(response_text)

    # then
    assert extracted_code == expected_code


def test_extract_code_with_no_markdown_just_code():
    """
    마크다운 없이 코드만 있는 경우, 코드를 그대로 반환하는지 테스트합니다. (이상적으로는 AI가 항상 마크다운을 사용해야 함)
    """
    # given
    response_text = "def test_simple():\n    x = 1\n    assert x == 1"
    
    # when
    extracted_code = extract_python_code_from_response(response_text)
    
    # then
    # 마크다운 없는 코드를 처리하도록 로직이 변경되었으므로,
    # 이제 코드가 그대로 반환되어야 합니다.
    assert extracted_code == response_text


def test_extract_code_with_no_python_code():
    """
    응답에 파이썬 코드가 전혀 없을 때, None을 반환하는지 테스트합니다.
    """
    # given
    response_text = "I am sorry, but I cannot generate a test for this diff."
    
    # when
    extracted_code = extract_python_code_from_response(response_text)
    
    # then
    assert extracted_code is None


def test_extract_code_with_multiple_code_blocks():
    """
    여러 개의 코드 블록이 있을 때, 첫 번째 파이썬 코드 블록만 추출하는지 테스트합니다.
    """
    # given
    response_text = (
        "First, you need this helper function:\n```python\ndef helper():\n    return 1\n```\n"
        "And here is the test:\n```python\ndef test_main():\n    assert helper() == 1\n```"
    )
    expected_code = "def helper():\n    return 1"
    
    # when
    extracted_code = extract_python_code_from_response(response_text)
    
    # then
    assert extracted_code == expected_code


def test_extract_code_with_different_language_markdown():
    """
    'python'이 아닌 다른 언어의 마크다운이 있을 때, 이를 무시하고 None을 반환하는지 테스트합니다.
    """
    # given
    response_text = "Here is some json:\n```json\n{\"key\": \"value\"}\n```\nNo python code here."
    
    # when
    extracted_code = extract_python_code_from_response(response_text)

    # then
    assert extracted_code is None


def test_empty_response_string():
    """
    빈 문자열이 입력되었을 때, None을 반환하는지 테스트합니다.
    """
    # given
    response_text = ""
    
    # when
    extracted_code = extract_python_code_from_response(response_text)

    # then
    assert extracted_code is None


def test_response_with_no_test_needed_keyword():
    """
    AI가 테스트가 필요 없다는 특정 키워드를 반환할 때, 해당 키워드를 그대로 반환하는지 테스트합니다.
    """
    # given
    response_text = "NO_TESTS_NEEDED"
    
    # when
    extracted_code = extract_python_code_from_response(response_text)

    # then
    assert extracted_code == "NO_TESTS_NEEDED"


def test_response_with_just_backticks():
    """
    마크다운은 있지만 내용이 비어있는 경우, 빈 문자열을 반환하는지 테스트합니다.
    """
    # given
    response_text = "```python\n```"
    expected_code = ""

    # when
    extracted_code = extract_python_code_from_response(response_text)

    # then
    assert extracted_code == expected_code 