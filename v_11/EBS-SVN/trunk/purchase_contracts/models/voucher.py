# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from odoo import api, fields, models, exceptions,_

class account_voucher(models.Model):
    """
    To add contract id to account voucher """
    _inherit = 'account.voucher'

    contract_id = fields.Many2one('purchase.contract', 'Contract')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
