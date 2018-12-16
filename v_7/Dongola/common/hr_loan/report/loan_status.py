import time
import re
from report import report_sxw
import calendar
import datetime
from openerp.osv import osv
from openerp.tools.translate import _


class loan_status(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loan_status, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'loan':self.get_loan,
            'name':self.get_name,
            'employee':self._get_emp,
        })
    
    def get_loan(self):
        return globals()['re_res']

    def get_name(self,data):
        self.cr.execute('''select name as loan_name from hr_loan where id=%s  '''%data['loan'][0])
        res=self.cr.dictfetchall()
        return res

    def _get_emp(self,data):
        ret_res=[]
        res_data={}
        remain=0
        remain_total=0
        paid_total=0
        loan_total=0
        instal_total=0
        instal_no =0
        self.cr.execute(''' 
              SELECT r.name AS emp, e.emp_code as code,COALESCE(l.installment_amount,0) as instl,l.loan_amount as loan,e.id,
              l.start_date as s_date, COALESCE(ceil( l.loan_amount/l.installment_amount),0) as no 
              ,(select sum(loan_amount)  from hr_employee_loan where loan_id=l.id and employee_id=e.id GROUP BY employee_id ) as paid
              FROM hr_employee as e 
              LEFT JOIN resource_resource as r on (e.resource_id=r.id) 
              LEFT JOIN hr_employee_loan as l on (e.id=l.employee_id)
              WHERE l.loan_id=%s and l.start_date between %s and %s 
              and l.state not in ('draft','requested','rejected')
              GROUP BY r.name , e.emp_code ,l.installment_amount,l.loan_amount ,l.start_date,l.total_installment,e.id,l.id''' ,
              (data['loan'][0],data['start_date'],data['end_date']))
        res=self.cr.dictfetchall()
        i=0
        if not res:
		   raise osv.except_osv(_('Warning'), _('There is no employee take the selected loan in selected period'))
        while(len(res) > i): 
                if (res[i]['paid'] > 0):
                     paid=res[i]['paid']
                else :
                     paid=0
                remain=res[i]['loan']-paid  
                res_data = { 'paid': round(paid,2),
                             'num': str(i+1),
                             'code': res[i]['code'],
                             'emp': res[i]['emp'],
                             'instl': round(res[i]['instl'],2),
                             'loan': round(res[i]['loan'],2),
                             'date': res[i]['s_date'],
                             'inum': int(res[i]['no']),
                             'remain': round((res[i]['loan']-paid),2),
                           }
                remain_total+=res[i]['loan']-paid
                paid_total+=paid
                loan_total+=res[i]['loan']
                instal_total+=res[i]['instl']
                instal_no +=res[i]['no']
                ret_res.append(res_data)
                i+=1
        globals()['re_res']={'remain_total':round(remain_total,2),'paid_total':round(paid_total,2),'loan_total':round(loan_total,2),'instal_total':round(instal_total,2),'instal_no':int(instal_no)}
        return ret_res

report_sxw.report_sxw('report.loan.status', 'hr.employee.loan', 'addons/hr_loan/report/loan_status.rml' ,parser=loan_status ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
