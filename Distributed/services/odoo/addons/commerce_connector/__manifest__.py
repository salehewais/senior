{
    "name": "Commerce Connector",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Apply OrderConfirmed in odoo_db and publish InventoryUpdated",
    "description": """
Confirmed orders arrive from RabbitMQ as OrderConfirmed. This module creates
the customer, the products, and one sales order from that payload. Stock
changes write an InventoryUpdated row into commerce_event_outbox in the same
transaction. Fulfillment buttons call the order service over HTTP.
    """,
    "author": "Commerce learning project",
    "license": "LGPL-3",
    "depends": ["sale_management", "sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/commerce_views.xml",
    ],
    "installable": True,
    "application": False,
}
