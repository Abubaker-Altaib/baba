# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, exceptions, tools, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(strin="code",required=True)

    _sql_constraints = [
        ('code_name_uniq', 'unique (code,name,company_id)', 'The code,name must be unique per company !')
    ]

    @api.constrains('email')
    def _validate_email(self):
        for partner in self:
            if partner.email and not tools.single_email_re.match(partner.email):
                raise Warning(_("Please enter a valid email address."))
        return True

