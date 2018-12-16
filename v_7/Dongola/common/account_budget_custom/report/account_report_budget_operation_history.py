# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_budget_operation_history(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.account.budget.operation.history.report'

    def __init__(self, cr, uid, name, context=None):
        super(account_budget_operation_history, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'budget_total':self._budget_total,
        })
	self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        return super(account_budget_operation_history, self).set_context(objects, data, ids, report_type=report_type)

    def _budget_total(self,budget):
	total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
	for line in budget.account_budget_line:
		total['planned_amount']+=line.planned_amount
		total['total_operation']+=line.total_operation
		total['balance']+=line.balance
		total['residual_balance']+=line.residual_balance
	return [total]


report_sxw.report_sxw('report.account.account.budget.operation.history.report', 'account.budget.operation.history', 'account_budget_custom/report/account_report_budget_operation_history_report.rml', parser=account_budget_operation_history, header='internal landscape')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
