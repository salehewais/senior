from django.apps import AppConfig


class ProjectionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projections"

    def ready(self) -> None:
        from projections.domain.versions import order_projection_max_version
        from projections.observability.metrics import register_projection_max_version
        from projections.observability.tracing import configure_tracing

        configure_tracing("reporting-service")
        register_projection_max_version(order_projection_max_version)
