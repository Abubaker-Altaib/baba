import time
from report import report_sxw
import calendar
import datetime


class loan_details_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loan_details_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self.get_employee,
            'line1':self._getcom,
            #'line5':self.emp_count,
            'name':self._get_ded_allow_name,
            'total':self._get_ded_allow_total,
                     
        })

    globals()['columns_size'] = 16

    def _getcom(self,data):
        self.cr.execute('SELECT name AS company_name From res_company where id=%s'%(data['form']['company_id'][0]))
        res = self.cr.dictfetchall()
        
        return res
    def get_employee(self,data):
         total1=0
         total2=0
         total3=0
         total4=0
         total5=0
         total6=0
         total7=0
         total8=0
         total9=0
         total10=0
         total11=0
         total12=0
         total13=0
         total14=0
         total15=0
         total16=0
         total17=0
         res_data = {}
         top_result = []
         res = {}
         com_res = {}
         periods = []  
         year = data['year'] 
         month = data['month']
         company = data['company_id'][0]
         #---------- function to get sequence for table ----------------
         def get_seq_table(self,allow_seq,emp):
             last_val = 0
             loan = 0
             where_clause = " WHERE active = TRUE  " 
             loan_obj = self.pool.get('hr.loan')
             loan_ids = loan_obj.search(self.cr,self.uid,['|',('company_ids','=',False),('company_ids', 'in', (company))])
             if loan_ids:
                where_clause += " and id in (%s) " % ','.join(map(str, loan_ids))
             self.cr.execute('''SELECT id FROM hr_loan''' + where_clause + ''' Order by id ASC ''')
             allow_ded_res = self.cr.dictfetchall()
             res_len = len(allow_ded_res)
             for i in xrange(0,res_len):
                 if(allow_seq == (i+1)):
                       last_val = allow_ded_res[i]['id']
             #------------------- Get data from loan installment table -------------------
             if (last_val > 0):
                    #
                    self.cr.execute('''SELECT hr_employee_loan.id
                         FROM public.hr_employee_loan,public.hr_loan_archive
                         WHERE hr_loan_archive.loan_id = hr_employee_loan.id 
                         AND hr_employee_loan.loan_id= %s 
                         AND public.hr_loan_archive.year= %s 
                         AND public.hr_loan_archive.month= %s 
                         AND public.hr_employee_loan.employee_id= %s''',(last_val,str(year),str(month),emp))
                    loan_res = self.cr.dictfetchall()
                    if(len(loan_res) > 0):
                        loan = loan_res[0]['id']
             return loan      
         #----------------- Get employees from hr_employee depend on company ------------
         self.cr.execute("SELECT hr_employee.id,hr_employee.sequence from hr_employee,resource_resource where resource_resource.id=hr_employee.resource_id AND resource_resource.company_id = %s AND hr_employee.state != 'refused'  order by hr_employee.sequence"%(company))
         com_res = self.cr.dictfetchall()
         x = 0
         
         for b in com_res:
                  periods.append(com_res[x]['id'])
                  x+=1
         i = 0
         count = len(periods)
         #----------------- set all loans to 0 at fisrt ----------
         for r in xrange(1,(columns_size+1)):
             globals()['allow_amount%s' % r] = 0
         #------------------------------------------------------------
         while i < count:
                
               self.cr.execute('''SELECT hr_employee.id,resource_resource."name" AS emp_name, hr_employee.emp_code AS emp_code,\
                      hr_loan_archive.loan_amount AS loan_amount, hr_loan_archive.loan_id 
                      FROM public.resource_resource,public.hr_employee,hr_loan_archive
                      WHERE resource_resource.id = hr_employee.resource_id 
                      AND hr_employee.id = hr_loan_archive.employee_id 
                      AND hr_employee.id = %s 
                      AND hr_loan_archive.year = %s 
                      AND hr_loan_archive.month = %s ;''',(periods[i],year,month))
               res = self.cr.dictfetchall()
               
               #-------------- if first sheet add basic amount to total -----------------
               total_1 = 0
               #----------------- fill allow amount with values ----------------------------------------
               res_len = len(res)
               for y in xrange(0,columns_size):
                       #------ to fill 16 coulums in Report -----------------------
                       globals()['allow_amount%s' % (y+1)] = 0
                       for m in xrange(0,columns_size):
                            if(m < res_len):
                                 #---------- read from Loan archive ---------------
                                 if(get_seq_table(self,y+1,periods[i]) == res[m]['loan_id']):  
                                      globals()['allow_amount%s' % (y+1)] = res[m]['loan_amount']
                                 
                                                                                                 
                       total_1 = total_1 + globals()['allow_amount%s' % (y+1)]
                       #-----------------------------------------------------------
               
               #-----------------------------------------------------------------------------------------
               if(len(res) > 0):
                     res_data = { 'emp_code': res[0]['emp_code'],
                                  'emp_name': res[0]['emp_name'],
                                  'total_1': round(total_1,2),
                                  'allow_amount1': round(allow_amount1,2),
                                  'allow_amount2': round(allow_amount2,2),
                                  'allow_amount3': round(allow_amount3,2),
                                  'allow_amount4': round(allow_amount4,2),
                                  'allow_amount5': round(allow_amount5,2),
                                  'allow_amount6': round(allow_amount6,2),
                                  'allow_amount7': round(allow_amount7,2),
                                  'allow_amount8': round(allow_amount8,2),
                                  'allow_amount9': round(allow_amount9,2),
                                  'allow_amount10': round(allow_amount10,2),
                                  'allow_amount11': round(allow_amount11,2),
                                  'allow_amount12': round(allow_amount12,2),
                                  'allow_amount13': round(allow_amount13,2),
                                  'allow_amount14': round(allow_amount14,2),
                                  'allow_amount15': round(allow_amount15,2),
                                  'allow_amount16': round(allow_amount16,2),
                                   }
                     top_result.append(res_data)
                     total1+=allow_amount1
                     total2+=allow_amount2
                     total3+=allow_amount3
                     total4+=allow_amount4
                     total5+=allow_amount5
                     total6+=allow_amount6
                     total7+=allow_amount7
                     total8+=allow_amount8
                     total9+=allow_amount9
                     total10+=allow_amount10
                     total11+=allow_amount11
                     total12+=allow_amount12
                     total13+=allow_amount13
                     total14+=allow_amount14
                     total15+=allow_amount15
                     total16+=allow_amount16
               i+=1
               res = {}
               res_data = {}
         total17=total1+total2+total3+total4+total5+total6+total7+total8+total9+total10+total11+total12+total13+total14+total15+total16    
         globals()['totlz']={'total1':round(total1,2),'total2':round(total2,2),'total3':round(total3,2),'total4':round(total4,2),'total5':round(total5,2),'total6':round(total6,2),'total7':round(total7,2),'total8':round(total8,2),'total9':round(total9,2),'total10':round(total10,2),'total11':round(total11,2),'total12':round(total12,2),'total13':round(total13,2),'total14':round(total14,2),'total15':round(total15,2),'total16':round(total16,2),'total17':round(total17,2),}
         return top_result
        
    def _get_ded_allow_name(self,data):
         res_data = {}
         top_result = []
         allow_ded_res = {}
         #----------------- set all allownces name to NULL at fisrt ----------
         for i in xrange(1,(columns_size+1)):
             globals()['allow_name%s' % i] = ''
         #------------------------------------------------------------
         where_clause = " WHERE active = TRUE  " 
         loan_obj = self.pool.get('hr.loan')
         loan_ids = loan_obj.search(self.cr,self.uid,['|',('company_ids','=',False),('company_ids', 'in', (data['company_id'][0]))])
         if loan_ids:
            where_clause += " and id in (%s) " % ','.join(map(str, loan_ids))
         self.cr.execute('''SELECT name as allow_name FROM  hr_loan''' + where_clause +''' Order by id ASC ''')
         allow_ded_res = self.cr.dictfetchall()
         
         #----------------- fill allow name with values ------------------------
         for y in xrange(0,columns_size):
             if(y < len(allow_ded_res)):
                  globals()['allow_name%s' % (y+1)] = allow_ded_res[y]['allow_name']
             else:
                  globals()['allow_name%s' % (y+1)] = ''
         #-----------------------------------------------------------------------
         res_data = { 'allow_name1': allow_name1,
                             'allow_name2': allow_name2,
                             'allow_name3': allow_name3,
                             'allow_name4': allow_name4,
                             'allow_name5': allow_name5,
                             'allow_name6': allow_name6,
                             'allow_name7': allow_name7,
                             'allow_name8': allow_name8,
                             'allow_name9': allow_name9,
                             'allow_name10': allow_name10,
                             'allow_name11': allow_name11,
                             'allow_name12': allow_name12,
                             'allow_name13': allow_name13,
                             'allow_name14': allow_name14,
                             'allow_name15': allow_name15,
                             'allow_name16': allow_name16,
                           }
         
         top_result.append(res_data)
         return top_result
    def _get_ded_allow_total(self):

            return [globals()['totlz']]
 
report_sxw.report_sxw('report.loan.details', 'hr.loan.archive', 'addons/hr_loan/report/loan_details.rml' ,parser=loan_details_report,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
