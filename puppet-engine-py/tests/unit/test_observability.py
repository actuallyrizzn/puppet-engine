import pytest
from unittest.mock import patch, MagicMock
from src.utils.observability import StructuredLogger, setup_observability

def test_structured_logger():
    logger = StructuredLogger("test_service")
    assert logger.service_name == "test_service"
    assert logger.logger is not None

def test_structured_logger_log():
    logger = StructuredLogger("test_service")
    # Test that logging doesn't raise exceptions
    logger.log("info", "test message", extra_data="value")
    assert True  # If we get here, no exception was raised

@patch('opentelemetry.trace.set_tracer_provider')
@patch('opentelemetry.trace.get_tracer_provider')
@patch('opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument_app')
@patch('opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor.instrument')
def test_setup_observability(mock_httpx, mock_fastapi, mock_get_provider, mock_set_provider):
    mock_app = MagicMock()
    logger = setup_observability(mock_app, "test_service")
    assert logger is not None
    assert isinstance(logger, StructuredLogger)

@patch('opentelemetry.trace.set_tracer_provider')
@patch('opentelemetry.trace.get_tracer_provider')
@patch('opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument_app')
@patch('opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor.instrument')
def test_setup_observability_with_correlation_id(mock_httpx, mock_fastapi, mock_get_provider, mock_set_provider):
    mock_app = MagicMock()
    logger = setup_observability(mock_app, "test_service")
    
    # Test logging with correlation ID
    with patch('opentelemetry.trace.get_current_span') as mock_span:
        mock_span_context = MagicMock()
        mock_span_context.trace_id = "test_trace_id"
        mock_span.return_value.get_span_context.return_value = mock_span_context
        
        logger.log("info", "test message", user_id="123")
        assert True  # If we get here, no exception was raised 