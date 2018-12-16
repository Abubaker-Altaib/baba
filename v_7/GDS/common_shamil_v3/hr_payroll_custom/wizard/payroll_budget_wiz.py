# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
import time
from datetime import datetime

class cat_wiz(osv.osv_memory):
    """ To manage category reports """
    _name = "payroll.budget.wiz"

    _description = "Payroll Budget Report"

    def get_months(sel, cr, uid, context):
        i=0
        res=[]
        while i<12:
            t=()
            t=(i+1,i+1)
            res.append(t)
            i+=1
        return res
        
    _columns = {
            'company_id':fields.many2one('res.company','Company',required=True),
	    'month':fields.selection(get_months, 'Month', required=True),
	    'year':fields.integer('Year', required=True),
	    'department_ids' : fields.many2many('hr.department.payroll' , 'hr_report_pay_bud_rel', 'report_id','dep_id', string="groups") ,
	
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'payroll.budget.wiz', context=c),
        'month': int(time.strftime('%m')),
        'year': int(time.strftime('%Y')),
    }

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.payroll.main.archive',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.budget',
            'datas': datas,
            }

