# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.osv import osv,fields,orm

class report_12c_move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_12c_move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata
        })
    def _getdata(self,pick):
        res={}
        return res

report_sxw.report_sxw('report.report_12c_move', 'vehicle.move', 'addons/admin_affairs/report/report_12c_move.rml' ,parser=report_12c_move,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        
