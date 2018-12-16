# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm

class departments_wizard(osv.osv_memory):
    
    _name ='departments.wizard'


    _columns = {
        'general_dep':fields.boolean('General Departments'),
        'departments_ids': fields.many2many('hr.department','departments_wizard_departments_rel',string='Departments'),
    }

    def onchange_gen_dep(self, cr, uid, ids,general_dep, context={}):
        if general_dep:
            dep_obj = self.pool.get('hr.department')
            dep_cat_obj = self.pool.get('hr.department.cat')
            general_cat_ids = dep_cat_obj.search(cr, uid, [('category_type', '=','general_dep')], context=context)
            #general_ids = dep_obj.search(cr, uid, [('cat_id', 'in', general_cat_ids)], context=context)
            return{
                'domain':{
                    'departments_ids':[('cat_id', 'in', general_cat_ids)]
                }
            }
        return {
                'domain':{
                    'departments_ids':[]
                }
            }

    def print_report(self, cr, uid, ids, context={}):
        
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.department',
             'form': data
             }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'department.pyramidal',
            'datas': datas,
                    }
