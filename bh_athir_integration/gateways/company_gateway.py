class CompanyGateway:
    def __init__(self, env):
        self.env = env

    def browse(self, company_id):
        return self.env['res.company'].browse(company_id).exists()
