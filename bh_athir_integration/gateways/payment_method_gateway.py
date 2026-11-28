class PaymentMethodGateway:
    def __init__(self, env):
        self.env = env

    def get(self, method_id):
        if 'account.payment.method' not in self.env:
            return self.env['account.payment.method'].browse()
        return self.env['account.payment.method'].browse(method_id).exists()
