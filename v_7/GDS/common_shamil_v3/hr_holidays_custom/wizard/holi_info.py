# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time


class holi_info(osv.osv_memory):
    _name = "holi.info"

    
    _columns = {

        
         'dep_id': fields.many2one('hr.department','Department Name' , required=True),
         'year':fields.integer('Year', required=True),
         'holi_type': fields.many2many('hr.holidays.status','holi_info_id','holi_info_type', 'holi_info_name','Holiday Type',required=True),
       
    }
    _defaults = {
        'year': int(time.strftime('%Y')),
		}

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids':  [],
             'model': 'hr.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'holi.info',
            'datas': datas,
            }
    
holi_info()

