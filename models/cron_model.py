from odoo import models, fields, api


class CommissionsCron(models.Model):
    _name = 'commissions.cron'
    _description = 'Commissions Cron'

    def action_check_plans(self):
        today = fields.Date.today()
        plans = self.env['commissions.plans'].search(
            [('state', 'in', ['approved']),
             ('date_to', '<', today)]
        )
        for plan in plans:
            plan.write({'state': 'done'})
