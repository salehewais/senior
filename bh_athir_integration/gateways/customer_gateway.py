class CustomerGateway:
    def __init__(self, env):
        self.env = env
        self.Partner = env['res.partner'].sudo()

    def get(self, partner_id):
        return self.Partner.browse(partner_id).exists()
