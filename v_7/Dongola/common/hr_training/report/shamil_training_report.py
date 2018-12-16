from report import report_sxw
import time
import math
from osv import osv, fields
from tools.translate import _


class shamil_training_report(report_sxw.rml_parse):    
    def __init__(self, cr, uid, name, context):
        super(shamil_training_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time':time,
            'dept' :self._get_dept,
            'count':self.count_emps,
            'deps':self.get_deps,
            'count_inside':self.count_emps_inside,
            'dept_inside':self.get_dept_inside,
            'count_outside':self.count_emps_outside,
            'dept_outside':self.get_dept_outside,
            'count_tr':self._count_trainee,
            'dept_tr':self.get_dept_tr,
            'dept_student':self.get_dept_student,
            'count_student':self._count_student,
            'dept_graduate':self.get_dept_graduate,
            'count_graduate':self._count_graduate,
            'percentage':self.get_percentage,
            'amount':self.get_amount,
            'enrich':self.get_enrich,
            
            
        })
        self.percentage =0
        self.student=0
        self.trainee=0
        #self.graduate=0 
        self.total =0 

    def get_child_dept(self,cr,uid,dept_id,context=None):
        department_obj = self.pool.get('hr.department')
        reads = department_obj.read(self.cr, self.uid, [dept_id], ['id','child_ids'], context=context)
        child_ids=[]
        for record in reads:
           if record['child_ids']:
              child_ids=record['child_ids']
              for child in record['child_ids']:
                 child_ids+=self.get_child_dept(self.cr,self.uid,child,context=context)
        return child_ids
###############################department#################################
    def get_deps(self,d_id):
        self.cr.execute('''
SELECT distinct
pd.id as ss
FROM 
hr_department as pd
WHERE 
  pd.parent_id =%s
'''%d_id)  
        res=self.cr.dictfetchall()
        return res
    ####################################count###############################

    def count_emps(self,child_ids,data):
       date1 = data['start_date']
       date2 = data['end_date']
       top_res=[]
       emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('start_date','>=',date1),('start_date','<=',date2),('department_id','in',child_ids)] )
       #print"**********emp**************",emp_ids ,len(emp_ids)  
       return len(emp_ids)


###############################all#function################################

    def _get_dept(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       if data['department_id']:
          for b in  data['department_id']:
 
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self.count_emps(child_ids ,data)
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}

            top_res.append(data_dec)
       return top_res
#####################################################plan_name#######################
    def count_emps_inside(self,child_ids,data):
		date1 = data['start_date']
		date2 = data['end_date']
		top_res=[]
		emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('start_date','>=',date1),('start_date','<=',date2),('department_id','in',child_ids) ,('training_place','=','inside')] )
		return len(emp_ids)
          
          
###############################all#function################################

    def get_dept_inside(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       #print"   --------------------------------------", data['department_id']
       if data['department_id']:
         for b in  data['department_id']:
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self.count_emps_inside(child_ids ,data)
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}
            top_res.append(data_dec)
       return top_res
###################################################################
    def count_emps_outside(self,child_ids,data):
		date1 = data['start_date']
		date2 = data['end_date']
		top_res=[]
		emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('start_date','>=',date1),('start_date','<=',date2),('department_id','in',child_ids) ,('training_place','=','outside')] )
		return len(emp_ids)
          
###############################all#function################################

    def get_dept_outside(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       #print"   --------------------------------------", data['department_id']
       if data['department_id']:
          for b in  data['department_id']:
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self.count_emps_outside(child_ids ,data)
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}
            top_res.append(data_dec)
       return top_res
#####################################################plan_name#######################
    def _count_trainee(self,child_ids,data):
       date1 = data['start_date']
       date2 = data['end_date']
       list_typ=[]
       self.cr.execute('''
        SELECT
	   		e.employee_type as e_type  ,b.name as n  ,count(e.employee_type ) ,e.bonus_id
		FROM 
			hr_employee e,hr_department  ,hr_salary_bonuses as b   
		WHERE
			e.state !='refuse' and
			e.bonus_id = b.id and
      		to_char(e.employment_date,'YYYY-mm-dd')>=%s and 
     		to_char(e.employment_date,'YYYY-mm-dd')<=%s and
	  		e.employee_type='trainee' and	
      		e.department_id = hr_department.id and
	  		hr_department.id in %s
		GROUP BY
      		e.bonus_id ,e.employee_type ,b.name
''',(date1,date2,tuple(child_ids) ))
       busy = self.cr.dictfetchall()
       #print"**********busy**************",busy
       if busy:
          for rec in busy:
				dic = {'trainee':rec['count'] ,'name':rec['n'],}
				list_typ.append(dic)
				#trainee=rec['count']
				#print"**********ist_typ**************",list_typ
                #print"**********trainee**************",trainee
				return list_typ[0]['trainee']
       else :
          return 0
#####################################################################
    def get_dept_tr(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       for b in  data['department_id']:
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self._count_trainee(child_ids ,data)
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}
            top_res.append(data_dec)
       return top_res
