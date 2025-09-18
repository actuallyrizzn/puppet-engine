import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
try:
    from opentelemetry.sdk.resources import Resource
except Exception:
    Resource = None  # type: ignore
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore
except Exception:
    OTLPSpanExporter = None  # type: ignore
try:
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter  # type: ignore
except Exception:
    ConsoleSpanExporter = None  # type: ignore

try:
    from opentelemetry.instrumentation.motor import MotorInstrumentor
except ImportError:
    MotorInstrumentor = None

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

def setup_observability(
    app: FastAPI,
    service_name: str,
    enable_tracing: bool = False,
    otlp_endpoint: Optional[str] = None,
    enable_console_tracing: bool = False,
):
    # Setup tracing (env-gated)
    if enable_tracing:
        resource = None
        if Resource is not None:
            resource = Resource.create({"service.name": service_name})
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer_provider = trace.get_tracer_provider()

        # Prefer OTLP exporter if endpoint provided and package available
        if otlp_endpoint and OTLPSpanExporter is not None:
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                tracer_provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))
            except Exception:
                pass

        # Fallback to console exporter only if explicitly enabled
        if enable_console_tracing and ConsoleSpanExporter is not None:
            try:
                tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
            except Exception:
                pass

        # Instrument FastAPI and HTTPX
        try:
            FastAPIInstrumentor.instrument_app(app)
        except Exception:
            pass
        try:
            HTTPXClientInstrumentor().instrument()
        except Exception:
            pass

        # Instrument Motor (MongoDB) if available
        if MotorInstrumentor:
            try:
                MotorInstrumentor().instrument()
            except Exception:
                pass

    # Setup structured logging always
    logger = StructuredLogger(service_name)
    return logger