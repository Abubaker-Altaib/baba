# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date,datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _


class hr_alternate_report(osv.osv_memory):
    _name = "hr.alternate.report"

    _description = "alternate report wizard"

    _columns = {
        'start_date':fields.date('Start Date'),
        'alternative_setting_ids':fields.many2many('hr.alternative.setting',string='Categories'),
    }


    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['emp_ids'] = []
        datas = {
             'ids': [],
             'model': 'hr.alternative.process',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'alternate_report.report',
            'datas': datas,
            }
    
    def print_report_emp(self, cr, uid, ids, context=None):
        '''
        when select form employees view
        '''
        data = self.read(cr, uid, ids, [], context=context)[0]
        #data['emp_ids'] = context.get('active_ids', [])
        datas = {
             'ids': [],
             'model': 'hr.alternative.process',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'alternate_report.report',
            'datas': datas,
            }

  