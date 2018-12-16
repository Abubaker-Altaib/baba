# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from account_voucher_wafi.account_account import cancel_vouchers as cancel_vouchers

class account_petty_cash_wizard(osv.osv_memory):
 
    _name = 'account.petty.cash.wizard'

    _description = 'Petty cash'

    _columns = {
        'chart_account_id':fields.many2one('account.account','Chart Of Account' ,required=True),
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        'period_from': fields.many2one('account.period', 'Start Period'),
        'period_to': fields.many2one('account.period', 'End Period'),
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves', required=True),

 
 }
    
 
