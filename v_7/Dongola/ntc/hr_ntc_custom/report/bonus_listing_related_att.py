# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class bonus_listing_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bonus_listing_report, self).__init__(cr, uid, name, context)
        self.total = {'total_allowance':0.0, 'total_deduction':0.0,'total_loans':0.0,'net':0.0,
                      'allowances_tax':0.0,'tax':0.0,'zakat':0.0,'imprint':0.0}
        self.name = {'name':''}
        self.localcontext.update({
            'time': time,
            'payroll':self.payroll,
            'name': self._name,
        })
    def get_sum(self,row,sum_counter,i,name_text):
        #to avoid header
        if sum_counter == 0:sum_counter=1
        sum_row = []
        for x in row[1]:
            sum_row.append(0.0)
        

        co = 1
        while co < (sum_counter + i):
            col = 0
            while col < len(row[co]):
                try:
                    sum_row[col] += float(str(row[co][col]))
                    sum_row[col] = round(sum_row[col],2)
                except:
                    sum_row[col] = name_text
                col += 1
            co += 1
        sum_row[len(sum_row)- 1] = ''
        return sum_row
            #row.append(sum_row)
    
    def payroll(self,data):
        salary_obj = self.pool.get('hr.salary.scale')
        company= data['form']['company_id'][0]
        payroll_ids= salary_obj.search(self.cr,self.uid,[])
        total_data = [] 
        sub_data = []
        sub_data2 = []
        self.cr.execute(
            'SELECT emp.id, emp.name_related AS name, '\
            'pay.total_allowance AS total_allowance,pay.total_deduction AS total_deduction,pay.total_loans AS total_loans,'\
            'pay.allowances_tax AS allowances_tax,pay.tax AS tax,pay.zakat AS zakat,'\
            'pay.net AS net, adr.imprint AS imprint ,pay.id AS pay_id '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
            'LEFT JOIN hr_salary_degree deg on (deg.id= emp.degree_id)'\
            'LEFT JOIN hr_allowance_deduction_archive adr ON (adr.main_arch_id=pay.id)' \
            'WHERE pay.month  =%s'\
            'AND pay.year=%s ' \
            'AND adr.allow_deduct_id = %s '\
            'AND pay.salary_date=%s ' \
            'AND pay.company_id = %s '\
            'AND pay.scale_id in %s '\
            'AND adr.type = %s '\
            'AND pay.in_salary_sheet = False '\
	        'group by emp.id,pay.total_allowance ,pay.total_deduction,pay.allowances_tax,pay.tax,pay.zakat,pay.net,deg.sequence,pay.total_loans,adr.imprint,pay.id '
            'ORDER BY  deg.sequence,emp.name_related' , (data['form']['month'],data['form']['year'],data['form']['allow'][0],data['form']['bonus_date'],company,tuple(payroll_ids),'allow'))    
        res = self.cr.dictfetchall()
        pays_ids = [i['pay_id'] for i in res]
        pays_ids += pays_ids

        self.cr.execute(
            'SELECT sadnper.employee_id as emp ,sadnper.percentage as percentage '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN 	hr_employee_salary_addendum sadn ON (pay.arch_id=sadn.id)' \
            'LEFT JOIN 	hr_salary_addendum_percentage sadnper ON (sadnper.adden_id=sadn.id)' \
            'WHERE pay.id  = %s ', tuple(  pays_ids[:1]  ))    
        percent = self.cr.dictfetchall()
        percent = {i['emp']:i['percentage'] for i in percent}

        self.cr.execute(
            'SELECT emp.id,adr.allow_deduct_id as deduct_name,adr.amount as deduct_amount '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
            'LEFT JOIN hr_allowance_deduction_archive adr ON (adr.main_arch_id=pay.id) ' \
            'WHERE pay.id  in %s '\
            'AND adr.type = %s ', (tuple(pays_ids) ,'deduct'))    
        deduct_res = self.cr.dictfetchall()

        deduct_ids = [i['deduct_name'] for i in deduct_res]

        deduct_ids = list(set(deduct_ids))

        allowobj = self.pool.get('hr.allowance.deduction')

        allow_read = allowobj.read(self.cr, self.uid, deduct_ids,['name'])

        allow_names = {i['id']:i['name'] for i in allow_read}

        #allow_names.reverse()

        self.cr.execute(
            'SELECT emp.id,ln_type.id as loan_name,ln.loan_amount as loan_amount '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
            'LEFT JOIN hr_loan_archive ln ON (ln.main_arch_id=pay.id) ' \
            'LEFT JOIN hr_employee_loan emln ON (ln.loan_id=emln.id)'
            'LEFT JOIN hr_loan ln_type ON (ln_type.id=emln.loan_id) ' \
            'WHERE pay.id in '+str(tuple(pays_ids) )) 

        
        loan_res = self.cr.dictfetchall()


        loan_ids = [i['loan_name'] for i in loan_res]

        loan_ids = list(set(loan_ids))
        
        loanobj = self.pool.get('hr.loan')

        loan_read = loanobj.read(self.cr, self.uid, loan_ids,['name'])

        loan_names = [i['name'] for i in loan_read]

        loan_names.reverse()
	#deduct_ids.reverse()
        


        new_list = []
        names_line = []
        names_line += [u'الصافي',u'إجمالي الخصومات',u'الضريبة على اﻹستحقاقات']
        #names_line += allow_names
        #names_line += loan_names
        for deduct_id in deduct_ids:
            names_line+=[allow_names[deduct_id] ]
        names_line += [u'إجمالي السلفيات',u'الدمغة',u'الضريبة', u'الحافز',u'النسبة', u'اﻹستحقاق',u'الاسم']
        new_list.append(names_line)

        counter = 1
        for i in res:
            line = []
            line.append(i['net'])
            line.append(i['total_deduction']+i['total_loans'])
            line.append(i['allowances_tax'])
            for deduct_id in deduct_ids:
                if deduct_id:
                    ll = filter(lambda x :  x['id'] == i['id'] and deduct_id == x['deduct_name'] , deduct_res)
                    if ll:
                        line.append(ll[0]['deduct_amount'] and ll[0]['deduct_amount'] or 0.0)
                    else:
                        line.append(0.0)
            
            '''for loan_id in loan_ids:
                if loan_id:
                    ll = filter(lambda x :  x['id'] == i['id'] and loan_id == x['loan_name'] , loan_res)
                    if ll:
                        line.append(ll[0]['loan_amount'] and ll[0]['loan_amount'] or 0.0)
                    else:
                        line.append(0.0)'''
            line.append(i['total_loans'])
            line.append(i['imprint'])
            line.append(i['tax'])
            line.append(i['total_allowance'])

            line.append(percent[i['id']])
            x = i['total_allowance'] * 100.0
            x = x / percent[i['id']]
            x = round(x,2)
            line.append(x)

            line.append(i['name'])
            line.append(counter)
            counter += 1
            new_list.append(line)
        
        row = new_list

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
        row.append(sum_row)

        co = 0
        while co < (len(sum_row) - 1):
            if sum_row[co] == 0:
                i = 0
                while i < len(row) - 1:
                    del row[i][co]
                    i+=1
                del sum_row[co]
                co -= 1
            co+=1

        new_list = []
        header = names_line
        flag = False
        i = 0
        sum_counter = 0
        for item in row:
            new_list.append(item)
            if i == 14 and not flag:
                new_list.append(self.get_sum(row,sum_counter,i,u'الإجمالي'))
                new_list.append(header)
                new_list.append(self.get_sum(row,sum_counter,i,u'اﻹجمالي المرحل'))
                
                #keep position for sum
                sum_counter += 14
                flag = True
                i = 0
            if i == 17 and flag:
                new_list.append(self.get_sum(row,sum_counter,i+1,u'الإجمالي'))
                new_list.append(header)
                new_list.append(self.get_sum(row,sum_counter,i+1,u'اﻹجمالي المرحل'))
                #keep position for sum
                sum_counter += 17
                i = 0
            i += 1


        #print "..................dd",total_data
        return new_list

    def _name(self):
        return [self.name]  
   
report_sxw.report_sxw('report.bonus_listing_related_att.report', 'hr.payroll.main.archive', 'addons/hr_ntc_custom/report/bonus_listing.mako' ,parser=bonus_listing_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



