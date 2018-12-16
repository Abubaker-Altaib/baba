# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _

class hr_employee_report(osv.osv_memory):
    #_name= "hr.employee.reportt"
    _inherit = "hr.employee.reportt"
    

    def onchange_type(self, cr, uid, ids, report_type):
        return {'value':{} }

    _columns = {
    'worker': fields.boolean('Worker'), 
    'substitution': fields.boolean('Substitution'),  

      }
    """_defaults = {
                    'report_type' : 'employee',
                    'groupby' : 'company',
                            }"""
 
    def print_report(self, cr, uid, ids, context={}):
        data ={'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.common.ntc.report', 'datas': data}


 