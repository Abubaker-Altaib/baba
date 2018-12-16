# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import pooler
from report import report_sxw


class account_report(report_sxw.rml_parse):
    
    _name = 'report.account.report'

    def __init__(self, cr, uid, name, context=None):
        super(account_report, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'lines': self._get_lines,
            'get_header': self._get_header,
        })

    def _get_header(self, report):
        return [dict([('name','البيــان')]+[(l.sequence,l.name) for l in report.template_id.column_ids])]
        
    def _get_lines(self, report):
        self.pool = pooler.get_pool(self.cr.dbname)
        report_line_pool = self.pool.get('account.balance.reporting.line')             
        total = {'name':'الإجمـــالي'}
        lines = []
        for i in set([l.account_id.id for l in report.line_ids]):            
            row = {}
            report_line_ids = report_line_pool.search(self.cr, self.uid, [('report_id','=',report.id),('account_id','=',i)], context=self.context)
            report_lines = report_line_pool.browse(self.cr, self.uid, report_line_ids,  context=self.context)            
            for l in report_lines:
                    index = l.template_line_id.disclosure_number
                    val = l.previous_value+l.current_value
                    row.update({'name': l.template_line_id.detail_account_ids and l.template_line_id.detail_account_ids[0].name or '/',index:val})
                    total.update({index:total.get(index,0)+val}) 
            lines.append(row)
        lines.append(total)
        return lines


report_sxw.report_sxw('report.account.report', 'account.balance.reporting', 'addons/account_balance_reporting/report/account_report.rml', parser=account_report,header=False)

report_sxw.report_sxw('report.account.report4', 'account.balance.reporting', 'addons/account_balance_reporting/report/account_report4.rml', parser=account_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
