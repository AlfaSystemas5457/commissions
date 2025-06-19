# -*- coding: utf-8 -*-

from odoo import models, fields, api


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
    target_amount = fields.Float(
        'Cantidad objetivo', tracking=True, digits=(16, 2)
    )
    commission = fields.Float('Comisión', tracking=True, required=True)
    plan_ids = fields.Many2many(
        'commissions.plans', string='Planes', required=True)
    sale_id = fields.Many2one(
        'sale.order', string='Venta', tracking=True)
    invoice_id = fields.Many2one(
        'account.move', string='Factura', tracking=True)

    display_name = fields.Char(
        compute='_compute_display_name'
    )

    @api.depends('seller', 'date', 'uid')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.uid} - {record.seller.name} - {record.date.strftime("%d/%m/%Y %H:%M:%S")}'
