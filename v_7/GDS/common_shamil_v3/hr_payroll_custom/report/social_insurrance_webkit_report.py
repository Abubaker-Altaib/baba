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

from openerp.report import report_sxw

class social_insurrance_webkit(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(social_insurrance_webkit, self).__init__(cr, uid, name, context)
        self.localcontext.update({       
            'emps':self.get_employees,
            'total':self.get_total,
            'user':self._get_user,
        })

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid)

    def get_employees(self,data):
        top_res=[]
        top_res2 = []
        count = 0
        page = 0
        comm_total=insu_total=last_total=0
        exception_obj = self.pool.get('hr.allowance.deduction.exception')
        allowance_salary_obj = self.pool.get('hr.salary.allowance.deduction') 
        allow_ded_obj = self.pool.get('hr.allowance.deduction')
        allow_rec = allow_ded_obj.browse(self.cr,self.uid,data['insurance_id'][0])
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
            self.cr.execute('''select hr_payroll_main_archive.id as id from hr_payroll_main_archive 
            left join hr_employee ON (hr_payroll_main_archive.employee_id = hr_employee.id)
            left join hr_salary_degree deg ON (deg.id= hr_employee.degree_id) 
            where scale_id in %s and in_salary_sheet = True and company_id in %s and year = %s and month = %s and department_id in %s 
            order by  hr_employee.name_related''',
                 (tuple(data['scale_ids']),tuple(data['company_ids']),data['year'],data['month'],tuple(data['dept_ids'])) ) 
        else:
            self.cr.execute('''select hr_payroll_main_archive.id as id from hr_payroll_main_archive 
            left join hr_employee ON (hr_payroll_main_archive.employee_id = hr_employee.id)
            left join hr_salary_degree deg ON (deg.id= hr_employee.degree_id)
             where scale_id in %s and in_salary_sheet = True and company_id in %s and year = %s and month = %s 
             order by  hr_employee.name_related''',
                 (tuple(data['scale_ids']),tuple(data['company_ids']),data['year'],data['month']))

        main_arc_ids_dic = self.cr.dictfetchall()
        #main_arc_ids=self.pool.get('hr.payroll.main.archive').search(self.cr,self.uid,domain)
        if main_arc_ids_dic:
            main_arc_ids = [x['id'] for x in main_arc_ids_dic]
            main_arc=self.pool.get('hr.payroll.main.archive').browse(self.cr,self.uid,main_arc_ids)
            
            no=0 
            for rec in main_arc:
                self.cr.execute('''select id from hr_allowance_deduction_exception where employee_id=%s and
                 allow_deduct_id = %s and ((start_date <= %s and end_date >= %s) or (start_date <= %s and end_date is NULL))''',
                 (rec.employee_id.id,data['insurance_id'][0],rec.salary_date,rec.salary_date,rec.salary_date)) 
                except_id = self.cr.dictfetchall()
                if except_id:
                    continue
                allowance_scale_id = allowance_salary_obj.search(self.cr,self.uid,[('allow_deduct_id','=',data['insurance_id'][0]),
                    ('payroll_id','in',data['scale_ids']),('degree_id','=',rec.employee_id.degree_id.id)])
                allowance_scale_rec = allowance_salary_obj.browse(self.cr,self.uid,allowance_scale_id[0])
                insurance=self.inner(rec.id,[data['insurance_id'][0]])
                if insurance == 0:
                    continue
                no+=1 
                count += 1
                insurance=self.inner(rec.id,[data['insurance_id'][0]])
                if allowance_scale_id:
                    wage = float(insurance*100)/float(allowance_scale_rec.amount)
                    comm = allow_rec.company_load and float(wage * allow_rec.percentage)/float(100) or float(wage * 17)/float(100)
                    total_perc = allow_rec.company_load and (allow_rec.percentage + allowance_scale_rec.amount) or 25
                    total = float(wage * total_perc)/float(100)            
                else:
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
                if (count % 32) == 0.0 and page == 0:
                    page += 1
                    count = 0
                    dic1={
                        'no':'-',
                        'code':'-',
                        'name':u'الإجمالي',
                        'E_date':'-',
                        'sn':'-',
                        'insu':round(insu_total,2),
                        'basic':round((rec.basic_salary+self.inner(rec.id,composed_ids)),2),
                        'wage':'-',
                        'comm':round(comm_total,2),
                        'total':round(last_total,2)
                        }
                    dic2={
                        'no':'-',
                        'code':'-',
                        'name':u'الإجمالي المرحل',
                        'E_date':'-',
                        'sn':'-',
                        'insu':round(insu_total,2),
                        'basic':round((rec.basic_salary+self.inner(rec.id,composed_ids)),2),
                        'wage':'-',
                        'comm':round(comm_total,2),
                        'total':round(last_total,2)
                        }
                    top_res.append(dic1)
                    top_res.append(dic2)
                elif (count % 32) == 0.0 and page != 0:
                    dic1={
                        'no':'-',
                        'code':'-',
                        'name':u'الإجمالي',
                        'E_date':'-',
                        'sn':'-',
                        'insu':round(insu_total,2),
                        'basic':round((rec.basic_salary+self.inner(rec.id,composed_ids)),2),
                        'wage':'-',
                        'comm':round(comm_total,2),
                        'total':round(last_total,2)
                        }
                    dic2={
                        'no':'-',
                        'code':'-',
                        'name':u'الإجمالي المرحل',
                        'E_date':'-',
                        'sn':'-',
                        'insu':round(insu_total,2),
                        'basic':round((rec.basic_salary+self.inner(rec.id,composed_ids)),2),
                        'wage':'-',
                        'comm':round(comm_total,2),
                        'total':round(last_total,2)
                        }
                    top_res.append(dic1)
                    top_res.append(dic2)

                else:
                    pass

            self.total={
                       'comm_total':round(comm_total,2),
                       'insu_total':round(insu_total,2),
                       'last_total':round(last_total,2),
                       }
            if top_res:
                top_res2.append(top_res)
            return top_res2

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
  

report_sxw.report_sxw('report.social.insurrance.webkit', 'hr.payroll.main.archive', 'hr_payroll_custom/report/social_insurrance_webkit_report.mako', parser=social_insurrance_webkit, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
