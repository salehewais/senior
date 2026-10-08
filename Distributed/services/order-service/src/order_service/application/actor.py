"""Who is calling a use case. Filled from a verified access token, never from the JSON body."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from order_service.domain.roles import Role


@dataclass(frozen=True, slots=True)
class Actor:
    account_id: uuid.UUID
    role: Role
