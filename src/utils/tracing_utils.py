from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "utils_tracing_utils_py_g239",
    "g_annotation_created": 239,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "A utility for configuring OpenTelemetry tracing.",
    "artifact_type": "UTILITY_MODULE_PYTHON",
    "status_in_lifecycle": "PROPOSED",
    "purpose_statement": "To provide a centralized mechanism for initializing and configuring OpenTelemetry, as per ADR-OS-019.",
    "authors_and_contributors": [{"g_contribution": 239, "identifier": "Roo"}],
    "internal_dependencies": [],
    "external_dependencies": [
        {"name": "opentelemetry-api", "version_constraint": ">=1.6.0,<2.0.0"},
        {"name": "opentelemetry-sdk", "version_constraint": ">=1.6.0,<2.0.0"},
        {"name": "opentelemetry-exporter-otlp-proto-grpc", "version_constraint": ">=1.6.0,<2.0.0"}
    ],
    "linked_issue_ids": ["issue_D6_roadmap"]
  }
}
# ANNOTATION_BLOCK_END

from opentelemetry import trace
import os
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    _HAS_OTLP = True
except Exception:  # pragma: no cover – exporter optional for tests
    _HAS_OTLP = False

from opentelemetry.sdk.trace.export import ConsoleSpanExporter

def configure_tracer(service_name: str):
    """Configures the OpenTelemetry tracer."""
    provider = TracerProvider()

    # Disable remote exporter in test/dev when HAIOS_DISABLE_OTEL is set or OTLP not present.
    if os.environ.get("HAIOS_DISABLE_OTEL", "1") == "1" or not _HAS_OTLP:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    else:
        processor = BatchSpanProcessor(OTLPSpanExporter())
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)