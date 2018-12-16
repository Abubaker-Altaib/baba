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
    _name = "cat.wiz"

    _description = "Category Report"

    _columns = {
        'company_id':fields.many2one('res.company','Company',required=True),
	'cat_id':fields.many2many('hr.employee.category',string='Category',required=True),
	
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'cat.wiz', context=c),
    }

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.employee.category',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cat.report',
            'datas': datas,
            }

