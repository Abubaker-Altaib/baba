#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pooler
from report import report_sxw
from datetime import datetime

class payroll_report(report_sxw.rml_parse):
    globals()['total_allow_inc'] = 0
    globals()['total_allow_dec'] = 0
    globals()['total_deduct_ince'] = 0
    globals()['total_deduct_dec'] = 0
    globals()['total_prev'] = 0
    globals()['total_curr'] = 0
    globals()['loan_inc'] = 0
    globals()['loan_dec'] = 0

    def __init__(self, cr, uid, name, context):
        super(payroll_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'total':self._get_total_pyroll,
            'payroll':self._get_payroll_budget,
            'user':self._get_user,
        })
        globals()['total_allow_inc'] = 0
        globals()['total_allow_dec'] = 0
        globals()['total_deduct_ince'] = 0
        globals()['total_deduct_dec'] = 0
        globals()['total_prev'] = 0
        globals()['total_curr'] = 0
        globals()['loan_inc'] = 0
        globals()['loan_dec'] = 0

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name

    def _get_payroll_budget(self,data):
        top_result=[]
        re_res1=[]
        re_res2=[]
        re_res3=[]
        no=0
        count = 0
        globals()['total_allow_inc'] = 0
        globals()['total_allow_dec'] = 0
        globals()['total_deduct_ince'] = 0
        globals()['total_deduct_dec'] = 0
        globals()['total_prev'] = 0
        globals()['total_curr'] = 0
        globals()['loan_inc'] = 0
        globals()['loan_dec'] = 0
        pay_dep= data['form']['department_ids']
        c= data['form']['company_id'][0]
        if int(data['form']['month'])==1:
           prev_month=12
           year=data['form']['year']-1
        else:
           prev_month=int(data['form']['month'])-1
           year=data['form']['year']
        self.cr.execute('''SELECT distinct 
hr_payroll_main_archive.employee_id as ids,
hr_department_payroll.name as empdep,
deg.sequence,
hr_employee.emp_code AS employee_code,
hr_employee.name_related ,
hr_employee.emp_code as emp_code ,
deg.name as emp_deg ,
resource_resource.name AS employee_name,
(select net from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=hr_employee.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) AS total ,
(select net from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=hr_employee.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) AS prev_total ,
((select net from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=hr_employee.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) - (select net from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=hr_employee.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS diff 
 FROM
 hr_payroll_main_archive
left join hr_employee ON (hr_payroll_main_archive.employee_id = hr_employee.id)
left join hr_salary_degree as deg ON (deg.id= hr_payroll_main_archive.degree_id) 
left join resource_resource ON (hr_employee.resource_id = resource_resource.id) 
left join hr_department_payroll ON (hr_payroll_main_archive.payroll_employee_id = hr_department_payroll.id)
WHERE hr_payroll_main_archive.company_id =%s and ( (hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s) or (hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s) ) and hr_payroll_main_archive.in_salary_sheet=True and hr_payroll_main_archive.payroll_employee_id in %s
order by  deg.sequence DESC''' ,
 (int(data['form']['month']),data['form']['year'],prev_month,year,int(data['form']['month']),data['form']['year'],prev_month,year,c,int(data['form']['month']),data['form']['year'],prev_month,year,tuple(pay_dep),))    
        res = self.cr.dictfetchall()
        page = 0
        for b in res:
                    if b['diff'] is None: b['diff'] = 0.0
                    if b['total'] is None: b['total'] = 0.0
                    if b['prev_total'] is None: b['prev_total'] = 0.0
                    # if (b['total'] - b['prev_total']) == 0.0: 
                    #     continue
                    count += 1 
                    check=0
                    check1=0
                    sums=0
                    sums1=0.0
                    allow_incres = 0
                    allow_decres = 0
                    deduct_incres = 0
                    deduct_decres = 0
                    final_allow = 0
                    final_deduct = 0
                    loan_incres = 0
                    loan_decres = 0

                    comments = ''
                    comm = ''
                    no+=1
                    dic={
                      'no':no,
                      'emp_deg':b['emp_deg'],
                      'emp_code':b['emp_code'],
                      'employee_name':b['employee_name'],
                      'total':b['total'],
                      'prev_total':b['prev_total'],
                      'diff':b['diff'],
                      'ids':b['ids'],
                      
                        }
                    re_res1.append(dic)

                    self.cr.execute('''SELECT distinct
(select sum(loan.loan_amount) FROM hr_loan_archive loan,hr_payroll_main_archive where  loan.main_arch_id = hr_payroll_main_archive.id and hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as loan_prev,

(select sum(loan.loan_amount) FROM hr_loan_archive loan,hr_payroll_main_archive where  loan.main_arch_id = hr_payroll_main_archive.id and hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)as loan_now 

FROM hr_loan_archive ''',
(b['ids'],prev_month,year,b['ids'],int(data['form']['month']),data['form']['year']))
                    res5 = self.cr.dictfetchall()

                    final_loan=0
                    for cc in res5:
                        if cc['loan_prev'] == None:
                            cc['loan_prev'] = 0

                        if cc['loan_now'] == None:
                            cc['loan_now'] = 0

                        final_loan = cc['loan_now'] - cc['loan_prev'] 
                        #final_deduct = cc['deduct_now'] - cc['deduct_prev']
                    if final_loan > 0 :
                        loan_incres = final_loan
                        globals()['loan_inc'] += loan_incres
                    if final_loan < 0 :
                        loan_decres = final_loan
                        globals()['loan_dec'] += loan_decres
                    

                    self.cr.execute('''SELECT distinct
(select sum(adr.amount) FROM hr_allowance_deduction_archive adr,hr_payroll_main_archive where adr.type='allow' and adr.main_arch_id = hr_payroll_main_archive.id and hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as allow_prev,

(select sum(adr.amount) FROM hr_allowance_deduction_archive adr,hr_payroll_main_archive where adr.type='allow' and adr.main_arch_id = hr_payroll_main_archive.id and hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)as allow_now,

(select sum(adr.amount) FROM hr_allowance_deduction_archive adr,hr_payroll_main_archive where adr.type='deduct' and adr.main_arch_id = hr_payroll_main_archive.id and hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as deduct_prev,

(select sum(adr.amount) FROM hr_allowance_deduction_archive adr,hr_payroll_main_archive where adr.type='deduct' and adr.main_arch_id = hr_payroll_main_archive.id and hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)as deduct_now

FROM hr_allowance_deduction_archive ''',
(b['ids'],prev_month,year,b['ids'],int(data['form']['month']),data['form']['year'],b['ids'],prev_month,year,b['ids'],int(data['form']['month']),data['form']['year']))
                    res1 = self.cr.dictfetchall()

                    ################tax#################################
                    self.cr.execute('''SELECT distinct
(select distinct hr_payroll_main_archive.tax FROM hr_payroll_main_archive where hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as deduct_prev,

(select distinct hr_payroll_main_archive.tax FROM hr_payroll_main_archive where hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)as deduct_now

FROM hr_allowance_deduction_archive ''',
(b['ids'],prev_month,year,b['ids'],int(data['form']['month']),data['form']['year']))
                    res_tax = self.cr.dictfetchall()
                    #####################################################

                    ################basic salary#################################
                    self.cr.execute('''SELECT distinct
(select distinct hr_payroll_main_archive.basic_salary FROM hr_payroll_main_archive where hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as salary_prev,

(select distinct hr_payroll_main_archive.basic_salary FROM hr_payroll_main_archive where hr_payroll_main_archive.employee_id=%s and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)as salary_now

FROM hr_allowance_deduction_archive ''',
(b['ids'],prev_month,year,b['ids'],int(data['form']['month']),data['form']['year']))
                    res_basic = self.cr.dictfetchall()
                    #####################################################

                    #print res1,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                    for cc in res1:
                        if cc['allow_now'] == None:
                            cc['allow_now'] = 0

                        if cc['allow_prev'] == None:
                            cc['allow_prev'] = 0

                        if cc['deduct_now'] == None:
                            cc['deduct_now'] = 0

                        if cc['deduct_prev'] == None:
                            cc['deduct_prev'] = 0
                        if res_tax:
                            if res_tax[0]['deduct_prev'] == None:
                                res_tax[0]['deduct_prev'] = 0
                            if res_tax[0]['deduct_now'] == None:
                                res_tax[0]['deduct_now'] = 0

                            cc['deduct_prev'] += res_tax[0]['deduct_prev']
                            cc['deduct_now'] += res_tax[0]['deduct_now']
                        
                        if res_basic:
                            if res_basic[0]['salary_prev'] == None:
                                res_basic[0]['salary_prev'] = 0
                            if res_basic[0]['salary_now'] == None:
                                res_basic[0]['salary_now'] = 0
                            cc['allow_prev'] += res_basic[0]['salary_prev']
                            cc['allow_now'] += res_basic[0]['salary_now']

                        final_allow = cc['allow_now'] - cc['allow_prev'] 
                        final_deduct = cc['deduct_now'] - cc['deduct_prev']
                    if final_allow > 0 :
                        allow_incres = final_allow
                        globals()['total_allow_inc'] += allow_incres
                    if final_allow < 0 :
                        allow_decres = final_allow
                        globals()['total_allow_dec'] += allow_decres
                    if final_deduct > 0:
                        deduct_incres = final_deduct
                        globals()['total_deduct_ince'] += deduct_incres
                    if final_deduct < 0 :
                        deduct_decres = final_deduct
                        globals()['total_deduct_dec'] += deduct_decres
                    if b['total'] == None:
                        b['total'] = 0
                    globals()['total_curr'] += b['total']
                    if b['prev_total'] == None:
                        b['prev_total'] = 0
                    globals()['total_prev'] += b['prev_total']
                    self.cr.execute('''SELECT distinct exp.comments FROM hr_allowance_deduction_exception exp where exp.employee_id=%s and cast(to_char(exp.start_date ,'MM') as int)<=%s and cast(to_char(exp.end_date ,'MM') as int)>=%s and cast(to_char(exp.start_date ,'YYYY') as int) =%s and cast(to_char(exp.end_date ,'YYYY') as int)=%s ''',
(b['ids'],int(data['form']['month']),int(data['form']['month']),data['form']['year'],data['form']['year']))
                    res_comments = self.cr.dictfetchall()
                    for com in res_comments:
                        #comments += com['comments'] and '/'+com['comments'] or '/'
                         comments +=  '/'
                    if comments:
                        comments = comments.split('/', 1 )
                        comm = comments[1]
                    x={
                        'allow_incres':allow_incres,
                        'allow_decres':allow_decres,
                        'deduct_incres':deduct_incres,
                        'deduct_decres':deduct_decres,
                        'emp_deg':b['emp_deg'],
                        'emp_code':b['emp_code'],
                        'employee_name':b['employee_name'],
                        'total':b['total'],
                        'prev_total':b['prev_total'],
                        'incras':comm,
                        'no':no,
                        'loan_incres':loan_incres,
                        'loan_decres':loan_decres,
                       }
                    if allow_incres == 0.0 and allow_decres == 0.0 and deduct_incres == 0.0 and deduct_decres == 0.0 and loan_incres == 0.0 and loan_decres == 0.0:
                        count -= 1
                        globals()['total_curr'] -= b['total']
                        globals()['total_prev'] -= b['prev_total']
                        continue
                    re_res2.append(x)

                    if (count % 16) == 0.0 and page == 0:
                        page += 1
                        count = 0
                        x1={
                        'allow_incres':globals()['total_allow_inc'],
                        'allow_decres':globals()['total_allow_dec'],
                        'deduct_incres':globals()['total_deduct_ince'],
                        'deduct_decres':globals()['total_deduct_dec'],
                        'employee_name':u'الإجمالي',
                        'total':globals()['total_curr'],
                        'prev_total':globals()['total_prev'],
                        'incras':comm,
                        'no':'-',
                        'loan_incres':globals()['loan_inc'],
                        'loan_decres':globals()['loan_dec'],
                       }
                        re_res2.append(x1) 
                        re_res3.append(re_res2) 
                        re_res2 = []
                        x2={
                            'allow_incres':globals()['total_allow_inc'],
                            'allow_decres':globals()['total_allow_dec'],
                            'deduct_incres':globals()['total_deduct_ince'],
                            'deduct_decres':globals()['total_deduct_dec'],
                            'employee_name':u'الإجمالي المرحل',
                            'total':globals()['total_curr'],
                            'prev_total':globals()['total_prev'],
                            'incras':comm,
                            'no':'-',
                            'loan_incres':globals()['loan_inc'],
                            'loan_decres':globals()['loan_dec'],
                        }
                        re_res2.append(x2)
                    elif (count % 15) == 0.0 and page != 0:
                        page += 1
                        x1={
                        'allow_incres':globals()['total_allow_inc'],
                        'allow_decres':globals()['total_allow_dec'],
                        'deduct_incres':globals()['total_deduct_ince'],
                        'deduct_decres':globals()['total_deduct_dec'],
                        'employee_name':u'الإجمالي',
                        'total':globals()['total_curr'],
                        'prev_total':globals()['total_prev'],
                        'incras':comm,
                        'no':'-',
                        'loan_incres':globals()['loan_inc'],
                        'loan_decres':globals()['loan_dec'],
                       }
                        re_res2.append(x1) 
                        re_res3.append(re_res2) 
                        re_res2 = []
                        x2={
                            'allow_incres':globals()['total_allow_inc'],
                            'allow_decres':globals()['total_allow_dec'],
                            'deduct_incres':globals()['total_deduct_ince'],
                            'deduct_decres':globals()['total_deduct_dec'],
                            'employee_name':u'الإجمالي المرحل',
                            'total':globals()['total_curr'],
                            'prev_total':globals()['total_prev'],
                            'incras':comm,
                            'no':'-',
                            'loan_incres':globals()['loan_inc'],
                            'loan_decres':globals()['loan_dec'],
                        }
                        re_res2.append(x2)

                    else:
                        # if b == res[len(res)-1]:
                        #     x1={
                        #     'allow_incres':globals()['total_allow_inc'],
                        #     'allow_decres':globals()['total_allow_dec'],
                        #     'deduct_incres':globals()['total_deduct_ince'],
                        #     'deduct_decres':globals()['total_deduct_dec'],
                        #     'employee_name':u'الإجمالي',
                        #     'total':globals()['total_curr'],
                        #     'prev_total':globals()['total_prev'],
                        #     'incras':comm,
                        #     'no':'-',
                        #     'loan_incres':globals()['loan_inc'],
                        #     'loan_decres':globals()['loan_dec'],
                        # }
                        #     re_res2.append(x1) 

                        re_res3.append(re_res2)
                        re_res2 = []
        return re_res3

    def _get_total_pyroll(self,data):

        top_result=[]
        re_res1=[]
        re_res2=[]
        no=0
        c= data['form']['company_id'][0]
        if data['form']['month']==1:
           prev_month=12
           year=data['form']['year']-1
        else:
           prev_month=int(data['form']['month'])-1
           year=data['form']['year']
        self.cr.execute('''SELECT distinct 
(select sum(net) from hr_payroll_main_archive where  month=%s and year=%s) AS s_total ,
(select sum(net) from hr_payroll_main_archive where month=%s and year=%s) AS s_prev_total 
 FROM
 hr_payroll_main_archive
left join hr_employee ON (hr_payroll_main_archive.employee_id = hr_employee.id) 
join resource_resource ON (hr_employee.resource_id = resource_resource.id) 
WHERE hr_payroll_main_archive.company_id =%s''' ,
 (int(data['form']['month']),data['form']['year'],prev_month,year,c))    
        res0 = self.cr.dictfetchall()
        if res0[0]['s_total'] == None :
            res0[0]['s_total'] = 0

        if res0[0]['s_prev_total'] == None:
            res0[0]['s_prev_total'] = 0
        x={
            'total_allow_inc':globals()['total_allow_inc'],
            'total_allow_dec':globals()['total_allow_dec'],
            'total_deduct_ince':globals()['total_deduct_ince'],
            'total_deduct_dec':globals()['total_deduct_dec'],
            'inc_total':globals()['total_curr'],
            'dec_total':globals()['total_prev'],
            'loan_inc':globals()['loan_inc'],
            'loan_dec':globals()['loan_dec'],
           } 
        re_res2.append(x)
        return re_res2 
        
report_sxw.report_sxw('report.payroll.budget', 'hr.payroll.main.archive', 'addons/hr_payroll_custom/report/payroll_budget_report.rml' ,parser=payroll_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


