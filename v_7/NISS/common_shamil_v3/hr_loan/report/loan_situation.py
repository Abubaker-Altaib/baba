import time
from report import report_sxw
import calendar
import datetime
import pooler

class loan_situation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loan_situation, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'emp':self.get_employee,
            'loan':self._get_loan,
            'total':self.get_total,
        })
    
    def get_employee(self,form):
        result = []
        periods = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.employee')
        
        result = emp.browse(self.cr,self.uid, form['emp_id'])
        return result

    def get_total(self):
        return globals()['re_res']

    def _get_loan(self,h):
        loan_id=[]
        return_res=[]
        remain_total=0
        paid_total=0
        loan_total=0
        instal_total=0
        instal_no =0
        globals()['re_res']={'remain_total':0,'paid_total':0,'loan_total':0,'instal_total':0,'instal_no':0,}
        self.cr.execute('''select id from hr_employee_loan where employee_id=%s'''%h)
        res=self.cr.fetchall()
        if len(res)>0: 
           for n in res:
               loan_id.append(n[0])
        if len(loan_id)>0:
          self.cr.execute('''
SELECT 
COALESCE(l.installment_amount,0) as instl,l.loan_amount as loan,n.name as loan_name,
l.start_date as s_date, COALESCE(ceil( l.loan_amount/l.installment_amount),0) as num 
,(select sum(loan_amount)  from hr_loan_archive where loan_id=l.id and employee_id=l.employee_id GROUP BY employee_id) as paid
from
 hr_employee_loan as l 
 left join hr_loan  as n on (n.id=l.loan_id)
where
     l.id in %s and l.employee_id=%s and l.state not in ('draft','rejected','requested')
group by
l.installment_amount,l.loan_amount ,l.start_date,l.total_installment,l.id,l.employee_id,loan_name
''',(tuple(loan_id),h))
          re=self.cr.dictfetchall()
        #print"------------------------------------------------",re
          if len(re)>0:
            oc=0
            for b in re:
                oc+=1
                paid=0
                if (b['paid'] > 0):
                     paid=b['paid']
                else :
                     paid=0
                dic={
                       'no':oc,
                       'loan':round(b['loan'],2),
                       'instl':round(b['instl'],2),
                       'loan_name':b['loan_name'],
                       's_date':b['s_date'],
                       'num':int(b['num']),
                       'paid':round(paid,2),
                       'remain':round((b['loan']-paid),2),
                        }
                return_res.append(dic) 
                remain_total+=b['loan']-paid
                paid_total+=paid
                loan_total+=b['loan']
                instal_total+=b['instl']
                instal_no +=b['num']
                globals()['re_res']={'remain_total':round(remain_total,2),'paid_total':round(paid_total,2),'loan_total':round(loan_total,2),'instal_total':round(instal_total,2),'instal_no':instal_no}
          return return_res
        else:
          return [{'no': 0,}]
                      
report_sxw.report_sxw('report.loan.situation', 'hr.loan.archive', 'addons/hr_loan/report/loan_situation.rml' ,parser=loan_situation)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
