# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv


class account_budget_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'

    _columns = {
        'group_cash_budget': fields.boolean("Cash Budget Management",
            implied_group='account_budget_custom.group_cash_budget',
            help="""This allows to Manage Cash Budgets."""),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
