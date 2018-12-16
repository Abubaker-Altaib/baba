# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _



class ResConfigSettings(models.Model):
    _inherit = 'res.company'

    account_code_size = fields.Integer(default=8)
    set_code_auto = fields.Boolean()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_code_size = fields.Integer(related='company_id.account_code_size')
    set_code_auto = fields.Boolean(related='company_id.set_code_auto')


