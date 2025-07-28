import os
from unittest.mock import patch, mock_open, ANY

import pytest
from diff2test.file_writer import save_test_code_to_file


@patch("pathlib.Path.mkdir")
@patch("builtins.open", new_callable=mock_open)
def test_save_test_code_to_file_creates_directory_and_writes_file(
    mock_open_file, mock_mkdir
):
    """
    save_test_code_to_file 함수가 대상 디렉토리를 생성하고,
    예상되는 경로에 정확한 내용을 가진 테스트 파일을 생성하는지 테스트합니다.
    """
    # given
    source_file_path = "src/my_module/main.py"
    generated_code = "def test_main():\n    assert True"
    output_dir = "generated_tests"
    expected_test_file_path = os.path.join(
        output_dir, "src", "my_module", "test_main.py"
    )

    # when
    saved_path = save_test_code_to_file(
        source_file_path, generated_code, output_dir
    )

    # then
    # 1. 디렉토리 생성 확인
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # 2. 파일 쓰기 확인
    # open 함수는 Path 객체를 인자로 받으므로, ANY로 확인합니다.
    mock_open_file.assert_called_once_with(ANY, "w", encoding="utf-8")
    mock_open_file().write.assert_called_once_with(generated_code)

    # 3. 반환된 경로 확인
    # resolve() 때문에 절대 경로가 되므로, endswith로 확인
    assert saved_path.endswith(expected_test_file_path)

@patch("pathlib.Path.mkdir", side_effect=IOError("Permission denied"))
def test_save_fails_on_directory_creation(mock_mkdir):
    """
    디렉토리 생성 중 OS 에러(예: 권한 없음)가 발생했을 때,
    함수가 None을 반환하며 정상적으로 종료되는지 테스트합니다.
    """
    # given
    source_file_path = "src/main.py"
    generated_code = "def test_main(): pass"
    output_dir = "/no_permission"

    # when
    saved_path = save_test_code_to_file(
        source_file_path, generated_code, output_dir
    )

    # then
    assert saved_path is None


@patch("pathlib.Path.mkdir")
@patch("builtins.open", side_effect=IOError("Disk full"))
def test_save_fails_on_file_write(mock_open, mock_mkdir):
    """
    파일 쓰기 중 OS 에러(예: 디스크 꽉 참)가 발생했을 때,
    함수가 None을 반환하며 정상적으로 종료되는지 테스트합니다.
    """
    # given
    source_file_path = "src/main.py"
    generated_code = "def test_main(): pass"
    output_dir = "tests"

    # when
    saved_path = save_test_code_to_file(
        source_file_path, generated_code, output_dir
    )

    # then
    assert saved_path is None 