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

class qual_wiz(osv.osv_memory):
    """ To manage category reports """
    _name = "qual.wiz"

    _description = "Qualifications Report"

    _columns = {
        'cat_id':fields.many2one('hr.qualification','Qualifications Category',required=True),
	'qual_id':fields.many2many('hr.qualification',string='Employees Qualifications',required=True),
    }

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.employee.qualification',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'qual.report',
            'datas': datas,
            }

