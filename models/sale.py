# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime


class CommissionSale(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        approved_plans = self.env['commissions.plans'].search(
            [('state', 'in', ['approved'])]
        )

        for plan in approved_plans:
            if plan.date_to and plan.date_to < datetime.today().date():
                plan.write({'state': 'done'})
                continue

            if not plan.general_employee and self.user_id.id not in plan.sellers_ids.seller.ids:
                continue

            for achievement in plan.achievement_ids:
                if achievement.achievements_type != 'amount_sold':
                    continue

                if achievement.product_id:
                    product_line = self.order_line.filtered(
                        lambda l: l.product_id == achievement.product_id)

                    self.env['commissions.commissions'].create(
                        {
                            'seller': self.user_id.id,
                            'date': datetime.today(),
                            'commission': sum([achievement.amount if achievement.type_amount == 'fixed' else data.price_subtotal * achievement.amount for data in product_line]),
                            'commission_type': achievement.type_amount,
                            'plan_ids': approved_plans.ids,
                            'sale_id': self.id
                        }
                    )
                    continue

                if achievement.product_category_id:
                    product_categ_line = self.order_line.filtered(
                        lambda l: l.product_id.categ_id == achievement.product_category_id)

                    self.env['commissions.commissions'].create(
                        {
                            'seller': self.user_id.id,
                            'date': datetime.today(),
                            'commission': sum([achievement.amount if achievement.type_amount == 'fixed' else data.price_subtotal * achievement.amount for data in product_categ_line]),
                            'commission_type': achievement.type_amount,
                            'plan_ids': approved_plans.ids,
                            'sale_id': self.id
                        }
                    )
                    continue

                self.env['commissions.commissions'].create(
                    {
                        'seller': self.user_id.id,
                        'date': datetime.today(),
                        'commission': achievement.amount if achievement.type_amount == 'fixed' else self.amount_total * achievement.amount,
                        'commission_type': achievement.type_amount,
                        'plan_ids': approved_plans.ids,
                        'sale_id': self.id
                    }
                )

        return res
