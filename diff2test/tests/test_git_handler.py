import subprocess
from unittest.mock import MagicMock, patch

import pytest
from diff2test.git_handler import get_current_changes, get_diff_between_commits
from diff2test.models import DiffInfo


@patch("subprocess.run")
def test_get_current_changes_with_valid_diff(mock_subprocess_run):
    """
    `git diff`가 유효한 변경 사항을 반환할 때, get_current_changes가 DiffInfo 객체 리스트를 올바르게 생성하는지 테스트합니다.
    """
    # given
    mock_diff_output = (
        "diff --git a/sample.py b/sample.py\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "@@ -1,2 +1,3 @@\n"
        "+import os\n"
        " def hello():\n"
        "-    pass\n"
        "+    return 'hello'\n"
    )
    # mock_subprocess_run의 반환 객체 설정
    mock_result = MagicMock()
    mock_result.stdout = mock_diff_output
    mock_result.returncode = 0
    mock_subprocess_run.return_value = mock_result

    # when
    diff_infos = get_current_changes(target=None)

    # then
    assert len(diff_infos) == 1
    assert isinstance(diff_infos[0], DiffInfo)
    assert diff_infos[0].file_path == "sample.py"
    assert "+import os" in diff_infos[0].diff_content
    # git diff HEAD -- **/*.py ':(exclude)**/test_*.py' 를 호출했는지 검증
    mock_subprocess_run.assert_called_with(
        [
            "git",
            "diff",
            "--unified=3",
            "HEAD",
            "--",
            "**/*.py",
            ":(exclude)**/test_*.py",
        ],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )


@patch("subprocess.run")
def test_get_diff_between_commits(mock_subprocess_run):
    """
    두 커밋 사이의 `git diff`가 유효한 변경 사항을 반환할 때, get_diff_between_commits가 DiffInfo 객체 리스트를 올바르게 생성하는지 테스트합니다.
    """
    # given
    mock_diff_output = "diff --git a/another.py b/another.py\n--- a/another.py\n+++ b/another.py\n@@ -1,1 +1,1 @@\n-old line\n+new line\n"
    mock_result = MagicMock()
    mock_result.stdout = mock_diff_output
    mock_result.returncode = 0
    mock_subprocess_run.return_value = mock_result
    commit_a = "HEAD~1"
    commit_b = "HEAD"

    # when
    diff_infos = get_diff_between_commits(commit_a, commit_b, target=None)

    # then
    assert len(diff_infos) == 1
    assert diff_infos[0].file_path == "another.py"
    assert "new line" in diff_infos[0].diff_content
    mock_subprocess_run.assert_called_with(
        [
            "git",
            "diff",
            "--unified=3",
            commit_a,
            commit_b,
            "--",
            "**/*.py",
            ":(exclude)**/test_*.py",
        ],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )


@patch("subprocess.run")
def test_get_current_changes_no_diff(mock_subprocess_run):
    """
    변경 사항이 없을 때, get_current_changes가 빈 리스트를 반환하는지 테스트합니다.
    """
    # given
    mock_result = MagicMock()
    mock_result.stdout = ""  # 변경 내용 없음
    mock_result.returncode = 0
    mock_subprocess_run.return_value = mock_result

    # when
    diff_infos = get_current_changes(target=None)

    # then
    assert len(diff_infos) == 0


@patch("subprocess.run")
def test_git_command_fails(mock_subprocess_run):
    """
    git 명령어 실행이 실패할 때 (예: git 저장소가 아님), CalledProcessError 예외가 발생하는지 테스트합니다.
    """
    # given
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        128, "git diff", stderr="fatal: not a git repository"
    )

    # when / then
    with pytest.raises(subprocess.CalledProcessError):
        get_current_changes(target=None)


@patch("subprocess.run")
def test_diff_parser_excludes_test_files(mock_subprocess_run):
    """
    git diff 명령어가 'test_*.py' 파일을 올바르게 제외하는지 테스트합니다.
    _get_effective_pathspecs 함수가 생성하는 git 인자를 통해 필터링됩니다.
    """
    # given
    # git diff 명령어는 ':(exclude)**/test_*.py' 패턴에 의해
    # test_app.py 파일을 결과에서 제외해야 합니다.
    # 따라서 mock 응답에는 해당 파일의 diff가 포함되지 않아야 합니다.
    mock_diff_output = (
        "diff --git a/src/app.py b/src/app.py\n"
        "--- a/src/app.py\n"
        "+++ b/src/app.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-a\n"
        "+b\n"
    )
    mock_result = MagicMock()
    mock_result.stdout = mock_diff_output
    mock_result.returncode = 0
    mock_subprocess_run.return_value = mock_result

    # when
    diff_infos = get_current_changes(target=None)

    # then
    # _get_effective_pathspecs에 의해 test_app.py는 제외되어야 함
    assert len(diff_infos) == 1
    assert diff_infos[0].file_path == "src/app.py" 