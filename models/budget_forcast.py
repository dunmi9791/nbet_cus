from odoo import fields, models, api


class BudgetForecast(models.Model):
    _name = 'budget.forecast'
    _description = 'Budget forecast table'

    budget_line = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Budget_line',
        required=False)
    budget_id = fields.Many2one(comodel_name='crossovered.budget', string="Budget")
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency")
    company_id = fields.Many2one('res.company', string='Branch', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
    planned_amount = fields.Monetary(
        'Budgeted Amount', required=True,
        )
    january = fields.Monetary(
        'January', required=False,
        )
    february = fields.Monetary(
        'February', required=False,
        )
    march = fields.Monetary(
        'March', required=False,
        )
    april = fields.Monetary(
        'April', required=False,
        )
    may = fields.Monetary(
        'May', required=False,
        )
    june = fields.Monetary(
        'june', required=False,
        )
    july = fields.Monetary(
        'July', required=False,
        )
    august = fields.Monetary(
        'August', required=False,
        )
    september = fields.Monetary(
        'September', required=False,
        )
    october = fields.Monetary(
        'October', required=False,
        )
    november = fields.Monetary(
        'November', required=False,
        )
    december = fields.Monetary(
        'December', required=False,
        )

    @api.one
    @api.depends('company_id')
    def _compute_currency(self):
        self.currency_id = self.company_id.currency_id or self.env.user.company_id.currency_id
