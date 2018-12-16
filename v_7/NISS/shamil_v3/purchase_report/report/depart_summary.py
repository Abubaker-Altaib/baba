# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Suppliers Evaluation report         ----------------------------------------------------------------------------------------------------------------
class depart_summary(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(depart_summary, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
        date1 = data['form']['Date_from']
        date2 = data['form']['Date_to']
        purchase_type = 'internal'
        self.cr.execute("""
                select
                    min(d.name) as department ,
                    count(po.name) as no ,
                    sum(po.amount_total) as amount
                    
                    
                from purchase_order po
                     left join hr_department d on (po.department_id=d.id)
                     left join ireq_m ir on (po.ir_id=ir.id)

                where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (po.state NOT IN ('cancel')) and ir.purchase_type=%s
                group by
                d.name
                
             """,(date1,date2,purchase_type)) 
        res = self.cr.dictfetchall()

        return res
report_sxw.report_sxw('report.purchase_depart_summary', 'purchase.order', 'addons/purchase_report/report/depart.summary.rml' ,parser=depart_summary ,header=False)
