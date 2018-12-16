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

class account_voucher_line(models.Model):
    """
    To add contract id to account voucher line """
    _inherit = 'account.voucher.line'

  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
