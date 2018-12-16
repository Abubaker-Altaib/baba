# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from osv import osv

class exit_permit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(exit_permit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal':self._get_qtytotal
        })
    def _get_qtytotal(self,move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total+=move.product_qty
        return {'quantity':total,'uom':uom}

report_sxw.report_sxw('report.stock.exit_permit.list','stock.picking','addons/stock_report/report/exit_permit.rml',parser=exit_permit)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
