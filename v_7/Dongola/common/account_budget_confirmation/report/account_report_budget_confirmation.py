# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_budget_confirmation(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_budget_confirmation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'residual':self._get_residual,
            '_get_total': self._get_total,
        })
        self.context = context

    def _get_residual(self, budget):
        budget_line_obj = self.pool.get('account.budget.lines')
        budget_line = budget_line_obj.search(self.cr, self.uid, [('analytic_account_id', '=', budget.analytic_account_id.id),
                                                                                       ('general_account_id','=',budget.general_account_id.id), 
                                                                                       ('period_id', '=', budget.period_id.id)], context=self.context)
        return budget_line_obj.browse(self.cr, self.uid, budget_line, context=self.context) or [False]

    def _get_total(self, objects):
        return [reduce(lambda x, y: x+y, [obj.amount for obj in objects])]

report_sxw.report_sxw('report.account.account.budget.confirmation', 'account.budget.confirmation', 'addons/account_budget_confirmation/report/account_report_budget_confirmation.rml', parser=account_budget_confirmation, header=True)

report_sxw.report_sxw('report.account.account.budget.confirmation.list', 'account.budget.confirmation', 'addons/account_budget_confirmation/report/account_report_budget_confirmation_list.rml', parser=account_budget_confirmation, header=True)
