#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from tools.translate import _
from osv import osv,orm
import time

class add_fuel_request(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(add_fuel_request, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        'time':time,
        'datas': self.get_data,
        'get_vhc': self.get_vhc,
        })
        self.context = context

    def get_vhc(self,move_lines):
        lines = []
        for move_line in move_lines:
            for l in move_line.line_id:
                lines.append(l)
        return lines

    def get_data(self,recs):
        return recs


    
        
report_sxw.report_sxw('report.add_fuel_request', 'additional.fuel', 'fuel_management/report/add_fuel_request.rml' ,parser=add_fuel_request ,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

