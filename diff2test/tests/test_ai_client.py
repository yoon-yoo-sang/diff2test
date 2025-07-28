from unittest import mock
from unittest.mock import patch, MagicMock

import pytest
from google.api_core import exceptions as google_exceptions

from diff2test.ai_client import generate_text_from_prompt, _initialize_vertex_ai, _vertex_ai_initialized_configs
from diff2test.models import AIConfig


@patch("diff2test.ai_client.vertexai.init")
def test_init_vertex_ai_calls_sdk_init(mock_vertex_init):
    """
    init_vertex_ai 함수가 주어진 설정값으로 Vertex AI SDK의 초기화 함수를 올바르게 호출하는지 테스트합니다.
    """
    # given
    project_id = "my-test-project"
    region = "my-test-region"

    ai_config = AIConfig(
        project_id=project_id,
        region=region,
    )

    # when
    _initialize_vertex_ai(ai_config)

    # then
    mock_vertex_init.assert_called_once_with(project=project_id, location=region)


@patch("diff2test.ai_client.GenerativeModel")
@patch("diff2test.ai_client.vertexai.init")
def test_generate_text_from_prompt_successful(
    mock_vertex_init, mock_generative_model
):
    """
    generate_text_from_prompt 함수가 성공적으로 AI 모델의 응답 텍스트를 반환하는지 테스트합니다.
    """
    # given
    prompt = "Generate a test for this diff."
    ai_config = AIConfig(
        project_id="p1", region="r1", model_name="gemini-test"
    )
    expected_text = "Here is your generated test."

    # Mock the model and its response
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = expected_text
    mock_model_instance.generate_content.return_value = mock_response
    mock_generative_model.return_value = mock_model_instance

    # when
    result_text = generate_text_from_prompt(prompt, ai_config)

    # then
    mock_vertex_init.assert_called_once_with(
        project=ai_config.project_id, location=ai_config.region
    )
    mock_generative_model.assert_called_once_with(ai_config.model_name)
    mock_model_instance.generate_content.assert_called_once_with(
        prompt,
        generation_config=mock.ANY,
        safety_settings=mock.ANY,
    )
    assert result_text == expected_text


@patch("diff2test.ai_client.GenerativeModel")
@patch("diff2test.ai_client.vertexai.init")
def test_generate_text_from_prompt_api_error(
    mock_vertex_init, mock_generative_model
):
    """
    AI 모델 API 호출 중 Google API 에러가 발생했을 때,
    에러를 로깅하고 None을 반환하는지 테스트합니다.
    """
    # given
    prompt = "A prompt that causes an error."
    ai_config = AIConfig(project_id="p1", region="r1")

    # Mock the model to raise an exception
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.side_effect = (
        google_exceptions.InternalServerError("Internal API error")
    )
    mock_generative_model.return_value = mock_model_instance

    # when
    result_text = generate_text_from_prompt(prompt, ai_config)

    # then
    assert result_text is None


@patch("diff2test.ai_client.vertexai.init", side_effect=ValueError("SDK init failed"))
def test_init_vertex_ai_fails(mock_vertex_init):
    """
    Vertex AI SDK 초기화에 실패했을 때, init_vertex_ai가 예외를 다시 발생시키는지 테스트합니다.
    """
    # given
    # 다른 테스트의 영향으로 이미 초기화되었을 수 있으므로, 테스트 전에 초기화 상태를 클리어합니다.
    _vertex_ai_initialized_configs.clear()
    ai_config = AIConfig(project_id="p1", region="r1")

    # when & then
    # init_vertex_ai는 예외를 잡아서 로깅하고 다시 발생시키므로,
    # pytest.raises로 예외 발생을 확인합니다.
    with pytest.raises(ValueError, match="SDK init failed"):
        _initialize_vertex_ai(ai_config)


@patch("diff2test.ai_client.GenerativeModel")
@patch("diff2test.ai_client.vertexai.init")
def test_generate_text_from_empty_prompt(mock_vertex_init, mock_generative_model):
    """
    빈 프롬프트가 주어졌을 때, API 호출 없이 None을 반환하는지 테스트합니다.
    """
    # given
    prompt = ""
    ai_config = AIConfig(project_id="p1", region="r1")

    # when
    result = generate_text_from_prompt(prompt, ai_config)

    # then
    assert result is None
    mock_generative_model.return_value.generate_content.assert_not_called() 