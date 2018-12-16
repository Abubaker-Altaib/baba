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
import time
from openerp.report import report_sxw
from openerp.tools import ustr
from openerp.tools.translate import _
from openerp.tools import to_xml

class social_insurrance_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(social_insurrance_webkit, self).__init__(cr, uid, name, context)
        self.localcontext.update({       
            'emps':self.get_employees,
            'total':self.get_total,
        })

    def get_employees(self,data):
        top_res=[]
        comm_total=insu_total=last_total=0
        composed_ids=[]
        self.cr.execute('''select allowance_id as idd from com_allow_deduct_rel where com_allow_deduct_id=(
select id  from hr_allowance_deduction 
where type='complex' and   allowance_type in ('substitution','qualification','family_relation','in_cycle') and  salary_included=True and old_salary_included=True and started_section_included=True  and penalty=True and taxable=True  and special=True and linked_absence=True)''') 
        basic_salary_ids = self.cr.dictfetchall()
        if basic_salary_ids :
            for row in basic_salary_ids:
                composed_ids.append(row['idd'])
        domain=[('scale_id','in',data['scale_ids']),('in_salary_sheet','=',True),('company_id','in',data['company_ids']),('year','=',data['year']),('month','=',data['month'])]
        if data['dept_ids']:
            domain+=[('department_id','in',data['dept_ids'])]
        main_arc_ids=self.pool.get('hr.payroll.main.archive').search(self.cr,self.uid,domain)
        if main_arc_ids:
            main_arc=self.pool.get('hr.payroll.main.archive').browse(self.cr,self.uid,main_arc_ids)
            no=0 
            for rec in main_arc:
                no+=1 
                insurance=self.inner(rec.id,[data['insurance_id'][0]])             
                wage=float(insurance*100)/float(8)
                comm=float(wage * 17)/float(100)
                total=float(wage * 25)/float(100)
                dic={
                     'no':no,
                     'code':rec.code,
                     'name':rec.employee_id.name,
                     'E_date':rec.employee_id.employment_date,
                     'sn':rec.employee_id.otherid,
                     'insu':round(insurance,2),
                     'basic':round((rec.basic_salary+self.inner(rec.id,composed_ids)),2),
                     'wage':round(wage,2),
                     'comm':round(comm,2),
                     'total':round(total,2)
                    }
                comm_total+=comm
                insu_total+=insurance
                last_total+=total
                top_res.append(dic)
            self.total={
                       'comm_total':round(comm_total,2),
                       'insu_total':round(insu_total,2),
                       'last_total':round(last_total,2),
                       }
            return top_res

    def inner(self,main_id,src_ids):
        domain=[('main_arch_id','=',main_id),('allow_deduct_id','in',src_ids)]
        amount=0
        alow_deduc_ids=self.pool.get('hr.allowance.deduction.archive').search(self.cr,self.uid,domain)
        if alow_deduc_ids:
            alow_deduc=self.pool.get('hr.allowance.deduction.archive').browse(self.cr,self.uid,alow_deduc_ids) 
            for rec in alow_deduc: 
                amount+=rec.amount
        return amount
        

    def get_total(self):
         return self.total
  

report_sxw.report_sxw('report.social.insurrance.webkit', 'hr.payroll.main.archive', 'hr_payroll_custom/report/social_insurrance_webkit_report.mako', parser=social_insurrance_webkit, header="False")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
