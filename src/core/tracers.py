from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from .config import settings


def configure_tracer() -> None:
    resource = Resource(attributes={'SERVICE_NAME': settings.project_name})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host, agent_port=settings.jaeger_port
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(ConsoleSpanExporter())
    )


instrumentor = FastAPIInstrumentor
