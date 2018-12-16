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

class training_wiz(osv.osv_memory):
    """ To manage category reports """
    _name = "training.wiz"

    _columns = {
    'partner_id':fields.many2one('res.partner', 'Trainer', domain=[('trainer','=',True)]),
	'report_type':fields.selection([('maselhi', 'Training Almeselhi'),('attract', 'Attract The Technical Assistance'),('limited', 'Limited Of Training Needs'),('total','Total Of Training Approved'),('file','Training File')], 'Report Type', required=True),
	'start_date':fields.date(string='Start Date'),
	'end_date':fields.date(string='End Date'),
	'year':fields.integer('Year', required=True),
	'emp':fields.many2many('hr.employee',string='Employees'),
	'salary':fields.many2one('hr.salary.scale',string='Salary Scale')
	
    }
    _defaults = {
        'report_type' : 'maselhi',
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
             'model': 'hr.employee.training',
             'form': data,
            }
        if datas['form']['report_type'] == 'file':
            return {'type': 'ir.actions.report.xml','report_name': 'training.report.file','datas': datas,}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'training.report',
            'datas': datas,
            }

