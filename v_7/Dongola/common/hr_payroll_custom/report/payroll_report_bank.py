# -*- coding: utf-8 -*-
import time
from report import report_sxw
import calendar
import datetime
import pooler
import math

class payroll_report_bank(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payroll_report_bank, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getShop,
            'line1':self._total,
            'line9':self._get_bank,
            'user':self._get_user,
            
        })
    globals()['total_net']=0.0

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name

    def _get_bank(self,data):
        bank_name_list = []
        bank_ids_list = []
        bank_ids = []
        if data['bank_id'] :
            bank_name1 = self.pool.get('res.bank').browse(self.cr,self.uid,data['bank_id'])
            bank_name_list += [{'bank_name':x.name} for x in bank_name1]
            bank_id = data['bank_id']
            salary_sheet = data['type'] == '1' and True or False
            allow = data['allow'] and data['allow'][0]
            if salary_sheet:
                self.cr.execute("select distinct b.id as bank_id ,b.name as bank_name from res_bank as b"\
                " left join res_partner_bank r on r.bank = b.id "\
                " left join hr_payroll_main_archive m on m.bank_account_id = r.id "\
                "where month = %s and year= %s and b.id in %s" , (data['month'],data['year'],tuple(bank_id),) )
            if not salary_sheet:
                self.cr.execute("select distinct b.id as bank_id ,b.name as bank_name from res_bank as b"\
                " left join res_partner_bank r on r.bank = b.id "\
                " left join hr_payroll_main_archive m on m.bank_account_id = r.id "\
                "where month = %s and year= %s and b.id in %s"\
                'AND m.salary_date=%s '  , (data['month'],data['year'],tuple(bank_id),data['bonus_date']) )
            bank_ids = self.cr.dictfetchall()
            bank_ids_list += bank_ids and [c['bank_name'] for c in bank_ids] or []
            if  bank_ids and len(bank_ids) != len(data['bank_id']):
              for x in bank_name_list:
                if x['bank_name'] not in bank_ids_list:
                  bank_ids += [x]
            bank_ids = not bank_ids and bank_name_list or bank_ids
        if data['no_bank'] : bank_ids.append({'bank_id' : 0 , 'bank_name' : 'الخزينة' , 'type' : 'cash'})
        return bank_ids

    def _getShop(self,data,bank_id=False):
        salary_scale_obj = self.pool.get('hr.salary.scale')
        allowance_obj = self.pool.get('hr.allowance.deduction')
        globals()['total_net']=0.0
        res_data = {}
        top_result = []
        c= data['form']['company_id']
        payroll_ids = data['form']['payroll_ids'] and data['form']['payroll_ids'] or salary_scale_obj.search(self.cr, self.uid, [])
        bank_id_list = bank_id and self.pool.get('res.partner.bank').search(self.cr,self.uid,[('bank','=',bank_id)])
        salary_sheet = data['form']['type'] == '1' and True or False
        allow = data['form']['allow'] and data['form']['allow'][0]
        '''if not allow:
            allow = allowance_obj.search(self.cr, self.uid, [('in_salary_sheet','=',False)])'''
        bank_ids_str = bank_id != 0 and ",".join(str(i) for i in bank_id_list)
        bank_query = bank_id != 0 and "in (%s)" %(bank_ids_str) or " is null "
        self.cr.execute("select m.employee_id from hr_payroll_main_archive as m "\
                        "where m.bank_account_id "+bank_query+" and month= %s and year = %s and in_salary_sheet = %s" 
                        , (data['form']['month'],data['form']['year'], salary_sheet))
        employees=self.cr.fetchall()
        if employees:
            emp_ids=[]
            for emp in employees:
                if emp[0] not in emp_ids:
                    emp_ids.append(emp[0])
         
        #-------------------------------------------------------------------------------
            

            if salary_sheet:
                self.cr.execute("SELECT hr_employee.id,rpb.acc_number AS employee_code, "\
                            "resource_resource.name AS employee_name,"\
                            "COALESCE(hr_payroll_main_archive.net,0) AS total "\
                            "FROM hr_payroll_main_archive "\
                            "left join hr_employee ON (hr_payroll_main_archive.employee_id = hr_employee.id) "\
                            "LEFT JOIN hr_salary_degree deg on (deg.id= hr_employee.degree_id) "\
                            "left join res_partner_bank rpb ON (hr_payroll_main_archive.bank_account_id = rpb.id) "\
                            "join resource_resource ON (hr_employee.resource_id = resource_resource.id) "\
                            "WHERE hr_payroll_main_archive.month=%s "\
                            "and hr_payroll_main_archive.year=%s " \
                            "and hr_payroll_main_archive.employee_id in %s " \
                            "and hr_payroll_main_archive.bank_account_id "+bank_query +
                            "and hr_payroll_main_archive.company_id =%s "\
                            "and hr_payroll_main_archive.in_salary_sheet =%s "\
                            "and hr_employee.payroll_id in %s "\
                            "order by deg.sequence, hr_employee.name_related" ,
                            (data['form']['month'],data['form']['year'],tuple(emp_ids),
                              tuple(c),salary_sheet, tuple(payroll_ids)))  
            else:
                self.cr.execute("SELECT hr_employee.id,rpb.acc_number AS employee_code, "\
                            "resource_resource.name AS employee_name,"\
                            "COALESCE(hr_payroll_main_archive.net,0) AS total "\
                            "FROM hr_payroll_main_archive "\
                            "left join hr_employee ON (hr_payroll_main_archive.employee_id = hr_employee.id) "\
                            "LEFT JOIN hr_salary_degree deg on (deg.id= hr_employee.degree_id) "\
                            "LEFT JOIN hr_allowance_deduction_archive adr ON (adr.main_arch_id=hr_payroll_main_archive.id)" \
                            "left join res_partner_bank rpb ON (hr_payroll_main_archive.bank_account_id = rpb.id) "\
                            "join resource_resource ON (hr_employee.resource_id = resource_resource.id) "\
                            "WHERE hr_payroll_main_archive.month=%s "\
                            "and hr_payroll_main_archive.year=%s " \
                            "and hr_payroll_main_archive.employee_id in %s " \
                            "and hr_payroll_main_archive.bank_account_id "+bank_query +
                            "and hr_payroll_main_archive.company_id =%s "\
                            "and hr_payroll_main_archive.in_salary_sheet =%s "\
                            "and hr_employee.payroll_id in %s "\
                            "and adr.allow_deduct_id = %s "\
                            'AND hr_payroll_main_archive.salary_date=%s ' \
                            "order by deg.sequence, hr_employee.name_related" ,
                            (data['form']['month'],data['form']['year'],tuple(emp_ids),
                              tuple(c),salary_sheet, tuple(payroll_ids), allow,data['form']['bonus_date'] ))

            res = self.cr.dictfetchall()
            i=0
            while (len(res) > i):
                          res_data = { 'no': i+1,
                                 'employee_code': res[i]['employee_code'], #employee_code
                                 'employee_name': res[i]['employee_name'],
                                 'total': res[i]['total'],
                               }
                          globals()['total_net'] += res[i]['total']
                          top_result.append(res_data)
                          i+=1
        return top_result

    def _total(self,data,bank_id):
        return globals()['total_net']

        
report_sxw.report_sxw('report.payroll.report.bank', 'hr.payroll.main.archive', 'addons/hr_payroll_custom/report/payroll_report_bank.rml' ,parser=payroll_report_bank,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


