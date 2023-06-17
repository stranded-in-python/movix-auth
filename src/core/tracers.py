from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(JaegerExporter(agent_host_name='localhost', agent_port=6831))
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(ConsoleSpanExporter())
    )


instrumentor = FastAPIInstrumentor
