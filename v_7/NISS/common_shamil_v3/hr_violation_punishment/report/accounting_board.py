
from report import report_sxw


class accounting_board(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(accounting_board, self).__init__(cr, uid, name, context)

report_sxw.report_sxw('report.accounting_board', 'hr.employee.violation', 'hr_violation_punishment/report/accounting_board.rml' ,parser=accounting_board,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
