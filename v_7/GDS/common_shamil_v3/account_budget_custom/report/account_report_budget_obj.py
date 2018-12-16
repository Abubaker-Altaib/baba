# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_budget_object(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_budget_object, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
	        'budget_total':self._budget_total,
        })

    def _budget_total(self,budget):
    	total = {'planned_amount':0.0, 'total_operation':0.0, 'balance':0.0, 'residual_balance':0.0}
    	for line in budget.account_budget_line:
    		total['planned_amount']+=line.planned_amount
    		total['total_operation']+=line.total_operation
    		total['balance']+=line.balance
    		total['residual_balance']+=line.residual_balance
    	return [total]

report_sxw.report_sxw('report.account.account.budget.object', 'account.budget', 'addons/account_budget_custom/report/account_report_budget_obj.rml', parser=account_budget_object, header='custom landscape')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
