# -*- encoding: utf-8 -*-
from report import report_sxw
import time
from osv import osv, fields
from tools.translate import _
import mx
import mx.DateTime 
class hr_expenses(report_sxw.rml_parse):    
    def __init__(self, cr, uid, name, context):
        super(hr_expenses, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'name':self._get_name,             
            'expenses':self._get_expenses, 
            'total':self._get_totals,             
        })    
    def _get_name(self, data): 
        return  self.pool.get('hr.allowance.deduction').browse(self.cr,self.uid,data).name
      
    def _get_expenses(self, data):        
        self.gobal_total=0
        self.gobal_count=0
        top_res=[]
        for dep in data['department_ids']:
            local_row=[]
            received_res=[]
            excluded_ids=[0]
            emp_ids=[]
            emp_dicts=[]
            trans_ids=self.pool.get('hr.process.archive').search(self.cr,self.uid,['|',('previous','=',dep),('reference','=','hr.department'),('date','<=',data['end_date']),('date','>=',data['start_date'])])
            if trans_ids:
                for trans in self.pool.get('hr.process.archive').browse(self.cr,self.uid,trans_ids):
                    emp_dic={
		            'emp_id':trans.employee_id.id,
	    	            'emp_obj':trans.employee_id,
		            'start':data['start_date'],
			    'end' :data['end_date'],
			    'dep' :dep,
                           }
                    if trans.department_id.id==dep and trans.employee_id.id not in emp_ids and trans.employee_id.payroll_id.id in data['payroll_ids'] :
                        emp_dic.update({'start': trans.date,})
                        emp_dicts.append(emp_dic)
                        excluded_ids.append(trans.employee_id.id)
                        emp_ids.append(trans.employee_id.id)
                    elif trans.previous.id==dep and trans.employee_id.id not in emp_ids and trans.employee_id.payroll_id.id in data['payroll_ids'] :
                        emp_ids.append(trans.employee_id.id)
                        emp_dic.update({'end': trans.date,})
                        emp_dicts.append(emp_dic)
            dom=[('payroll_id','in',data['payroll_ids']),('department_id','=',dep),('id','not in',excluded_ids)]
            empl_ids=self.pool.get('hr.employee').search(self.cr,self.uid,dom)
            #print empl_ids,"empl_idssssssssssssssss"
            if empl_ids :
                for emp in self.pool.get('hr.employee').browse(self.cr,self.uid,empl_ids):
                    emp_dic={
		            'emp_id':emp.id,
	    	            'emp_obj':emp,
		            'start':data['start_date'],
			    'end' :data['end_date'],
			    'dep' :dep,
                           }
                    emp_dicts.append(emp_dic)
                    #print emp_dicts,"emp_dicttttttttttttttt"
                    emp_ids.append(emp.id)
            if emp_dicts :             
                received_res=self._get_main(emp_dicts,emp_ids,data) 
                #print received_res,"received_res"         
                if received_res:
                    local_row.append(self.pool.get('hr.department').browse(self.cr,self.uid,[dep])[0].name)
                    local_row.append(received_res)
                    top_res.append(local_row)
        if top_res :
            return top_res
        else:
            raise osv.except_osv(_('Warning !'),
		            _('Sorry No result to show during this period of time!'))  
    
    def _range_months(self, date1,date2 ):
        years=['0']
        months=['0']
        start =mx.DateTime.Parser.DateTimeFromString(date1)
        end =mx.DateTime.Parser.DateTimeFromString(date2)
        if start.year==end.year:
            years.append(start.year)
            [months.append (str(mon)) for mon in range(start.month, (end.month+1))]
        else:
            years.append(start.year)
            years.append(end.year)
            [months.append (str(mon)) for mon in range(start.month, 13)]
            [months.append (str(mon)) for mon in range(1, (end.month+1))]
        #print tuple(years),"yearssssss99999999999"
        #print tuple(months),"monthssssssssss99999999999"
        return tuple(years),tuple(months) 

    def _get_main(self, emp_dicts,emp_ids,data ):
        local_total=0
        counter=0
        loco_res=[]
        def _shaping(self,result,counter):
            o_dic={
		   'no':counter,
	    	   'code':loc['emp_obj'].emp_code,
		   'name':loc['emp_obj'].name,
		   'amount' :round(result['amount'],2),
                              }
            loco_res.append(o_dic)
        if data['selection']=='1':
            for loc in emp_dicts :
                years=self._range_months(loc['start'],loc['end'])[0]
                months=self._range_months(loc['start'],loc['end'])[1]
                dom=[('department_id','in',data['department_ids']),('state','=','approved'),('allowance_id','=',data['allowance'][0])]
                add_ids=self.pool.get('hr.additional.allowance').search(self.cr,self.uid,dom)
                #print add_ids,"adddddddd_ids"
                if add_ids:
                 for emp in self.pool.get('hr.additional.allowance').browse(self.cr,self.uid,add_ids):
                          period =mx.DateTime.Parser.DateTimeFromString(emp.period_id.date_start)
                          print period,"perioooooooooood"

                 if period.month in months and period.year in years:
                  self.cr.execute(''' SELECT 
                  sum (l.amounts_value) as amount
                  FROM 
                  public.hr_additional_allowance d,
                  public.hr_additional_allowance_line l

	          WHERE 

			  l.state='implement' and 
			  l.employee_id=%s 
			  ''',(loc['emp_id'],))
                  overtime=self.cr.dictfetchone()
                  #print "add_overtimmmmmmmmmmmmmme",overtime
                  if overtime['amount']>0:
                    counter+=1
                    local_total+=overtime['amount']
                    _shaping(self,overtime,counter)
        elif data['selection']=='2':
            for loc in emp_dicts :
                years=self._range_months(loc['start'],loc['end'])[0] 
                #print years,"yeaaaaaars"
                months=self._range_months(loc['start'],loc['end'])[1]
                
               
                self.cr.execute('''  SELECT sum (m.amount) as amount
                 FROM 
                 public.hr_allowance_deduction_archive m,
                 public.hr_payroll_main_archive p
                 WHERE 
                 m.main_arch_id=p.id and
                 p.month in %s  and
                 p.year in %s and  
                 p.employee_id=%s and
                 m.allow_deduct_id=%s''',(months,years,loc['emp_id'],data['allowance'][0]))
                overtime=self.cr.dictfetchone()
                #print overtime,"overtimmmmmmmmmmme"
                if overtime['amount']>0:
                    counter+=1
                    local_total+=overtime['amount']
                    _shaping(self,overtime,counter)
        elif data['selection']=='3':
            for loc in emp_dicts :
                self.cr.execute('''  SELECT sum (amount) as amount
                FROM 
                public.hr_subsidy 
                WHERE 

                employee_id=%s and
                allowance=%s and
                date >= %s and
                date <=%s''',(loc['emp_id'],data['allowance'][0],loc['start'],loc['end']))
                overtime=self.cr.dictfetchone()
                if overtime['amount']>0:
                    counter+=1
                    local_total+=overtime['amount']
                    _shaping(self,overtime,counter)
        if loco_res:
            self.gobal_total+=local_total
            self.gobal_count+=counter
            t_dic={'no':'','code':'','name':  u'الإجمالي','amount' :round(local_total,2),}
            loco_res.append(t_dic)
            return loco_res
         

    def _get_totals(self ):
        return {'total':round(self.gobal_total,2),'count':self.gobal_count,}

report_sxw.report_sxw('report.hr.expenses',
                       'hr.payroll.main.archive',
                       'addons/hr_extra_report/report/hr_payroll_expenses.rml',header=True,
                       parser=hr_expenses)
