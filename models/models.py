# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math


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


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    released_amount = fields.Monetary(
        string='Released Amount',
        required=False)
    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Actual Amount', help="Amount really earned/spent.")
    actual_amount = fields.Monetary(
        compute='_compute_actual_amount', string='Amount Utilised', help="Amount really earned/spent.")
    planned_amount = fields.Monetary(
        'Budgeted Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    percentage = fields.Float(
        compute='_compute_percentage', string='Percentage on Budgeted',
        help="Comparison between practical and planned amount. This measure tells you if you are below or over budget.")
    percentage_released = fields.Float(
        compute='_compute_percentage_released', string='Percentage on Released',
        help="Comparison between practical and released amount. This measure tells you if you are below or over budget.")

    # the percentage field was reworked to compute against the planned amount instead of theoretical

    @api.multi
    def _compute_percentage(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.percentage = float((line.actual_amount or 0.0) / line.planned_amount)
            else:
                line.percentage = 0.00

    @api.multi
    def _compute_percentage_released(self):
        for line in self:
            if line.released_amount != 0.00:
                line.percentage_released = float((line.actual_amount or 0.0) / line.released_amount)
            else:
                line.percentage_released = 0.00

    @api.multi
    @api.onchange('practical_amount')
    def _compute_actual_amount(self):
        for line in self:
            if line.practical_amount:
                line.actual_amount = abs(line.practical_amount)


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    report_type = fields.Selection(
        string='Report Type',
        selection=[('normal', 'Normal'),
                   ('tally', 'T Style'), ],
        default='normal', )




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
