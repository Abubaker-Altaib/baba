# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services (<http://www.serpentcs.com>)
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
############################################################################
import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.report.interface import report_rml
from openerp.report.interface import toxml
import mx
from openerp import pooler
import time
from mako.template import Template
from openerp.report import report_sxw
from openerp.tools import ustr
from openerp.tools.translate import _
from openerp.tools import to_xml

class payroll_taxes_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payroll_taxes_webkit, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'allowance': self._taxed_allowance,
            'total': self._get_total,
            'emps': self._emp_tax,
            'dept': self._get_dept,

        })

    def _taxed_allowance(self,data):
        row=[]
        col=[]
        sums=[]
        arc_ids = []
        domain=[('pay_sheet','=','second'),('in_salary_sheet','=',True),('name_type','=','allow')]
        alownce_ids = self.pool.get('hr.allowance.deduction').search(self.cr,self.uid,domain)
        if alownce_ids :
            col.append(u'إجمالي الضرائب')
            if data['process']!='monthly':
                for alw in self.pool.get('hr.allowance.deduction').browse(self.cr,self.uid,alownce_ids) :
                    col.append(alw.name)
                    sums.append(0)
            for elm in [u'الدخل الشخصي',u'اسم الموظف',u'#']:
                col.append(elm) 
            row.append(col)
            domain=[('month','=',data['month']),('in_salary_sheet','=',True),('year','=',data['year'])]
            self.cr.execute(
                '''SELECT pm.id AS id
                FROM hr_payroll_main_archive pm
                LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                LEFT JOIN hr_salary_degree deg on (deg.id= emp.degree_id)
                WHERE pm.month =%s and pm.year =%s and in_salary_sheet = True
                ORDER BY  deg.sequence,emp.name_related''',(data['month'],data['year'],)) 
            res = self.cr.dictfetchall()
            if res:
                for x in res:
                    arc_ids.append(x['id'])
            main_ids = self.pool.get('hr.payroll.main.archive').search(self.cr,self.uid,domain)
            if  arc_ids:
                main_arch=self.pool.get('hr.payroll.main.archive').browse(self.cr,self.uid,arc_ids)
                no=0
                total=0
                for emp in main_arch:
                    if emp.tax >0 or emp.allowances_tax >0 :
                        no+=1
                        col=[]
                        col.append(0)
                        index=0
                        if data['process']!='monthly':
                            for alow_id in alownce_ids:
                                dom=[('main_arch_id','=',emp.id),('allow_deduct_id','=',alow_id)]
                                allow_id=self.pool.get('hr.allowance.deduction.archive').search(self.cr,self.uid,dom)
                                if allow_id:
                                    amount=self.pool.get('hr.allowance.deduction.archive').browse(self.cr,self.uid,allow_id)[0].tax_deducted
                                    col.append(amount or 0)
                                    sums[index]+=amount
                                else:
                                    col.append(0)
                        col.append(emp.tax)
                        total+=emp.tax
                        col[0]=sum(col)
                        col.append(emp.employee_id.name)
                        #col.append(emp.employee_id.emp_code)
                        col.append(no)
                        row.append(col)
                col=[] 
                col.append(sum(sums)+total)
                sums.reverse()
                if data['process']!='monthly':
                    for sm in sums:
                        col.append(sm)
                col.append(total)
                col.append(u'الإجمالي')
                col.append(u'#')
                row.append(col) 
            return row

 
   
    def _get_total(self):
         return self.total 

    def _get_dept(self,data):     
        top_res=[]
        exepmted_ids=self.exepmted_ids=[]
        doamin=[('payroll_id','in',data['scale_ids']),('state','=','approved'),('tax_exempted','=',False),('company_id','in',data['company_ids'])]
        emp_ids=self.pool.get('hr.employee').search(self.cr,self.uid,doamin)
        if emp_ids :
            tax_ids=self.pool.get('hr.tax').search(self.cr,self.uid,[('active','=',True)])
            if tax_ids:
                tax_setting=self.pool.get('hr.tax').browse(self.cr,self.uid,tax_ids)[0]
                for emp in self.pool.get('hr.employee').browse(self.cr,self.uid,emp_ids): 
                    if emp.birthday  and emp.first_employement_date:
                        B_date = mx.DateTime.Parser.DateTimeFromString(emp.birthday)
                        E_date = mx.DateTime.Parser.DateTimeFromString(emp.first_employement_date)
                        diff_birth =( int(data['year'])-int(B_date.year) ) + (float(int(data['month'])-int(B_date.month))/float(365))
                        diff_emp= (int(data['year'])-int(E_date.year) ) + (float(int(data['year'])-int(E_date.month))/float(365))
                        if diff_birth >= tax_setting.taxset_age or diff_emp >= tax_setting.no_years_service :
                            exepmted_ids.append(emp.id)
                if exepmted_ids :
                    self.exepmted_ids=exepmted_ids
                    self.cr.execute('''
SELECT 
 ROW_NUMBER() 
        OVER (ORDER BY hr_department.name) AS no,
  hr_department.name as name, 
  count(hr_employee.id) as count
FROM 
  public.hr_employee, 
  public.hr_department
WHERE 
  hr_department.id = hr_employee.department_id
  AND hr_employee.id in %s
GROUP BY hr_department.name''',(tuple(exepmted_ids,),))
                    res = self.cr.dictfetchall()
                    if res : 
                        for rec in res:                     
                            top_res.append({'department':rec['name'],'count':rec['count'],'no':rec['no']})
                        return top_res

    def _emp_tax(self,data):  
        emp_ids=[]
        if data['process']=='exempted': 
            emp_ids=self.pool.get('hr.employee').search(self.cr,self.uid,[('payroll_id','in',data['scale_ids']),('state','=','approved'),('tax_exempted','=',True),('company_id','in',data['company_ids'])])
        else:
            if self.exepmted_ids :
               emp_ids=self.exepmted_ids
        if emp_ids:
           return self.pool.get('hr.employee').browse(self.cr,self.uid,emp_ids)
report_sxw.report_sxw('report.payroll.taxes.webkit', 'hr.employee', 'hr_payroll_custom/report/payroll_taxes_webkit_report.mako', parser=payroll_taxes_webkit, header="False")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

