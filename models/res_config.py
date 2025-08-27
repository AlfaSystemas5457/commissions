from odoo import models, fields, api


class CommissionsConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    account_expense_id = fields.Many2one(
        'account.account',
        string='Cuenta de gasto',
        required=True)

    account_payable_id = fields.Many2one(
        'account.account',
        string='Cuenta por pagar',
        required=True)

    def get_values(self):
        res = super(CommissionsConfig, self).get_values()
        commissions_params = self.env['ir.config_parameter'].sudo()
        res.update({
            'account_expense_id': self.env['account.account'].search(
                [('code', '=', commissions_params.get_param('commissions.account_expense_id'))], limit=1).id,
            'account_payable_id': self.env['account.account'].search(
                [('code', '=', commissions_params.get_param('commissions.account_payable_id'))], limit=1).id,
        })
        return res

    @api.onchange('account_expense_id', 'account_payable_id')
    def _onchange_account_fields(self):
        commissions_params = self.env['ir.config_parameter'].sudo()
        if self.account_expense_id:
            commissions_params.set_param(
                'commissions.account_expense_id', self.account_expense_id.code)
        if self.account_payable_id:
            commissions_params.set_param(
                'commissions.account_payable_id', self.account_payable_id.code)

    def set_values(self):
        super(CommissionsConfig, self).set_values()
        # Guardar los valores seleccionados en 'ir.config_parameter'
        commissions_params = self.env['ir.config_parameter'].sudo()
        if self.account_expense_id:
            commissions_params.set_param(
                'commissions.account_expense_id', self.account_expense_id.code)
        if self.account_payable_id:
            commissions_params.set_param(
                'commissions.account_payable_id', self.account_payable_id.code)
