# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_fiscalyear_budget_object(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_fiscalyear_budget_object, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'budget_total':self._budget_total,
        })

    def _budget_total(self,budget):
        return [sum([line.planned_amount for line in budget.account_fiscalyear_budget_line])]

report_sxw.report_sxw('report.account.account.fiscalyear.budget.object', 'account.fiscalyear.budget', 'addons/account_budget_custom/report/account_report_fiscalyear_budget_obj.rml', parser=account_fiscalyear_budget_object, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
