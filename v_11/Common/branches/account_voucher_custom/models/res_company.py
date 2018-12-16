# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    double_approval_amount = fields.Float(
        'Double approval amount', default=0.0,
        help="ceiling of expenses order double approve.")
    auto_budget=fields.Boolean('Automatic Budget Check for vouchers.',default=True)
