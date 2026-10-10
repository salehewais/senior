"""Process entrypoint for the notification consumer."""

from __future__ import annotations

from notification_service.messaging.consumer import main

if __name__ == "__main__":
    main()
