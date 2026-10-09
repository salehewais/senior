"""Odoo connector logic that does not import Odoo.

The Odoo module calls these functions inside ``odoo_db`` transactions.
The worker processes started beside Odoo call them for RabbitMQ and HTTP.
"""
