import time
from report import report_sxw
import calendar
import datetime
import pooler

class employee_loans(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(employee_loans, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           'time': time,
            'line':self._getShop,
            'date':self._getloan,
            'emp':self.get_employee,
            'amount':self._getamount,
            'total':self.get_total,
            
        })
    
    
        self.context = context
            #___________________________ loan name___________________________________
    def _getShop(self,data):      
        result = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.loan')
        ser=emp.search(self.cr, self.uid, [('id', '=',data['loan_id'][0] )])
        result = emp.browse(self.cr,self.uid,ser)
        return result

    def _getloan(self,data):
        pero=[]
        globals()['per']=[]
        globals()['totalz']={'total':0,'paid':0,'remain':0,'instal':0,}
        res = {}
        res_data = {}
        top_result = []
        loan = data['form']['loan_id'][0]
        total=0
        paids=0
        remain=0
        instal=0
        #-------------------------- function to retrieve paid amount for employee ---------
        def get_total_loan(self,emp,loan):
           res_loan = {}
           self.cr.execute("SELECT COALESCE(sum(loan_amount),0) as total FROM public.hr_loan_archive where employee_id = %s AND loan_id = %s"%(emp,loan))
           res_loan = self.cr.dictfetchall()
           return res_loan[0]['total']
           #----------------------------------------------------------------------------------
        self.cr.execute('''SELECT 
  hr_loan."name" AS loan_name, 
  COALESCE(l.installment_amount,0) AS installment_amount, 
  l.employee_id, 
  COALESCE(l.loan_amount,0) AS loan_amount, 
  l.id as loan_id,
  l.start_date AS start_date
FROM 
  public.hr_employee_loan l, 
  public.hr_loan
WHERE 
  l.loan_id = hr_loan.id AND
  l.loan_id = %s AND
  l.employee_id in %s AND
  l.state not in ('draft' ,'requested','rejected')
''',(loan,tuple (data['form']['employee_ids']))) 
        res = self.cr.dictfetchall()
        i = 0        
        while i < len(res):
                    loan_id = res[i]['loan_id']
                    emp     =  res[i]['employee_id']
                    self.cr.execute('''
SELECT resource_resource.name as name ,hr_employee.emp_code as code 
from resource_resource ,hr_employee 
where
hr_employee.resource_id=resource_resource.id
and 
 hr_employee.id =%s '''% emp)
                    res_name = self.cr.dictfetchall()
                    paid = get_total_loan(self,emp,loan_id)
                    if paid:
                       globals()['per'].append(emp)
                    res_data = { 'no': str(i+1),
                                'installment_amount': round(res[i]['installment_amount'],2),
                                'start_date': res[i]['start_date'],
                                'loan_amount': round(res[i]['loan_amount'],2),
                                'paid_amount': round(paid,2),
                                'net_amount': round(res[i]['loan_amount']-paid,2),
                                'loan_name': res[i]['loan_name'],
                                'name':res_name[0]['name'],
                                'code':res_name[0]['code'],
                                }
                    total+=res[i]['loan_amount']
                    paids+=paid
                    remain+=res[i]['loan_amount']-paid
                    instal+=res[i]['installment_amount']
                    top_result.append(res_data)
                    i+=1
        globals()['totalz']={'total':round(total,2),'paid':round(paids,2),'remain':round(remain,2),'instal':round(instal,2),}
        return top_result


    def _getamount(self,data , emp):
        self.cr.execute("SELECT CAST(l.create_date AS date) as loan_date, round((l.loan_amount),2) as loan_amount,payment_type as pay \
from  hr_loan_archive as l left join hr_employee_loan as n on (l.loan_id=n.id) left join hr_employee as e on (l.employee_id=e.id)  where e.id=%s and n.loan_id=%s",(emp, data['form']['loan_id'][0])) 
        return self.cr.dictfetchall()

    def get_employee(self,form):
        result = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.employee')
        result = emp.browse(self.cr,self.uid, globals()['per'])
        return result

    def get_total(self):
        return globals()['totalz']

report_sxw.report_sxw('report.employee.loan', 'hr.loan.archive', 'addons/hr_loan/report/employee_loans.rml' ,parser=employee_loans)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
