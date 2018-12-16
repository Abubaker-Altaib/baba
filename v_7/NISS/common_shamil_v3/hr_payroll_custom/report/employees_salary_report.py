import time
from report import report_sxw
import calendar
import datetime
import pooler

class employees_salary(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(employees_salary, self).__init__(cr, uid, name, context)
        self.attr_dict = dict()
        self.attr_dict['all_total'] = 0
        self.attr_dict['total'] = 0
        self.attr_dict['loan'] = 0
        self.attr_dict['tax'] = 0
        self.attr_dict['basic'] = 0
        self.attr_dict['loan_total'] = {'loan_total':0 }
        self.localcontext.update({
            'time': time,
            'allow_deduct':self._get_allow_deduct,
            'loan':self._get_loan,
            'loan_total':self._get_loan_total,
            'total':self._get_total,
            'tax':self.tax_total,
            'basic':self.basic_salary,
               })
        
        


#------------------------------- allowance/deduction----------------------------------   
    def _get_allow_deduct(self,data,emp_id,name_type,paysheet):
        where = [emp_id,data['form']['month'],data['form']['year'],name_type]
        paysheet_clause = ""
        if paysheet:
           paysheet_clause = "and b.pay_sheet =%s "
           where.append(paysheet)
        self.cr.execute("SELECT e.sequence,b.sequence,e.name_related AS employee_name,round(m.amount,2) AS amount,b.name AS name FROM  hr_payroll_main_archive AS p left join hr_allowance_deduction_archive AS m on (m.main_arch_id=p.id) left join hr_allowance_deduction b on (m.allow_deduct_id=b.id) left join hr_employee e on (p.employee_id=e.id) WHERE e.id = %s and p.month=%s and  p.year=%s and b.name_type= %s and p.in_salary_sheet= True " + paysheet_clause + "GROUP BY e.sequence,b.sequence,e.name_related,m.amount,b.name ORDER BY e.sequence,b.sequence",tuple(where))    
        res = self.cr.dictfetchall() 
        self.attr_dict['total'] = {'total':sum(r['amount'] for r in res)} 
        if name_type=='allow':
           self.attr_dict['all_total']+=self.attr_dict['total']['total']
        else:
           self.attr_dict['all_total']-=self.attr_dict['total']['total']
        return res
#-------------------------loan----------------#

    def _get_loan(self,data,emp_id,paysheet):
        where = [emp_id,data['form']['month'],data['form']['year']]
        paysheet_clause = ""
        if paysheet:
           paysheet_clause = "and b.pay_sheet =%s "
           where.append(paysheet)
        self.cr.execute("SELECT round(m.loan_amount,2) AS amount,b.name AS name FROM  hr_payroll_main_archive AS p left join hr_loan_archive AS m on (m.main_arch_id=p.id) left join hr_employee_loan b on (m.loan_id=b.id) left join hr_employee e on (p.employee_id=e.id) WHERE e.id = %s and p.month=%s and  p.year=%s and p.in_salary_sheet= True " + paysheet_clause + "GROUP BY e.sequence,m.loan_amount,b.name ORDER BY e.sequence",tuple(where))    
        loan = self.cr.dictfetchall() 
        if loan[0]['amount'] :
            self.attr_dict['loan_total'] = {'loan_total':sum(r['amount'] for r in loan)} 
        else : return {};
        return loan

#----------------------- loan_total-----------##
    def _get_loan_total(self,data,emp_id):
        where = [emp_id,data['form']['month'],data['form']['year']]
        self.cr.execute("SELECT round(m.loan_amount,2) AS amount,b.name AS name FROM  hr_payroll_main_archive AS p left join hr_loan_archive AS m on (m.main_arch_id=p.id) left join hr_employee_loan b on (m.loan_id=b.id) left join hr_employee e on (p.employee_id=e.id) WHERE e.id = %s and p.month=%s and  p.year=%s GROUP BY e.sequence,m.loan_amount,b.name ORDER BY e.sequence",tuple(where))    
        loan = self.cr.dictfetchall() 
        loan_total = 0
        for l in loan :
            if l['amount'] :
                loan_total += l['amount']
        self.attr_dict['loan_total'] = {'loan_total':loan_total }
        return self.attr_dict['loan_total']

#------------------------------------------- total --------------------------   
    
    def _get_total(self,total_type):
        if total_type == 'allow_deduct':
           return self.attr_dict ['total'] 
        else:
           total= self.attr_dict ['all_total']
           self.attr_dict ['all_total'] =0
           return total  
   


#------------------------------------------- tax --------------------------   
    def tax_total(self,data,emp_id):
        main_archive_obj= pooler.get_pool(self.cr.dbname).get('hr.payroll.main.archive')
        main_arch_ids= main_archive_obj.search(self.cr, self.uid,[('employee_id', '=',emp_id),('month', '=', data['form']['month']),('year', '=', data['form']['year']),('in_salary_sheet', '=',True)])
        if main_arch_ids:
           for record in main_archive_obj.browse(self.cr, self.uid,main_arch_ids):
              self.attr_dict['tax']={'tax':record.tax + record.allowances_tax}
 
        return self.attr_dict['tax']

#-------------------------------------------basic salary--------------------------   
    def basic_salary(self,data,emp_id):
        main_archive_obj= pooler.get_pool(self.cr.dbname).get('hr.payroll.main.archive')
        main_arch_ids= main_archive_obj.search(self.cr, self.uid,[('employee_id', '=',emp_id),('month', '=', data['form']['month']),('year', '=', data['form']['year']),('in_salary_sheet', '=',True)])
        if main_arch_ids:
           for record in main_archive_obj.browse(self.cr, self.uid,main_arch_ids):
              self.attr_dict['basic']={'basic':record.basic_salary}
 
        return self.attr_dict['basic']




report_sxw.report_sxw('report.employees.salary', 'hr.employee', 'addons/hr_payroll_custom/report/employees_salary_report.rml' ,parser=employees_salary, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
