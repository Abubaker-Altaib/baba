# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw
from mako.template import Template
from openerp.report.interface import report_rml
from openerp.report.interface import toxml

class loan_details_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loan_details_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._process,  
        })

    
    def get_sum(self,row,sum_counter,i,name_str):
        #to avoid header
        if sum_counter == 0:sum_counter=1
        sum_row = []
        for x in row[0]:
            sum_row.append(0.0)
        co = 1
        while co < (sum_counter + i):
            col = 0
            while col < len(row[co]):
                try:
                    sum_row[col] += float(str(row[co][col]))
                    sum_row[col] = round(sum_row[col],2)
                except:
                    sum_row[col] = name_str
                col += 1
            co += 1
        sum_row[len(sum_row)- 1] = ''
        return sum_row

    def _process(self,data):
        row=[]
        col=[]
        sums=[]
        loan_obj = self.pool.get('hr.loan')
        company = data['company_id'][0]
        loan_ids = loan_obj.search(self.cr,self.uid,['|',('company_ids','=',False),('company_ids', 'in', (company))])
        loans=loan_obj.browse(self.cr,self.uid, loan_ids)
        
        self.cr.execute('''SELECT emp.id
         from hr_employee emp,resource_resource ,
         hr_salary_degree deg 
         where resource_resource.id=emp.resource_id 
         AND resource_resource.company_id = %s 
         AND emp.state != 'refused'  
         and deg.id= emp.degree_id 
         ORDER BY  deg.sequence,emp.name_related'''%(company))        
        
        new_emp_ids = self.cr.dictfetchall()
        new_emp_ids = [i['id'] for i in new_emp_ids]


        employee_ids=self.pool.get('hr.employee').browse(self.cr,self.uid, new_emp_ids)
        


        self.cr.execute('''SELECT emp.id as employee,
                      hr_l_a.loan_amount AS amount, hr_loan.id as loan_id 
                      FROM hr_loan_archive hr_l_a
                      left join hr_employee emp on(emp.id = hr_l_a.employee_id)  
		              left join hr_employee_loan hrel on (hrel.id = hr_l_a.loan_id)
                      left join hr_loan on (hr_loan.id = hrel.loan_id)
                      WHERE emp.id in %s
                      And hr_l_a.year = %s
                      AND hr_l_a.month = %s
                      and hr_l_a.payment_type = 'salary' ''',(tuple(new_emp_ids),data['year'],data['month']))
        res = self.cr.dictfetchall()

        amounts=dict([((r['employee'],r['loan_id']), r['amount']) for r in res])

        
        
        


        col.append(u'الاجمالي ')
        for loan in loans:
            col.append(loan.name)
        
        col.append(u'اﻹسم')
        col.append(u'الرقم')
        row.append(col)
        counter = 1
        for emp in employee_ids:
            col=[]  
            amount_total = 0
            amount_list = []
            for loan in loans:
                amount= amounts.get((emp.id,loan.id), 0.0)
                amount_list.append(amount)
                amount_total += amount
            
            col.append(amount_total)
            for amount1 in amount_list:
                col.append(amount1)
            col.append(emp.name)
            if amount_total != 0:
                col.append(counter)
                counter+=1
                row.append(col)
        
        if len(row) > 1:
            sum_row = []
            for x in row[1]:
                sum_row.append(0.0)
            co = 1
            while co < len(row):
                i = 0
                while i < len(row[co]):
                    try:
                        sum_row[i] += float(str(row[co][i]))
                        sum_row[i] = round(sum_row[i],2)
                    except:
                        sum_row[i] = u'الإجمالي'
                    i += 1
                co += 1
            sum_row[len(sum_row)- 1] = ''
            
            co = 0
            while co < (len(sum_row) - 1):
                if sum_row[co] == 0:
                    i = 0
                    while i < len(row):
                        del row[i][co]
                        i+=1
                    del sum_row[co]
                    co -= 1
                co+=1
                    


            row.append(sum_row)    

            new_list = []
            header = row[0]
            flag = False
            i = 0
            sum_counter = 0
            for item in row:
                new_list.append(item)
                if i == 10 and not flag:
                    new_list.append(self.get_sum(row,sum_counter,i,u'اﻹجمالي'))
                    new_list.append(header)
                    new_list.append(self.get_sum(row,sum_counter,i,u'اﻹجمالي المرحل'))
                    
                    #keep position for sum
                    sum_counter += 10
                    flag = True
                    i = 0
                if i == 11:
                    new_list.append(self.get_sum(row,sum_counter,i,u'اﻹجمالي'))
                    new_list.append(header)
                    new_list.append(self.get_sum(row,sum_counter,i,u'اﻹجمالي المرحل'))
                    
                    #keep position for sum
                    sum_counter += 11
                    i = 0
                i += 1
            row = new_list
           

        return row

report_sxw.report_sxw('report.loan.details', 'hr.loan.archive', 'addons/hr_loan/report/loan_details.mako' ,parser=loan_details_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

