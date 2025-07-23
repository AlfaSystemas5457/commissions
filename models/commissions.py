# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class Commissions(models.Model):
    _name = 'commissions.commissions'
    _description = 'Comisión'
    _inherit = ['mail.thread']
    _order = 'date DESC'
    _rec_name = 'display_name'

    uid = fields.Char(
        'UID', required=True, readonly=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'commissions.commissions')
    )
    seller = fields.Many2one(
        'res.users', string='Vendedores', tracking=True, required=True
    )
    date = fields.Datetime('Fecha')
    # target_amount = fields.Float(
    #     'Cantidad objetivo', tracking=True, digits=(16, 2)
    # )
    commission = fields.Float('Comisión', tracking=True, required=True)
    plan_ids = fields.Many2many(
        'commissions.plans', string='Planes', ondelete='restrict', required=True)
    sale_id = fields.Many2one(
        'sale.order', string='Venta', tracking=True)
    invoice_id = fields.Many2one(
        'account.move', string='Factura', tracking=True)

    paid = fields.Boolean('Pagada', default=False, tracking=True)

    display_name = fields.Char(
        compute='_compute_display_name'
    )

    @api.depends('seller', 'date', 'uid')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.uid} - {record.seller.name} - {record.date.strftime("%d/%m/%Y %H:%M:%S")}'

    def handle_paid(self):
        for record in self:
            if record.paid:
                continue

            if not record.commission or record.commission <= 0:
                raise UserError(
                    "La comisión debe tener un valor mayor a cero.")

            # Cuentas contables
            account_commission_expense = self.env['account.account'].search(
                [('code', '=', '601.74.01')], limit=1)
            account_payable = self.env['account.account'].search(
                [('code', '=', '210.01.01')], limit=1)

            if not account_commission_expense or not account_payable:
                raise UserError(
                    "No se encontraron las cuentas contables necesarias.")

            move_vals = {
                'ref': f'Pago de comisión {record.uid}',
                'date': fields.Date.today(),
                'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
                'line_ids': [
                    (0, 0, {
                        'name': 'Gasto por comisión',
                        'account_id': account_commission_expense.id,
                        'debit': record.commission,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': f'Comisión a {record.seller.name}',
                        'account_id': account_payable.id,
                        'debit': 0.0,
                        'credit': record.commission,
                        'partner_id': record.seller.partner_id.id,
                    }),
                ],
            }

            move = self.env['account.move'].create(move_vals)
            move.action_post()  # Asiento contable

            record.paid = True
