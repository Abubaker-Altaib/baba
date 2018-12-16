import mx
from report import report_sxw
from osv import osv
from tools.translate import _
import time

 
class additional_wage(report_sxw.rml_parse):
 def __init__(self, cr, uid, name, context):
        super(additional_wage, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._pars,
            #'prohibit':self._prohibit,
            'employee':self._get_emp,
            'total':self._total,
            'totals':self._totals,
            'count':self._count,
        })
        self.cr = cr
        self.uid = uid
        self.context = context

 globals()['dic']={}

 
 def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('hr.additional.allowance').browse(self.cr, self.uid, ids, self.context):
            '''if obj.state not in ('second_validate','approved'):
		            raise osv.except_osv(_('Error!'), _('You can not print this the additional wage has not been approved yet!'))''' 

        return super(additional_wage, self).set_context(objects, data, ids, report_type=report_type)
 
 def _pars(self,d):        
        res = amount_to_text_ar(d)
        return res


 def _count(self,h):        
        i=h.id        
        self.cr.execute(''' 
SELECT 
   count(public.hr_employee_mission_line.id) as nom
FROM 
  public.hr_employee_mission, 
  public.hr_employee_mission_line
WHERE 
  hr_employee_mission.id = hr_employee_mission_line.emp_mission_id AND
    hr_employee_mission.id=%s
'''%(i))
        res=self.cr.dictfetchall()
       
        return res[0]['nom']
 def _totals(self):        
 
        res = globals()['dic']
        #print">>>>>>>>>>>>>>>>>>>>>>eeeeeeeeeeeeeeeeeeeeee",res
        return res


 def _total(self,h):
        total=0        
        i=h.id        
        self.cr.execute(''' 
SELECT 
  hr_employee_mission.id , 
  hr_employee.name_related as name,
  res_partner_bank.acc_number as bank, 
  hr_employee_mission_line.tax as tax, 
  hr_employee_mission_line.stamp as imprint,
  hr_employee_mission_line.gross_amount as amount, 
  hr_employee_mission_line.mission_amounts as gross, 
  hr_employee_mission_line.amount as wage
FROM 
  public.hr_employee_mission, 
  public.hr_employee_mission_line, 
  public.hr_employee,
  public.res_partner_bank
WHERE 
  hr_employee_mission.id = hr_employee_mission_line.emp_mission_id AND
  hr_additional_allowance_line.employee_id= hr_employee.id and
  hr_employee.bank_account_id= res_partner_bank.id and
    hr_employee_mission.id=%s 
'''%(i))
        res=self.cr.dictfetchall()
        if (res):             
              for e in res:
                  total+=e['amount']
        return round(total,2)

 def _get_emp(self,h):
        total=0        
        i=h.id
        j = 0
        res_data = {}
        glo_data = {}
        top_result = []
        res = {}   
        total_days=0
        total_tax=0
        total_imprint=0
        total_wage=0
        total_net=0
        total_gross=0
        count=0
        self.cr.execute(''' 
SELECT 
  hr_employee_mission.id , 
   hr_employee.name_related as name, 
   res_partner_bank.acc_number as bank,
  hr_employee_mission_line.tax as tax, 
 hr_employee_mission_line.days as days, 
  hr_employee_mission_line.stamp as imprint, 
  hr_employee_mission_line.gross_amount as amount, 
  hr_employee_mission_line.mission_amounts as gross, 
  hr_employee_mission_line.amount as wage
FROM 
  public.hr_employee_mission, 
  public.hr_employee_mission_line, 
  public.hr_employee,
  public.res_partner_bank
WHERE 
  hr_employee_mission.id = hr_employee_mission_line.emp_mission_id AND
  hr_employee_mission_line.employee_id = hr_employee.id and
  hr_employee.bank_account_id= res_partner_bank.id and
    hr_employee_mission.id=%s 
'''%(i))
        res=self.cr.dictfetchall()
        while j < len(res):
            count+=1
            taxs=0
            impri=0
            if (res[j]['tax'] > 0):
                taxs=res[j]['tax']
            if (res[j]['imprint'] > 0):
                impri=res[j]['imprint']

            total_net+=res[j]['amount']
            total_gross+=res[j]['gross']
            total_wage+=res[j]['wage']
            total_imprint+=impri
            total_tax+=taxs
            total_days+=res[j]['days']
            res_data = { 'no': j+1,
                     'amount': round(res[j]['amount'],2),
                     'gross': round(res[j]['gross'],2),
                     'wage': round(res[j]['wage'],2),
                     'imprint': res[j]['imprint'],
                     'days':  res[j]['days'],
                     'tax':  round(res[j]['tax'],2),
                     'name':  res[j]['name'],
                     'bank': res[j]['bank'],
                   #  'salary_emp':  res[j]['salary_emp'],
                     #'code':  res[j]['code'],
                    }
               
            top_result.append(res_data)
            j+=1
        glo_data = {
                  'no':count,
                  'wage': round( total_wage,2),
                  'imprint': round(total_imprint,2),
                  'days':  total_days,
                  'tax':  round(total_tax,2),
                  'net':round(total_net,2),
                  'gross':round(total_gross,2),
           }
        globals()['dic']=glo_data
        #print">>>>>>>>>>>>>>>>>>>>>>",globals()['dic']
        res = {}
        res_data = {}
               
         
        return top_result                
        
 

report_sxw.report_sxw('report.mission_allowance', 'hr.employee.mission', 'addons/hr_ntc_custom/report/mission_allowance.rml' ,parser=additional_wage ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
