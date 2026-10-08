"""Roles live on the account row. Callers do not get to choose them."""

from enum import StrEnum


class Role(StrEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"
