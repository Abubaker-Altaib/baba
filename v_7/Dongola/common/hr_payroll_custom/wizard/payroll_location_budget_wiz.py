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

class cat_locate_wiz(osv.osv_memory):
    """ To manage category reports """
    _name = "payroll.location.budget.wiz"

    _description = "Payroll Budget Report"

    def _get_months(self, cr, uid, context):
        months=[(n,str(n)) for n in range(1,13)]
        return months
        
    _columns = {
        'month' :fields.selection(_get_months,"Month", required= True),
	'year' :fields.integer("Year", required= True),
        'type':fields.selection([('location','By Locations'),('department','By Department')],"Type"),
        'in_salary_sheet' : fields.boolean('In Salary Sheet'),
        'company_id' : fields.many2one('res.company','Company') ,
        'department_ids' : fields.many2many('hr.department' , 'hr_report_custom_location_deps_rel', 'report_id','dep_id', string="locations") ,
    }

    def _get_companies(self, cr, uid, context=None):

        return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'company_id': _get_companies,
        'in_salary_sheet': 1,
    }

    def on_change_company_id(self,cr , uid , ids ,company_id,types,context=None):
        department_obj = self.pool.get('hr.department')
        company_obj = self.pool.get('res.company')
        cat_ids = self.pool.get('hr.department.cat').search(cr , uid , [])
        #for rec in self.browse(cr, uid, ids, context=context):
        #    types=rec.type
        #    raise osv.except_osv(_('Error'), _('The  %s  Already Computed')
        #                            % (rec))
        if types == 'location':
           cat_ids = self.pool.get('hr.department.cat').search(cr , uid , [('outsite_scale' , '=' , True)])
        elif types == 'department':
             cat_ids = self.pool.get('hr.department.cat').search(cr , uid , [('outsite_scale' , '=' , False)])
        #dep_ids = department_obj.search(cr, uid, [('type','=','location')])
        com_ids = company_obj.search(cr, uid,[])

        vals = {}
        domain = {}
        domain['company_ids'] = [('id','in',com_ids)]
        domain['department_ids'] = [('cat_id','in',cat_ids)]
        vals['company_ids'] = False
        vals['department_ids'] = False
        if company_id:
            domain['company_ids'] = [('parent_id','=',company_id)]
            domain['department_ids'] = ['|','|',('company_id','=',company_id),('company_id','child_of',[company_id]),
                                           ('company_id.child_ids','child_of',[company_id]),('cat_id','in',cat_ids)]
            

        return {'value' : vals, 'domain': domain}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        context['rules'] = True
        data = self.read(cr, uid, ids, context=context)[0]
        rec = self.browse(cr, uid, ids[0], context=context)

        employee_obj = self.pool.get('hr.employee')
        department_obj = self.pool.get('hr.department')
        company_obj = self.pool.get('res.company')
        cat_ids = self.pool.get('hr.department.cat').search(cr, uid, [], context=context)

        data['company_name'] = rec.company_id and rec.company_id.name or False
        data['pay_sheet_name'] = ''
        data['type_name'] = 'الإستحقاقات\الخصومات'
        data['type_name'] = 'الإستحقاقات\الخصومات بالمواقع'
        data['type'] = 'location'
        if not rec.department_ids:
            domain = [('cat_id', 'in', cat_ids)]
            if rec.company_id:
                domain.append(('company_id', '=', rec.company_id.id))
            data['department_ids'] = department_obj.search(cr, uid, domain, context=context)

        datas = {
            'ids': context.get('active_ids', []),
            'model': 'hr.allowance.deduction.archive',
            'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.location.budget.report2',
            'datas': datas,
            }

