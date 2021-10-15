# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_genco = fields.Boolean(string="Is a GENCO",  )
    customer = fields.Boolean(string="Is a DISCO", )


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    budget_line_count = fields.Integer(string="Budget Lines", compute='get_budget_count', )

    def get_budget_count(self):
        count = self.env['crossovered.budget.lines'].search_count([('crossovered_budget_id', '=', self.id)])
        self.budget_line_count = count
        
    @api.multi
    def open_budget_lines(self):
        return {
            'name': _('budget_lines'),
            'domain': [('id', 'in', crossovered.budget.lines)],
            'view_type': 'form',
            'res_model': 'crossovered.budget.lines',
            'view_id': 'budget_lines_tree',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',

        }
        




# class nbet_custom(models.Model):
#     _name = 'nbet_custom.nbet_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
