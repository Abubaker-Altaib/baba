# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _



class ResConfigSettings(models.Model):
    _inherit = 'res.company'

    set_code_auto = fields.Boolean(default=True)
    accounts_code_digits = fields.Integer(string='Number of digits in an account code',default=8)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    set_code_auto = fields.Boolean(related='company_id.set_code_auto')


