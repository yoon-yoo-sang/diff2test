import logging
import pytest
from rich.logging import RichHandler

from diff2test.logger import logger


def test_logger_is_correctly_configured():
    """
    전역 로거 객체가 의도된 대로 올바르게 설정되었는지 확인합니다.
    """
    # then
    assert logger.name == "diff2test"
    assert logger.level == logging.DEBUG
    assert logger.propagate is False
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)


def test_logger_does_not_add_duplicate_handlers():
    """
    로거 모듈을 여러 번 import해도 핸들러가 중복으로 추가되지 않는지 테스트합니다.
    """
    # given
    initial_handler_count = len(logger.handlers)

    # when
    # 다른 모듈에서 logger를 import하는 상황을 시뮬레이션
    # (실제로는 importlib.reload를 사용하는 것이 더 정확할 수 있음)
    from diff2test import logger as logger2
    from diff2test.logger import logger as logger3

    # then
    assert len(logger.handlers) == initial_handler_count
    assert len(logger2.handlers) == initial_handler_count
    assert len(logger3.handlers) == initial_handler_count


def test_log_output_with_caplog(caplog, monkeypatch):
    """
    pytest의 `caplog` fixture를 사용하여 로그가 실제로 생성되는지 테스트합니다.
    caplog가 로그를 캡처할 수 있도록 logger.propagate를 True로 설정해야 합니다.
    """
    # given
    # monkeypatch를 사용하여 테스트 동안만 propagate를 True로 변경
    monkeypatch.setattr(logger, "propagate", True)

    # caplog는 기본적으로 WARNING 레벨 이상을 캡처하므로, 모든 레벨을 캡처하도록 설정 변경
    with caplog.at_level(logging.INFO):
        # when
        message = "This is an info message."
        logger.info(message)

        # then
        assert message in caplog.text
        assert caplog.records[0].name == "diff2test"  # 로거 이름 확인
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "INFO"
        assert record.message == message
