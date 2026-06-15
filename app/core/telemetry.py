from fastapi import FastAPI

from app.core.config import Settings


def setup_telemetry(app: FastAPI, settings: Settings) -> None:
    if not settings.otel_enabled:
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {
            SERVICE_NAME: settings.service_name,
            "deployment.environment": settings.environment,
            "service.version": settings.app_version,
        }
    )
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    if settings.otel_exporter_otlp_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint,
            insecure=settings.otel_exporter_otlp_insecure,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

