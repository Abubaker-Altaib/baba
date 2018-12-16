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
            'line':self._get_lines,
            'classification':self._get_classification,
        })
        class_ids = self.pool.get('account.budget.classification').search(cr, uid, [], context=context, order='sequence')
        self.classification = self.pool.get('account.budget.classification').browse(cr, uid, class_ids, context=context)

    def _get_classification(self):
        return self.classification 

    def _get_lines(self, budget, classification):
        line_ids = self.pool.get('account.fiscalyear.budget.lines').search(self.cr, self.uid, [('classification','=',classification),('account_fiscalyear_budget_id','=',budget)])
        total = 0
        res = []
        for fy_line in self.pool.get('account.fiscalyear.budget.lines').browse(self.cr, self.uid, line_ids):
            res.append([fy_line.general_account_id.name,fy_line.planned_amount])
            total+=fy_line.planned_amount
        res.append(['الإجمـــــــــــالي',total])
        return res

    def _budget_total(self,budget):
        return [sum([line.planned_amount for line in budget.account_fiscalyear_budget_line])]

report_sxw.report_sxw('report.account.account.fiscalyear.budget.object', 'account.fiscalyear.budget', 'addons/account_budget_custom/report/account_report_fiscalyear_budget_obj.rml', parser=account_fiscalyear_budget_object, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
