# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math
from dateutil import relativedelta
from datetime import datetime
from datetime import date
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_genco = fields.Boolean(string="Is a GENCO",  )
    customer = fields.Boolean(string="Is a DISCO", )
    advance_limit = fields.Monetary('Advance approval limit', )
    company_id = fields.Many2one('res.company', string='', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency")

    @api.one
    @api.depends('company_id')
    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id or self.env.user.company_id.currency_id


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    budget_line_count = fields.Integer(string="Budget Lines", compute='get_budget_count', )
    forecast_lines = fields.One2many(
        comodel_name='budget.forecast',
        inverse_name='budget_id',
        string='Forecast lines',
        required=False)
    forecast_done = fields.Binary(string="Forecast Done",  )

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

    def create_forecast_lines(self):
        if self.forecast_done:
            msg = _('Forecast Lines Already entered')
            raise UserError(msg)
        else:
            for line in self.crossovered_budget_line:
                forecast_line = {
                    'budget_line': line.analytic_account_id.id,
                    'budget_id': self.id,
                    'planned_amount': line.planned_amount,

                }
                record = self.env['budget.forecast']
                record.create(forecast_line)
                # self.forecast_done = True


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    released_amount = fields.Monetary(
        string='Released Amount',compute='_compute_released_amount',
        required=False, store=True )
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

    @api.multi
    @api.depends('analytic_account_id.budget_releases')
    def _compute_released_amount(self):
        for line in self:
            if line.analytic_account_id:
                releases = []
                for release in line.analytic_account_id.budget_releases:
                    releases.append(release.amount)
                    line.released_amount = sum(releases)






class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    report_type = fields.Selection(
        string='Report Type',
        selection=[('normal', 'Normal'),
                   ('tally', 'T Style'), ],
        default='normal', )


class AccountMove(models.Model):
    _inherit = 'account.move'

    attachment = fields.Binary(string="Attached document",  )
    status = fields.Selection(
        string='Effective Status',
        selection=[('not effective', 'Future Effective'),
                   ('due', 'Effective'),  ],
        compute='_compute_status',
        required=False, )

    @api.multi
    def _compute_status(self):
        for rec in self:
            rec.status = "due"
            if date.today() < rec.date:
                rec.status = "not effective"
            elif date.today() == rec.date:
                rec.status = "due"
            elif date.today() > rec.date:
                rec.status = "due"

class AccountAsset(models.Model):
    _inherit = 'account.asset.asset'

    assigned_to = fields.Many2one(
        comodel_name='res.users',
        string='Assigned to',
        required=False, track_visibility=True, trace_visibility='onchange',)
    source_of_fund = fields.Char(
        string='Source of fund',
        required=False, track_visibility=True, trace_visibility='onchange',)
    asset_number = fields.Char(string="Asset Number ",
                       default=lambda self: _('New'),
                       requires=False, readonly=True,)
    tag_number = fields.Char(string="Tag Number", required=False, track_visibility=True, trace_visibility='onchange',)
    location = fields.Many2one(
        comodel_name='location.ebs',
        string='Location',
        required=False, track_visibility=True, trace_visibility='onchange',)
    serial_num = fields.Char(string="Serial Number", required=False, track_visibility=True, trace_visibility='onchange', )
    manufacturer = fields.Char(string="Manufacturer", required=False, track_visibility=True, trace_visibility='onchange',)
    warranty_start = fields.Date(
        string='Warranty Start Date', required=False, track_visibility=True, trace_visibility='onchange',)
    warranty_end = fields.Date(
        string='Warranty End Date', required=False, track_visibility=True, trace_visibility='onchange', )
    model = fields.Char(string="Model", required=False, track_visibility=True, trace_visibility='onchange',)


    @api.model
    def create(self, vals):
        if vals.get('asset_number', _('New')) == _('New'):
            vals['asset_number'] = self.env['ir.sequence'].next_by_code('increment_assets') or _('New')
        result = super(AccountAsset, self).create(vals)
        return result

class LocationEbs(models.Model):
    _name = 'location.ebs'
    _description = 'LocationEbs'

    name = fields.Char(string="Location Name", required=False, track_visibility=True, trace_visibility='onchange',)
    description = fields.Text(
        string="Description",
        required=False)


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
