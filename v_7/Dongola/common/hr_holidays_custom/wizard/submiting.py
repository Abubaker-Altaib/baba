# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
import time

class submiting_report(osv.osv_memory):
   
    _name = "submiting.report" 
    _columns = {
         'company_id': fields.many2one('res.company','Company', required=True),
         'dep_id': fields.many2one('hr.department','Department', required=True),
         'name_id': fields.many2one('hr.employee','Employee Name', required=True),
         'absence':fields.selection([('mission', 'Mission'),('holiday', 'Holiday'),('training', 'Training')],'Absence Type', required=True),
         'From': fields.date('From', size=8, required=True),
         'to': fields.date('To', size=8, required=True),
         'work':fields.text('Work Assining', size=20 , required=True),
         'montr':fields.text('Work To Be monitoring', size=20 , required=True),
         'guardianship':fields.text('Guardianship', size=20 , required=True),

               }
    _defaults = {

        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'submiting.report', context=c), 
    }

    def check_Date(self, cr, uid, ids, context=None):
        for f in self.browse(cr, uid, ids, context=context):
          if f.From> f.to:
               return False
        return True 
    _constraints = [
        (check_Date, "The Date From must be before the Date To!", []),
    ]

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.holidays',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'submiting',
            'datas': datas,
            }

submiting_report()
 
