# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from osv import osv
import pooler

class clearance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(clearance_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
#            'line':self._getdata,
        })
"""    def _getdata(self,clearance_id):
          self.cr.execute(
                	select sum(b.bill_amount) as total_bill

			from purchase_clearance s
			left join purchase_clearance_billing b on (b.clearance_id = s.id)
			where s.id = %s%(clearance_id)) 
          res = self.cr.dictfetchall()
          return res """
report_sxw.report_sxw('report.clearance_report','purchase.clearance','purchase_clearance/report/clearance_report.rml',parser=clearance_report)

