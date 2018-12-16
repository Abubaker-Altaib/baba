# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
import time


class emp_training_list_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(emp_training_list_report, self).__init__(
            cr, 1, name, context=context)
        self.localcontext.update({
            'time': time,
            'lines_out': self._get_lines_out,
            'lines_in': self._get_lines_in
        })

    def _get_lines(self, id, type):
        return [i for i in id if i.training_place == type]

        return []

    def _get_lines_out(self, id):
        return self._get_lines(id, 'outside')

    def _get_lines_in(self, id):
        return self._get_lines(id, 'inside')


report_sxw.report_sxw('report.emp_training_list_report.report', 'hr.employee',
                      'addons/hr_ntc_custom/report/emp_training_list_report.rml', parser=emp_training_list_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
