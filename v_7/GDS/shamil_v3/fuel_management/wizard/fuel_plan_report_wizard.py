# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time

# fuel plan wizard report for Specific plan

class fuel_plan_report_wizard(osv.osv_memory):

    _name = "fuel.plan.report.wizard"
    _description = "Fuel Plan"

    def _get_months(self, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months
     
    _columns = {
        'month': fields.selection(_get_months,'Month', select=True),
        'year': fields.integer('Year', size=32,),
        'department_id': fields.many2one('hr.department', 'Department'),
    }

    _defaults = {
        'year': int(time.strftime('%Y'))

                }
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        context={
            'user_id':uid,
            #'database_cr': cr,
        }
        datas = {
             'ids': [],
             'model': 'fuel.plan',
             'form': data,
             'context':context
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel.plan.report',
            'datas': datas,
            }
fuel_plan_report_wizard()

# fuel outgoing wizard report for specific month
class fuel_plan_outgoing_report_wizard(osv.osv_memory):

    _name = "fuel.outgoing.report.wizard"
    _description = "All Fuel outgoing"

    def _get_months(self, cr, uid, context):
       """
        To get the plane month.

        @return: print the report
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months
     
    _columns = {
        'month': fields.selection(_get_months,'Month', select=True),
        'year': fields.integer('Year', size=32,),
        'company_id': fields.many2one('res.company','Company',required=True),
        'choose_type':fields.selection([('constant_plan','الخطة الثابتة'),('gen_manager','الاضافى-الادارات العامة')],'Choose Type'),
    }

    _defaults = {
        'year': int(time.strftime('%Y'))

                }
    
    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fuel.plan',
             'form': data,
            }
        if data['choose_type']== 'constant_plan' :
            return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel.outgoing.report',
            'datas': datas,
            }
        '''elif data['choose_type']=='gen_manager' :
           return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'gen.extra.report',
                    'datas':datas,

           }'''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
