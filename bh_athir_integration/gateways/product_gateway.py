class ProductGateway:
    def __init__(self, env):
        self.env = env

    def as_product_product(self, record):
        """Normalize mapping target to product.product."""
        if not record:
            return record
        if record._name == 'product.product':
            return record
        if record._name == 'product.template':
            return record.product_variant_id
        return record
