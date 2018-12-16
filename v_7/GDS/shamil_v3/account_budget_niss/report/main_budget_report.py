# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
from tools.translate import _
from report import report_sxw

class report_main_budget(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_main_budget, self).__init__(cr, uid, name, context)
        self.context = context
        self.localcontext.update({
            'get_lines':self.get_lines,
        })

        self.context = context
    '''def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('account.voucher').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'posted':
		            raise osv.except_osv(_('Error!'), _('You can not print this voucher, Please validated it first')) 
            if obj.journal_id.type != 'sale':
		        raise osv.except_osv(_('Error!'), _('You can not print this report from this form, Please choose another report')) 
        return super(report_cash_reciept, self).set_context(objects, data, ids, report_type=report_type) '''
   
    def get_lines(self, budget):
        result = []
        for line in budget.line_ids:
            res = {'name': line.name, 'planned_amount': line.plannet_amount, 'actual_amount': line.actual_amount}
            result.append(res)
        return result

report_sxw.report_sxw('report.account.budget.niss.main.report', 'account.budget.niss', 'addons/account_budget_niss/report/main_budget_report.rml', parser=report_main_budget,header='external' )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
