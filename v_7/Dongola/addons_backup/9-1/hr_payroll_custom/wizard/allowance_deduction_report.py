# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
#----------------------------------------
#hr_allowance_deduction_report
#----------------------------------------
class hr_allowance_deduction_report(osv.osv_memory):
    _name ='hr.allowance.deduction.report'

    def _get_months(self, cr, uid, context):
        months=[(n,n) for n in range(1,13)]
        return months

    _columns = {
        'company_id': fields.many2many('res.company','hr_report_company_rel','report_id','company_id','Company',required=True),
        'payroll_ids': fields.many2many('hr.salary.scale', 'hr_report_payroll_rel','pay_bonus','pay_id','Salary Scale'),
        'allow_deduct_ids': fields.many2many('hr.allowance.deduction','allow_deduct_rel','report_id','allow_deduct_id', 'Allowances/Deductions'),
        'employee_ids': fields.many2many('hr.employee','report_employee_rel','report_id','employ_id',"Employees"),
        'month' :fields.selection(_get_months,"Month", required= True),
	    'year' :fields.integer("Year", required= True),
        'type':fields.selection([('allow','Allowance'),('deduct','Deductions')],"Type"),
        'by':fields.selection([('allow','Allowances/Deductions'),('employee','Employee')],"By",required=True),
        'pay_sheet':fields.selection([('first', 'First Pay Sheet'), 
                                      ('second', 'Second Pay Sheet')],'Pay Sheet'),
        'in_salary_sheet' : fields.boolean('In Salary Sheet'),
        'display':fields.selection([('detail','Detail'),('total','Total')],"Display" ,required=True),
        'landscape' : fields.boolean('Landscape'),
        'department_cat_id' : fields.many2one('hr.department.cat','Department Category') ,
        'department_ids' : fields.many2many('hr.department' , 'hr_report_deps_rel') ,
    }
    def _get_companies(self, cr, uid, context=None): 
   
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'display':'detail',
        'company_id': _get_companies,
        'in_salary_sheet' :1,
        'by':'allow',
    }

    def on_change_cat(cr , uid , ids ,context=None):
        return {
            'value' : {
                'department_ids' :None ,
                        }
        }

    def _get_child_departments(self , cr , uid , department_id , args=[] ,context=None):
        dep_obj = self.pool.get('hr.department')
        dep_ids = dep_obj.search(cr,uid , [('parent_id' , '=' , department_id)]+args)
        for dep_id in dep_ids :
            dep_ids += self._get_child_departments(cr , uid , dep_id)
        return dep_ids

    def onchange_data(self,cr,uid,ids,company_id,payroll_ids,ttype,in_salary_sheet,pay_sheet):
        domain=value={}
        emp_domain= [('company_id','in',company_id[0][2]),('state','not in',('draft','refuse'))]
        if payroll_ids and payroll_ids[0][2]:
            emp_domain.append(('payroll_id','in',payroll_ids[0][2]))
            value['employee_ids']=[]
        domain['employee_ids']= emp_domain
        
        allow_domain= [('company_id','in',company_id[0][2]+[False]),('in_salary_sheet','=',in_salary_sheet)]
        if ttype:
            allow_domain.append(('name_type','=',ttype))
        if pay_sheet:
           allow_domain.append(('pay_sheet','=',pay_sheet))
        '''if not in_salary_sheet:
			allow_domain += [('allowance_type','=','general'),('allowance_type','!=','in_cycle'),('special','=', False)]'''
        domain['allow_deduct_ids']=allow_domain
        return {'domain':domain}

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]

        employee_obj = self.pool.get('hr.employee')

        if not data['allow_deduct_ids']:
            domain = []
            if data['in_salary_sheet'] :
                domain+=[('in_salary_sheet','=',data['in_salary_sheet'])]
                if data['pay_sheet']:
                    domain+=[('pay_sheet','=',data['pay_sheet'])]
            if not data['in_salary_sheet']:
                domain += [('allowance_type','=','general'),('allowance_type','!=','in_cycle'),('special','=', False)]
            if data['type']:
                domain+=[('name_type','=',data['type'])]
            allow_deduct_ids = self.pool.get('hr.allowance.deduction').search(cr, uid, domain, context=context)
            data['allow_deduct_ids'] = allow_deduct_ids
        
        if not data['employee_ids']:
            #emp_domain= [('company_id','in',data['company_id']),('state','not in',('draft','refuse'))]
            emp_domain= [('company_id','in',data['company_id']),('state','!=','draft')]
            if data['payroll_ids']:
                emp_domain.append(('payroll_id','in',data['payroll_ids']))
            employee_ids = employee_obj.search(cr, uid, emp_domain, context=context)
            data['employee_ids'] = employee_ids

        data['employee_ids'] = employee_obj.browse(cr, uid, data['employee_ids'], context=context)    
        
        data['employee_ids'] = sorted(data['employee_ids'], key=lambda k: (k.degree_id.sequence,k.name_related) )
        data['employee_ids'] = [x.id for x in data['employee_ids'] ]
        
        data['pay_sheet_name'] = ''
        if data['pay_sheet'] == 'second':
            data['pay_sheet_name'] = 'رقم : 2'
        if data['pay_sheet'] == 'first':
            data['pay_sheet_name'] = 'رقم : 1'
        
        data['type_name'] = 'الإستحقاقات\الخصومات'
        if data['type'] == 'allow':
            data['type_name'] = 'اﻹستحقاقات'
        if data['type'] == 'deduct':
            data['type_name'] = 'الإستقطاعات'
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.allowance.deduction.archive',
             'form': data
        }
        dep_cat_id = data.get('department_cat_id' , None)
        if dep_cat_id :
            dep_cat_id = dep_cat_id[0]
            department_ids = data.get('department_ids' , None)
            if not department_ids :
                department_ids = self.pool.get('hr.department').search(cr , uid , [('cat_id' , '=' , dep_cat_id) ])     
            outsite_scale = self.pool.get('hr.department.cat').read(cr , uid ,[dep_cat_id] , ['outsite_scale'] )[0]['outsite_scale'] 
            data.update({'outsite_scale' : outsite_scale})
            if not outsite_scale:
                childe_dep_ids = []
                for department_id in department_ids:
                    dep_ids = [department_id] + self._get_child_departments(cr , uid ,department_id , args=[('cat_id' , '!=' , dep_cat_id)])
                    childe_dep_ids.append(dep_ids)
                data.update({'childe_dep_ids': childe_dep_ids})
        if data['landscape']==True:
            return {
		        'type': 'ir.actions.report.xml',
		        'report_name': 'allowance.deduction.landscape',
		        'datas': datas,
		    }
        else:
            return{
		        'type': 'ir.actions.report.xml',
		        'report_name': 'allowance.deduction',
		        'datas': datas,
		        }
     
