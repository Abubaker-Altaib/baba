import time
from report import report_sxw
import calendar
import datetime
import pooler


class common_loan_rep(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(common_loan_rep, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line1':self._getShop2,
            'line_loan':self._getShop1,
            'get_loans':self.get_loan,
            'total':self._get_total,
            'total2':self._get_total1,
            'get_emp':self.get_employee1,

          
        })
        self.context = context
            #___________________________ loan name___________________________________
    
   
    def get_loan(self,form):
        result = []
        periods = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.loan')
        
        result = emp.browse(self.cr,self.uid, form['loans_id'])
        return result
    def _getShop2(self,data,i):
        periods=[]

       

        self.cr.execute('''SELECT 
  hr_employee_loan.name as name, 
  hr_loan_archive.loan_amount as mount
FROM 
  public.hr_employee_loan, 
  public.hr_loan_archive, 
  public.hr_employee, 
  public.resource_resource
WHERE 
  hr_employee_loan.id = hr_loan_archive.loan_id AND
  hr_loan_archive.employee_id = hr_employee.id AND
  hr_employee.resource_id = resource_resource.id AND
  hr_employee.id=%s AND
  hr_loan_archive.month =%s AND
  hr_loan_archive.year =%s 
''',(i, data['form']['month'],data['form']['year'],)) 
        res = self.cr.dictfetchall()
        return res


    def get_employee1(self,form):
        result = []
        periods = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.employee')
        

        result = emp.browse(self.cr,self.uid, form['employee_ids'])
        return result
    def get_total(self):
        return globals()['totalz']

    def get_employee(self,form):
        result = []
        per=[]
        emp = pooler.get_pool(self.cr.dbname).get('hr.employee')
        result = emp.browse(self.cr,self.uid, per)
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
           self.cr.execute("SELECT sum(loan_amount) as total FROM public.hr_loan_archive where employee_id = %s AND loan_id = %s"%(emp,loan))
           print emp,loan,"emp","loan"
           res_loan = self.cr.dictfetchall()
           print res_loan,"res_loan"
           if(res_loan[0]['total'] != False):
                return res_loan[0]['total']
           else:
                return 0
           #----------------------------------------------------------------------------------
        self.cr.execute('''SELECT 
  hr_loan."name" AS loan_name, 
  hr_employee_loan.installment_amount, 
  hr_employee_loan.employee_id, 
  hr_employee_loan.loan_amount, 
  hr_employee_loan.id as loan_id,
  hr_employee_loan.start_date
FROM 
  public.hr_employee_loan, 
  public.hr_loan
WHERE 
  hr_employee_loan.loan_id = hr_loan.id AND
  public.hr_employee_loan.loan_id = %s and
public.hr_employee_loan.employee_id in %s 
''',(loan,tuple (data['form']['employee_ids']))) 
        res = self.cr.dictfetchall()
        i = 0
                
        while i < len(res):
                    loan_id = res[i]['loan_id']
                    emp     =  res[i]['employee_id']
                    globals()['per'].append(emp)
                    self.cr.execute('''
SELECT resource_resource.name as name ,hr_employee.emp_code as code 
from resource_resource ,hr_employee 
where
hr_employee.resource_id=resource_resource.id
and 
 hr_employee.id =%s '''% emp)
                    res_name = self.cr.dictfetchall()
                    paid = get_total_loan(self,emp,loan_id)
                    res_data = {'no': str(i+1),
                                'num': str(i+1),
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
                    print top_result,"topresult"
                    i+=1
        globals()['totalz']={'total':round(total,2),'paid':round(paids,2),'remain':round(remain,2),'instal':round(instal,2),}
        return top_result

    def _getShop(self,data):      
        result = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.loan')
        ser=emp.search(self.cr, self.uid, [('id', '=',data['loan_id'][0] )])
        result = emp.browse(self.cr,self.uid,ser)
        return result

    def _get_total1(self,data,i):
            result = []
            periods = []
            emp = pooler.get_pool(self.cr.dbname).get('hr.loan.archive')

            r=0
            ser=emp.search(self.cr, self.uid, [('employee_id', '=', i),('month', '=', data['form']['month']),('year', '=', data['form']['year'])])
            #print "serarch",ser
            result = emp.browse(self.cr,self.uid, ser)
            #print result
            for w in result:
                r+=round(w.loan_amount,2)
        #print "rrrrrrr",r
            return r



    def _getShop1(self,data,i):
        result=[]
        c= data['form']['company_id']

        self.cr.execute("SELECT e.sequence,e.emp_code AS employee_code,resource_resource.name AS employee_name,round(m.loan_amount,2) AS loan_amount,b.name AS loan_name FROM  hr_loan_archive AS m left join hr_employee_loan AS f on (f.id=m.loan_id) left join hr_loan b on (f.loan_id=b.id) left join hr_employee e on (m.employee_id=e.id) left join resource_resource on (e.resource_id=resource_resource.id) WHERE b.id = %s and m.month=%s and  m.year=%s order by e.sequence",(i, data['form']['month'],data['form']['year'],))   
        res = self.cr.dictfetchall()
        i = 0
        while i < len(res):
              res_data={ 'no': str(i+1),
                                'employee_code': res[i]['employee_code'],
                                'employee_name': res[i]['employee_name'],
                                'loan_amount':res[i]['loan_amount'],
                               
                                }
              
              result.append(res_data)
              i+=1
        
        return result



    def _get_total(self,data,i):
            result = []
            periods = []
            emp = pooler.get_pool(self.cr.dbname).get('hr.loan.archive')

            r=0
            ser_fixed=pooler.get_pool(self.cr.dbname).get('hr.employee.loan').search(self.cr, self.uid, [('loan_id', '=', i)])

            ser=emp.search(self.cr, self.uid, [('loan_id', 'in' , tuple(ser_fixed)),('month', '=', data['form']['month']),('year', '=', data['form']['year'])])
            result = emp.browse(self.cr,self.uid, ser)
            for w in result:
                r+=round(w.loan_amount,2)

            return r

report_sxw.report_sxw('report.common.loan.rep', 'hr.employee.loan', 'addons/hr_loan/report/common_loan_rep.rml' ,parser=common_loan_rep)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
