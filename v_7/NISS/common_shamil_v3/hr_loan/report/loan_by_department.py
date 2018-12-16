import time
from report import report_sxw
import calendar
import datetime
from openerp.osv import osv
from openerp.tools.translate import _


class loan_by_department(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(loan_by_department, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line':self._getShop,
            'date':self._getloan,
            'deps':self._get_deps,
            'total':self.get_total,
            'final':self.total_total,
          
        })

    def _getShop(self,data):      
        result = []
        emp = self.pool.get('hr.loan')
        ser=emp.search(self.cr, self.uid, [('id', '=',data['loan_id'][0] )])
        result = emp.browse(self.cr,self.uid,ser)
        return result

    def _getloan(self,data, d_id):
        total=0
        top_result=[]
        self.cr.execute('''SELECT 
                  resource_resource.name  as name, 
                  hr_employee_loan.loan_amount as loan , 
                  hr_employee_loan.start_date as date,
                  hr_employee.emp_code as code
                FROM 
                  public.hr_employee_loan,
                  public.resource_resource ,
                  public.hr_employee
                WHERE 
                  hr_employee.resource_id=resource_resource.id
                  and public.hr_employee_loan.loan_id = %s 
                  and public.hr_employee_loan.department_id =%s 
                  and hr_employee_loan.employee_id= hr_employee.id
                  and hr_employee_loan.state not in ('draft','requested','rejected')
                  and   hr_employee_loan.start_date between %s  and %s ''',(data['loan_id'][0],d_id,data['start'],data['to_date'])) 
        res = self.cr.dictfetchall()
        i = 0
        while i < len(res):
              res_data={ 'no': str(i+1),
                                'start_date': res[i]['date'],
                                'loan': res[i]['loan'],
                                'name':res[i]['name'],
                                'code':res[i]['code'],
                                }
              total+=res[i]['loan']
              top_result.append(res_data)
              i+=1
        globals()['totalz']={'total':round(total,2)}
        return top_result


    def _get_deps(self,data ):
        pero=[]
        
        self.cr.execute('''SELECT distinct hr_employee_loan.department_id as de
                        FROM  public.hr_employee_loan
                        WHERE hr_employee_loan.loan_id =%s
                        AND hr_employee_loan.department_id in %s
                        AND hr_employee_loan.start_date between %s and %s
                        ''',(data['loan_id'][0],tuple(data['department_id']) ,data['start'],data['to_date'])) 
        res = self.cr.dictfetchall()
        if not res:
				 raise osv.except_osv(_('Warning'), _('There is no employee take the selected loan in selected departments and period'))
        pero=[]
        for b in res:
              pero.append(b['de'])
        result = []
        dep = self.pool.get('hr.department')
        result = dep.browse(self.cr,self.uid, pero)
        globals()['ids']=pero
        return result

    def get_total(self):
        return globals()['totalz']

    def total_total(self,data):
        if len(globals()['ids'])>0: 
           self.cr.execute('''SELECT sum(hr_employee_loan.loan_amount) as loan  ,count(id) as count
                    FROM public.hr_employee_loan
                    WHERE public.hr_employee_loan.loan_id = %s 
                    AND public.hr_employee_loan.department_id in %s
                    AND hr_employee_loan.state not in ('draft','requested','rejected')
                    AND hr_employee_loan.start_date between %s and %s ''',(data['loan_id'][0],tuple(globals()['ids']) ,data['start'],data['to_date'])) 
           res = self.cr.dictfetchall()
           return res[0]

report_sxw.report_sxw('report.loan.by.department', 'hr.employee.loan', 'addons/hr_loan/report/loan_by_department.rml' ,parser=loan_by_department)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
