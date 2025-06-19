# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime


class CommissionSale(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        plans_ids = self.env['commissions.sellers'].search(
            [('seller.id', '=', self.user_id.id),]
        )
        approved_plans = plans_ids.mapped('plan_id').filtered(
            lambda p: p.state == 'approved'
        )

        for plan in approved_plans:
            if plan.date_to and plan.date_to < datetime.today().date():
                plan.write({'state': 'done'})
                continue

            if self.user_id.id not in plan.sellers_ids.seller.ids:
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
                            'commission': sum([data.price_subtotal * achievement.rate for data in product_line]),
                            'plan_ids': plans_ids.ids,
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
                            'commission': sum([data.price_subtotal * achievement.rate for data in product_categ_line]),
                            'plan_ids': plans_ids.ids,
                            'sale_id': self.id
                        }
                    )
                    continue

                self.env['commissions.commissions'].create(
                    {
                        'seller': self.user_id.id,
                        'date': datetime.today(),
                        'commission': self.amount_total * achievement.rate,
                        'plan_ids': plans_ids.ids,
                        'sale_id': self.id
                    }
                )

        return res
