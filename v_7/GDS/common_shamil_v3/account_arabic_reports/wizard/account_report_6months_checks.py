# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_6months_checks(osv.osv_memory):
    _inherit = "account.common.journal.report"
    _name = 'account.6months.checks.arabic'
    _description = 'Six Months Checks'

    _columns = {
        'sort_selection': fields.selection([('date', 'Date'),
                                            ('ref', 'Bank'), ],
                                            'Entries Sorted By', required=True),
    }
    _defaults = {
        'sort_selection': 'date',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_6months_checks, self)._print_report(cr, uid, ids, data, context=context)
        data = res['datas']
        data['form'].update(self.read(cr, uid, ids, ['sort_selection'])[0])
        res.update({'report_name': 'account.6months.checks.arabic', 'datas': data})
        return res
#        return {'type': 'ir.actions.report.xml', 'report_name': 'account.6months.checks.arabic', 'datas': data}

account_6months_checks()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
