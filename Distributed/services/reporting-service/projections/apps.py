from django.apps import AppConfig


class ProjectionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projections"

    def ready(self) -> None:
        from projections.tracing import configure_tracing

        configure_tracing("reporting-service")
