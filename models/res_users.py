# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    access_scope_commissions = fields.Selection(
        [
            ('all', 'Mostrar todas las comisiones'),
            ('assigned', 'Solo mostrar comisiones asignadas / propias')
        ], string="Acceso a las comisiones", default='assigned', required=True, store=True
    )

    def _update_groups_based_on_scope(self):
        group_assigned = self.env.ref(
            'commissions.group_commissions_access_assigned', raise_if_not_found=False)
        group_all = self.env.ref(
            'commissions.group_commissions_access_all', raise_if_not_found=False)

        for user in self:
            if not group_assigned or not group_all:
                continue

            # Limpiar grupos
            user.groups_id = user.groups_id - group_assigned - group_all

            # Asignar grupo adecuado
            if user.access_scope_commissions == 'assigned':
                user.groups_id = user.groups_id | group_assigned
            else:
                user.groups_id = user.groups_id | group_all

    def _update_users_access_scope(self):
        users = self.search([])
        for user in users:
            if user.access_scope_commissions == 'assigned':
                user._update_groups_based_on_scope()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'access_scope_commissions' not in vals:
                vals['access_scope_commissions'] = 'assigned'

        users = super().create(vals_list)
        users._update_groups_based_on_scope()
        return users

    def write(self, vals):
        res = super().write(vals)
        if 'access_scope_commissions' in vals:
            self._update_groups_based_on_scope()
        return res
