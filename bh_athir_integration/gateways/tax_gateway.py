class TaxGateway:
    def __init__(self, env):
        self.env = env

    def get(self, tax_id):
        return self.env['account.tax'].browse(tax_id).exists()
