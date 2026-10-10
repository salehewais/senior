{
    "name": "Commerce Connector",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Saga commands create the sales order; stock changes publish InventoryUpdated",
    "description": """
OrderConfirmed is recorded and does not create a sales order. CreateErpOrder
does. ReserveInventory and ReleaseInventory are idempotent on the commerce
order id. Stock changes write an InventoryUpdated row into commerce_event_outbox
in the same transaction. Fulfillment buttons call the order service over HTTP.
    """,
    "author": "Commerce learning project",
    "license": "LGPL-3",
    "depends": ["sale_management", "sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/inventory_state_views.xml",
        "views/processed_event_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
