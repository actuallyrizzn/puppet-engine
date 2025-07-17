import logging
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.motor import MotorInstrumentor

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "%(name)s", "message": %(message)s}'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log(self, level: str, message: str, **kwargs):
        extra = {**kwargs}
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra)

def setup_observability(app: FastAPI, service_name: str):
    # Setup tracing
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    # Instrument HTTPX
    HTTPXClientInstrumentor().instrument()
    # Instrument Motor (MongoDB)
    MotorInstrumentor().instrument()
    # Setup structured logging
    logger = StructuredLogger(service_name)
    return logger 