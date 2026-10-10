from django.core.management.base import BaseCommand

from projections.messaging.consumer import main


class Command(BaseCommand):
    help = "Consume q.reporting.projection into reporting_db. Ack after each projection commit."

    def handle(self, *args, **options) -> None:
        del args, options
        main()
