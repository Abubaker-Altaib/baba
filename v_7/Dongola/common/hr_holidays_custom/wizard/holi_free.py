# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time

class holi_free(osv.osv_memory):
    _name = "holi.free"

    _columns = {        
         'comp_id':fields.many2one('res.company', 'Company Name',required=True),
         'department_id':fields.many2many('hr.department','holi_free_dep','holi_free_id', 'holi_free_name','Department Name',domain="[('company_id','=',comp_id)]"),
         'year':fields.integer('Year', required=True),
              
    }

    _defaults = {
        'year': int(time.strftime('%Y')),
        'comp_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'holi.free', context=c), 
		}

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': [],
             'model': 'hr.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'holi.free',
            'datas': datas,
            }
holi_free()

