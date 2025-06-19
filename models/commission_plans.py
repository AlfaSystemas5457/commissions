# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command
from datetime import date


class CommissionsPlans(models.Model):
    _name = 'commissions.plans'
    _description = 'Plan de comisión'
    _inherit = ['mail.thread']

    name = fields.Char('Plan de comisión', required=True, tracking=True)
    type_commission = fields.Selection(
        [
            ('targets', 'Objetivos'),
            ('achievements', 'Logros'),
        ], string='Tipo de comisión', tracking=True, default='achievements', required=True
    )
    type_sellers = fields.Selection(
        [
            ('seller', 'Vendedor'),
            ('team_seller', 'Equipo de vemtas'),
        ], string='Tipo de vendedor', tracking=True, default='seller', required=True
    )

    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('approved', 'Aprobado'),
            ('done', 'Listo'),
            ('cancel', 'Cancelado'),
        ], string='Estado', required=True, default='draft'
    )

    date_from = fields.Date(
        'Fecha inicial', default=date.today(), required=True, tracking=True)
    date_to = fields.Date('Fecha Final', tracking=True)

    Freq_target = fields.Selection(
        [
            ('monthly', 'Mensual'),
            ('quarterly', 'Trimestral'),
            ('biannual', 'Semestral'),
            ('annually', 'Anualmente'),
        ], string='Frecuencia objetivo', tracking=True, default='quarterly', required=True
    )

    achievement_ids = fields.One2many(
        'commissions.achievements',
        'plan_id',
        default=[Command.create({'achievements_type': 'amount_invoiced'})],
        copy=True,
        string='Logros',
        tracking=True
    )
    sellers_ids = fields.One2many(
        'commissions.sellers',
        'plan_id',
        copy=True,
        string='Vendedores',
        tracking=True,
    )

    def handle_approved(self):
        self.state = 'approved'

    def handle_done(self):
        self.state = 'done'

    def handle_cancel(self):
        self.state = 'cancel'

    def handle_draft(self):
        self.state = 'draft'


class CommissionsAchievements(models.Model):
    _name = 'commissions.achievements'
    _description = 'Logros de comisiones'
    _rec_name = 'display_name'

    plan_id = fields.Many2one(
        'commissions.plans', required=True, ondelete='cascade')
    achievements_type = fields.Selection(
        [
            ('amount_invoiced', "Cantidad facturada"),
            ('amount_sold', "Cantidad vendida"),
            # ('amount_paid', "Cantidad pagada"),
            # ('amount_refunded', "Cantidad reembolsada"),
            # ('amount_credited', "Cantidad acreditada"),
            # ('amount_canceled', "Cantidad cancelada"),
        ], string='Tipo', required=True
    )
    product_id = fields.Many2one('product.product', string='Producto')
    product_category_id = fields.Many2one(
        'product.category', string='Categoria'
    )
    rate = fields.Float('Tasa', digits=(16, 2), required=True)

    display_name = fields.Char(
        compute='_compute_display_name'
    )

    @api.depends('achievements_type', 'product_id', 'product_category_id', 'rate')
    def _compute_display_name(self):
        for record in self:
            type_label = dict(self._fields['achievements_type'].selection).get(
                record.achievements_type, '')
            parts = [type_label]

            if record.product_id:
                parts.append(f"- {record.product_id.name}")
            elif record.product_category_id:
                parts.append(f"- {record.product_category_id.name}")

            parts.append(f"- {record.rate}%")

            record.display_name = ' '.join(parts)


class CommissionsSellers(models.Model):
    _name = 'commissions.sellers'
    _description = 'Vendedores'
    _rec_name = 'seller'

    plan_id = fields.Many2one(
        'commissions.plans', required=True, ondelete='cascade')
    seller = fields.Many2one('res.users', string='Vendedor', required=True)
    date_from = fields.Date(
        'Desde', compute='_compute_date_from', store=True, readonly=False)
    date_to = fields.Date(
        'Hasta', compute='_compute_date_to', store=True, readonly=False)
    other_plans = fields.Many2many(
        'commissions.plans',
        string='Otros planes',
        compute='_compute_other_plans',
        readonly=False
    )

    @api.depends('seller', 'plan_id.date_from', 'plan_id.date_to', 'date_from', 'date_to')
    def _compute_other_plans(self):
        for record in self:
            if not record.seller or not record.plan_id:
                record.other_plans = [Command.clear()]
                continue

            other_plans_sellers = self.search([
                ('seller', '=', record.seller.id),
                ('plan_id.state', 'in', ['draft', 'approved']),
                ('id', '!=', record.id),
            ])

            other_plan_ids = other_plans_sellers.mapped('plan_id.id')
            record.other_plans = [Command.set(other_plan_ids)] if other_plan_ids else [
                Command.clear()]

    @api.depends('plan_id')
    def _compute_date_from(self):
        today = fields.Date.today()
        for user in self:
            if user.date_from:
                return
            if not user.plan_id.date_from:
                return
            user.date_from = max(
                user.plan_id.date_from, today) if user.plan_id.state != 'draft' else user.plan_id.date_from

    @api.depends('plan_id')
    def _compute_date_to(self):
        today = fields.Date.today()
        for user in self:
            if user.date_to:
                return
            if not user.plan_id.date_to:
                return
            user.date_to = max(
                user.plan_id.date_to, today) if user.plan_id.state != 'draft' else user.plan_id.date_to
