import time
from report import report_sxw
import calendar
import datetime
import pooler

class loans_situation_rep(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loans_situation_rep, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getShop,
            'date':self._getloan,
            'emp':self.get_employee,
            'amount':self._getamount,
            'total':self.get_total,
          
        })
    def _getShop(self,data):      
        result = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.loan')
        ser=emp.search(self.cr, self.uid, [('id', '=',data['loan_id'][0] )])
        result = emp.browse(self.cr,self.uid,ser)
        return result

    def _getloan(self,data):
        pero=[]
        globals()['per']=[]
        globals()['totalz']={'total':0.0,'paid':0.0,'remain':0.0,'instal':0.0,}
        res = {}
        res_data = {}
        top_result = []
        loan = data['form']['loan_id'][0]
        total=0.0
        paids=0.0
        remain=0.0
        instal=0.0
        #-------------------------- function to retrieve paid amount for employee ---------
        def get_total_loan(self,emp,loan):
            res_loan = {}
            self.cr.execute("SELECT sum(loan_amount) as total FROM public.hr_loan_archive where employee_id = %s AND loan_id = %s"%(emp,loan))
            res1 = self.cr.dictfetchall()
            res_loan  =res1[0]['total'] or 0.0
        self.cr.execute('''SELECT  hr_loan."name" AS loan_name, hr_employee_loan.installment_amount,hr_employee_loan.employee_id, 
                           hr_employee_loan.loan_amount,hr_employee_loan.id as loan_id,hr_employee_loan.start_date
                           FROM public.hr_employee_loan,public.hr_loan
                           WHERE hr_employee_loan.loan_id = hr_loan.id
                           AND public.hr_employee_loan.loan_id = %s and public.hr_employee_loan.employee_id in %s ''',(loan,tuple (data['form']['emp_id']))) 
        res = self.cr.dictfetchall()
        i = 0
        while i < len(res):
                    loan_id = res[i]['loan_id']
                    emp     =  res[i]['employee_id']
                    globals()['per'].append(emp)
                    self.cr.execute(''' SELECT resource_resource.name as name ,hr_employee.emp_code as code 
                                        FROM resource_resource ,hr_employee 
                                        WHERE hr_employee.resource_id=resource_resource.id
                                        AND hr_employee.id =%s '''% emp)
                    res_name = self.cr.dictfetchall() 
                    paid = get_total_loan(self,emp,loan_id) or 0.0
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
        self.cr.execute("SELECT CAST(l.create_date AS date) as loan_date, l.loan_id as loan_name, round((l.loan_amount),2) as loan_amount,payment_type as pay from  hr_loan_archive as l left join hr_employee_loan as n on (l.loan_id=n.id) left join hr_employee as e on (l.employee_id=e.id)  where e.id=%s and n.id=%s",(emp, data['form']['loan_id'][0])) 
        res = self.cr.dictfetchall()
        return res

    def get_employee(self,form):
        result = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.employee')
        result = emp.browse(self.cr,self.uid, globals()['per'])
        return result

    def get_total(self):
        return globals()['totalz']

report_sxw.report_sxw('report.loans.situation.rep', 'hr.loan.archive', 'addons/hr_loan/report/loans_situation_rep.rml' ,parser=loans_situation_rep)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
