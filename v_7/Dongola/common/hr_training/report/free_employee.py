# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm

class free_employee(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(free_employee, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time , 'emp': self._get_employee , 'dep': self._get_dep, 'manager': self._get_manager ,})
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        	for obj in self.pool.get('hr.employee.training.approved').browse(self.cr, self.uid, ids, self.context):
           		c=obj.line_ids
        		if not c:
        			raise osv.except_osv(_('Error!'), _('You can not print ..This report available only if the course hav employees!'))
        	return super(free_employee, self).set_context(objects, data, ids ,report_type=report_type)

    def _get_employee(self,department_id):
        o = self.pool.get('hr.employee.training')
        cour =o.browse(self.cr, self.uid,self.ids)[0]
        emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('training_employee_id','=',cour.id) ,('department_id','=',department_id.id),('employee_id','!=',department_id.manager_id.id)], context=self.context)
        emp_list = self.pool.get('hr.employee.training.line').browse(self.cr, self.uid, emp_ids, context=self.context)
        return emp_list

    def _get_dep(self,cour):
        top_res =[]
        self.cr.execute('''select distinct dep.parent_id as par  ,tr_dep.department_id  as dep_id  ,pd.name as par_name
            from hr_department as dep,
            hr_department as pd ,
            hr_employee_training_department as tr_dep,
            hr_employee_training as tr
            where 
            dep.parent_id= pd.id and
            dep.parent_id != 0 and
            tr_dep.department_id=dep.id and
            tr_dep.employee_training_id = tr.id and
            tr.type ='hr.approved.course' and
            tr.id=%s'''%cour)
        res = self.cr.dictfetchall()
        #print ">>>>>>>>>>>>>>res>>>>" ,res
        for d in res :
            data_dec={'name': d['par_name'],'par': d['par'],}
            top_res.append(data_dec)
        
        return top_res

    def _get_manager(self,cour,department_id):
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",department_id
        o = self.pool.get('hr.employee.training')
        cour =o.browse(self.cr, self.uid,self.ids)[0]
        emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('training_employee_id','=',cour.id) ,('employee_id.manager','=','True'),('department_id.parent_id','=',department_id) ], context=self.context)
        emp_list = self.pool.get('hr.employee.training.line').browse(self.cr, self.uid, emp_ids, context=self.context)
        return emp_list
report_sxw.report_sxw('report.free.employee','hr.employee.training.approved','addons/hr_training/report/free_employee.rml',parser=free_employee)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