##################################################################
    def _count_student(self,child_ids ,data):
       date1 = data['start_date']
       date2 = data['end_date']
       self.cr.execute('''
            SELECT c_type.name as c_name ,count(c_type),c_type.id as c_id
FROM recruits_trainers s,hr_department,
     hr_contract_type as c_type
     
WHERE  
      s.type_id =c_type.id and
      to_char(s.nat_ser_date_end,'YYYY-mm-dd')>=%s and 
      to_char(s.nat_ser_date_end,'YYYY-mm-dd')<=%s and
      c_type.id =4 and
      s.department_id = hr_department.id and
      hr_department.id in %s
GROUP BY
      c_type.name ,c_id

''',(date1,date2,tuple(child_ids) ))
       busy = self.cr.dictfetchall()
       #print"**********busy**************",busy
       if busy:
          for rec in busy:
                student=rec['count']
                #print"**********student**************",student
                return student

       else :
          return 0
#####################################################################
    def get_dept_student(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       for b in  data['department_id']:
           
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self._count_student(child_ids ,data)
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}

            top_res.append(data_dec)
                        

       return top_res
############################################################
    def _count_graduate(self,child_ids ,data):
       date1 = data['start_date']
       date2 = data['end_date']
       self.cr.execute('''
            SELECT c_type.name as c_name ,count(c_type),c_type.id as c_id
FROM recruits_trainers s,hr_department,
     hr_contract_type as c_type
     
WHERE  
      s.type_id =c_type.id and
      to_char(s.nat_ser_date_end,'YYYY-mm-dd')>=%s and 
      to_char(s.nat_ser_date_end,'YYYY-mm-dd')<=%s and
      c_type.id = 6 and
      s.department_id = hr_department.id and
      hr_department.id in %s
GROUP BY
      c_type.name ,c_id

''',(date1,date2,tuple(child_ids) ))
       busy = self.cr.dictfetchall()
       #print"**********busy**************",busy
       if busy:
          for rec in busy:
                graduate=rec['count']
                #print"**********graduate**************",graduate
                return graduate

       else :
          return 0
#####################################################################
    def get_dept_graduate(self,data):
       top_res=[]
       ap_count=0
       cu_count=0
       sums=0
       sumss=0
       sumsss=0
       avg=0
       no=0
       for b in  data['department_id']:
           
            no+=1
            child_ids= []
            self.cr.execute(''' SELECT name as nn from hr_department where id=%s'''%b)
            do = self.cr.dictfetchall()
            cu_count=0
            child_ids=self.get_child_dept(self.cr,self.uid,b,{})
            child_ids+=[b]
            cu_count=self._count_graduate(child_ids ,data)
            #print"**********cu_count*************",cu_count
            sumss+=cu_count
            data_dec={'name': do[0]['nn'],'cu_count':cu_count,'no':no,'sumss':sumss,}

            top_res.append(data_dec)
                        

       return top_res

########################################################################
    def get_percentage(self,data,i):
        percentage = data['percentage']
        top_res=[]
        #print ">>>>>>>>>befor>>>" ,i
        self.cr.execute('''
SELECT distinct
count(hr.id) as hr_id
FROM 
hr_employee as hr
WHERE 
  hr.state!='refuse'
''')  
        res=self.cr.dictfetchall()
        #print ">>>>>>>>>>>>" ,res 
        all_emp=res[0]['hr_id']
        vir_num=(all_emp * percentage) /100
        #print ">>>>>>vir_num>>>>>>" ,vir_num
        per= i*100 /all_emp
        #print ">>>>>per>>>>>>>" ,per
        data_dec={'vir_num': vir_num ,'per':per}
        #print ">>>>>data_dec>>>>>>>" ,data_dec
        top_res.append(data_dec)
        return top_res
#######################################################
    def get_enrich(self,data):
        top_res=[]
        date1 = data['start_date']
        date2 = data['end_date']
        #print ">>>>>>>>>befor>>>" 
        self.cr.execute('''
SELECT distinct
  sum(tl.final_amount) as amount,en.currency as cur ,
  currency.symbol as cur_name
FROM 
  hr_employee_training_line as tl ,
  hr_employee_training as tr,
  hr_training_enrich en,
  res_currency as currency 
WHERE
  tr.type ='hr.approved.course' and
  tr.enrich_id=en.id and
  en.currency=currency.id and
  tl.training_employee_id=tr.id and
  to_char(tr.start_date,'YYYY-mm-dd')>=%s and 
  to_char(tr.end_date,'YYYY-mm-dd')<=%s
GROUP BY en.currency ,cur_name 
''',(date1,date2))  
        res=self.cr.dictfetchall()
        #print ">>>>res>>>>>" ,res 
 
        return res
#############################################
    def get_amount(self,data):
        top_res=[]
        date1 = data['start_date']
        date2 = data['end_date']
        #print ">>>>>>>>>befor>>>" 
        self.cr.execute('''
SELECT distinct
  sum(tr.trainer_cost) as amount,tr.currency_id as cur ,
  currency.symbol as cur_name
FROM 
  hr_employee_training as tr ,
  res_currency as currency
WHERE
  tr.type ='hr.approved.course' and
  tr.state='done' and
  tr.currency_id=currency.id and
  to_char(tr.start_date,'YYYY-mm-dd')>=%s and 
  to_char(tr.end_date,'YYYY-mm-dd')<=%s
GROUP BY tr.currency_id ,cur_name 

''',(date1,date2))  
        res=self.cr.dictfetchall()
        #print ">>>>res>>>>>" ,res 
 
        return res
report_sxw.report_sxw('report.shamil.training.report',
                       'hr.employee.training',
                       'addons/hr_training/report/shamil_training_report.rml',header="internal landscape",
                       parser=shamil_training_report)
