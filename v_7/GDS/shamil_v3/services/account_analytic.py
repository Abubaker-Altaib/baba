# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv



class account_analytic_account(osv.Model):
    """Inherits 'account.analytic.account' to add field to indicate that the analytic account is belonging to an project.
    """
    _inherit = 'account.analytic.account'

    _columns = {
        'project': fields.boolean('Project'),
    }


