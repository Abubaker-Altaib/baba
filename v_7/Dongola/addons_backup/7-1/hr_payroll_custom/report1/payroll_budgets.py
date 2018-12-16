import time
import re
import pooler
from report import report_sxw
import calendar
import datetime

class payroll_budgets(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payroll_budgets, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'amount_s':self._amount,
            'stage_2':self._amount_satage2,
            'stage_3':self._amount_satage3,
            'stage_4':self._amount_satage4,
            'total':self._get_total,
            'totalz':self._get_totalz,
            'totale':self.totalz,
        })

    globals()['allowance']=[]
    globals()['no_exp_res']=[]
    globals()['sum_current']=0
    globals()['sum_predect']=0


#---------------------------   stage 1 (Salaries and Wages) ---------------------------
    def _amount(self,data,employee_type):
        top_res=[]
        try:
            """self.cr.execute('''SELECT sum(nex.no_exp) as no_exp,sum(nex.no_exp*hsb.basic_salary*12) as salary 
                               FROM expected_employees nex
                               LEFT JOIN hr_salary_bonuses hsb ON(hsb.id=nex.bonus_id)
                               WHERE year=%s '''%data['form']['year'])

            bonus= self.cr.dictfetchall()"""
            self.cr.execute('''SELECT COALESCE(sum(basic_salary),0) AS prev_basic_salary , count(employee_id) as cur_count
                             FROM hr_payroll_main_archive as m 
                             JOIN hr_employee e on (m.employee_id=e.id)
                             WHERE e.employee_type = %s and m.year=%s and m.in_salary_sheet= TRUE
                             and m.month=(select max(month) from hr_payroll_main_archive  where year=%s and in_salary_sheet= TRUE) ''',(employee_type,data['form']['year']-1,data['form']['year']-1))
            basic = self.cr.dictfetchall()
            x_add=0
            x_add_count=0
            bs=0
            if basic :
               bs=basic[0]['prev_basic_salary']*12
            self.cr.execute('''SELECT bonus_id as bon_id ,no_exp as no_exp,degree_id as degree_id FROM  expected_employees where employee_type=%s and year=%s ''',(employee_type,data['form']['year']))
            bonus= self.cr.dictfetchall()
            globals()['no_exp_res']=bonus
            if len(bonus)>0:
              for c in bonus :
                  local_sum=0
                  self.cr.execute('''
SELECT 
  hr_salary_bonuses.basic_salary
FROM 
  public.hr_salary_bonuses
WHERE 
   hr_salary_bonuses.id=%s'''%c['bon_id'])
                  x_basic= self.cr.dictfetchall()
                  local_sum=c['no_exp']*x_basic[0]['basic_salary']*12
                  x_add_count+=c['no_exp']
                  x_add+=local_sum
            dic={
                 'name':1,
                 'current':round(bs,2),
                 'cur_co': basic[0]['cur_count'],
                 'predict':round(x_add+bs,2),
                 'pre_co': x_add_count+basic[0]['cur_count'],
                 'differ':round(((x_add+bs)-bs),2),
                 'percent': (x_add and bs) and round((float((x_add+bs)-bs)/float(x_add+bs))*100,4) or 0
                }
            top_res.append(dic)
            '''for g in range(0,4):
                 x_add=0
                 x_add_count=0
                 bufer=globals()['allowance'][g]
                 cur_alw_mou=self.cur_allowance(bufer['alw_id'])
                 for r in globals()['no_exp_res']:
                      temp=0
                      b_mount=self.pre_allowance(bufer['alw_id'],bufer['type'],r['degree_id'],r['bon_id'],1,1)
                      if b_mount :
                            x_add_count+=r['no_exp']
                            temp=b_mount*r['no_exp']*12
                            x_add+=temp
                 di={
                      'name':bufer['name'],
                      'current':round((cur_alw_mou[0]['mount']*12),2),
                      'cur_co': cur_alw_mou[0]['count'],
                      'predict':round((x_add+(cur_alw_mou[0]['mount']*12)),2),
                      'pre_co': x_add_count+cur_alw_mou[0]['count'],
                      'differ':round(((x_add+(cur_alw_mou[0]['mount']*12))-(cur_alw_mou[0]['mount']*12)),2),
                      'percent':cur_alw_mou[0]['mount'] and round((float(x_add)/float(x_add+(cur_alw_mou[0]['mount']*12)))*100,4) or 0
                         }
                 top_res.append(di)'''
            if len(top_res)>0:
                for t in top_res:
                    globals()['sum_current']+=t['current']
                    globals()['sum_predect']+=t['predict']
        except: pass
        return top_res


#---------------------------   stage 2 ---------------------------
    def _amount_satage2(self,data,employee_type):
     top_res=[]
     try:    
      for g in range(1,11):
           nb=1
           x_add=0
           x_add_count=0
           alw_name=self.allowance_name('allow','first')
           if globals()['allowance'][g]:
              bufer=globals()['allowance'][g]
              cur_alw_mou=self.cur_allowance(bufer['alw_id'],employee_type)
              for r in globals()['no_exp_res']:
                   temp=0
                   if bufer['allowance_type']== 'family_relation':
                        nb=3
                   b_mount=self.pre_allowance(bufer['alw_id'],bufer['type'],r['degree_id'],r['bon_id'],nb,2)
                   if b_mount :
                      x_add_count+=r['no_exp']
                      temp=b_mount*r['no_exp']*12
                      x_add+=temp
              if (cur_alw_mou[0]['mount'])>0:
                    cur_alw_mou[0]['mount']=cur_alw_mou[0]['mount']
              else:
                  cur_alw_mou[0]['mount']=0

              di={
                      'name':bufer['name'],
                      'current':round((cur_alw_mou[0]['mount']*12),2),
                      'cur_co': cur_alw_mou[0]['count'],
                      'predict':round((x_add+(cur_alw_mou[0]['mount']*12)),2),
                      'pre_co': x_add_count+cur_alw_mou[0]['count'],
                      'differ':round(((x_add+(cur_alw_mou[0]['mount']*12))-(cur_alw_mou[0]['mount']*12)),2),
                      'percent':cur_alw_mou[0]['mount'] and round((float(x_add)/float(x_add+(cur_alw_mou[0]['mount']*12)))*100,4) or 0,
                         }
              top_res.append(di)
      if len(top_res)>0:
                for t in top_res:
                    globals()['sum_current']+=t['current']
                    globals()['sum_predect']+=t['predict']
     except: pass
     return top_res


#---------------------------   satage 3 ---------------------------
    def _amount_satage3(self,data,employee_type):
     top_res=[]
     alw_name=self.allowance_name('allow','second')
     try:
      for g in range(0,10):
           x_add=0
           x_add_count=0
           bufer=globals()['allowance'][g]
           friday=0
           cur_alw_mou=self.cur_allowance(bufer['alw_id'],employee_type)
           for r in globals()['no_exp_res']:
                temp=0
                b_mount=self.pre_allowance(bufer['alw_id'],bufer['type'],r['degree_id'],r['bon_id'],1,2)
                if b_mount :
                      x_add_count+=r['no_exp']
                      temp=b_mount*r['no_exp']*12
                      x_add+=temp
           if (cur_alw_mou[0]['mount'])>0:
                 cur_alw_mou[0]['mount']=cur_alw_mou[0]['mount']
                 friday=(float(x_add)/float(x_add+(cur_alw_mou[0]['mount']*12)))
           else:
               cur_alw_mou[0]['mount']=0
               if x_add < 1:
                   friday=0
               else:
                  friday=(float(x_add)/float(x_add+(cur_alw_mou[0]['mount']*12)))

           di={
                      'name':bufer['name'],
                      'current':round((cur_alw_mou[0]['mount']*12),2),
                      'cur_co': cur_alw_mou[0]['count'],
                      'predict':round((x_add+(cur_alw_mou[0]['mount']*12)),2),
                      'pre_co': x_add_count+cur_alw_mou[0]['count'],
                      'differ':round(((x_add+(cur_alw_mou[0]['mount']*12))-(cur_alw_mou[0]['mount']*12)),2),
                      'percent':round(friday*100,4)
                         }
           top_res.append(di)
      '''rt=self.consultant()
      top_res.append(rt)
      rr=self.retirement(data)
      top_res.append(self.trainee(data))
      top_res.append(self.requit(data))
      top_res.append(rr)'''
      if len(top_res)>0:
            for t in top_res:
                 globals()['sum_current']+=t['current']
                 globals()['sum_predect']+=t['predict']
     except: pass
     return top_res


#----------------------- stage 4 ------------------------
    def _amount_satage4(self,data):
     top_res=[]
     ded_name=self.allowance_name('deduct','first')
     try:
      for g in range(0,2):
           x_add=0
           x_add_count=0
           bufer=globals()['allowance'][g]
           cur_alw_mou=self.cur_allowance(bufer['alw_id'])
           for r in globals()['no_exp_res']:
                temp=0
                b_mount=self.pre_allowance(bufer['alw_id'],bufer['type'],r['degree_id'],r['bon_id'],1,2)
                if b_mount :
                      x_add_count+=r['no_exp']
                      if g==0:
                          temp=(b_mount*r['no_exp']*2)*12
                      else:
                          if g==1:
                                temp=((2*b_mount*r['no_exp'])+(float(b_mount*r['no_exp'])/8))*12
                      x_add+=temp
           if (cur_alw_mou[0]['mount'])>0:
                 cur_alw_mou[0]['mount']=cur_alw_mou[0]['mount']
           else:
               cur_alw_mou[0]['mount']=0

           di={
                      'name':bufer['name'],
                      'current':cur_alw_mou[0]['mount']*12,
                      'cur_co': cur_alw_mou[0]['count'],
                      'predict':x_add+(cur_alw_mou[0]['mount']*12),
                      'pre_co': x_add_count+cur_alw_mou[0]['count'],
                      'differ':round(((x_add+(cur_alw_mou[0]['mount']*12))-(cur_alw_mou[0]['mount']*12)),2),
                      'percent':round((float(x_add)/float(x_add+(cur_alw_mou[0]['mount']*12)))*100,4)
                         }
           top_res.append(di)
      if len(top_res)>0:
                for t in top_res:
                    globals()['sum_current']+=t['current']
                    globals()['sum_predect']+=t['predict']
     except: pass
     return top_res


#-------------------------------  components -----------------------------------

    def allowance_name(self,ad,sheet):

      self.cr.execute('''SELECT name, type,allowance_type,id AS alw_id
                           FROM hr_allowance_deduction
                           WHERE name_type = %s AND 
                           pay_sheet = %s AND 
                           active = True AND
                           sequence > 0
                           ORDER BY sequence ASC''',(ad,sheet))
      allownce= self.cr.dictfetchall()
      if len(allownce)>0:
         globals()['allowance']=allownce
         return 1
      else:
         return 3
        
    def cur_allowance(self,alw_id,employee_type):
        self.cr.execute('''SELECT COALESCE(sum(s.amount),0) as mount, 
                           count( s.employee_id) as count
                           FROM hr_employee_salary s
                           Join hr_employee e on (s.employee_id=e.id)
                           WHERE e.employee_type=%s and s.allow_deduct_id =%s''',(employee_type,alw_id))
        cur_allownace= self.cr.dictfetchall()
        return cur_allownace

    def pre_allowance(self,alw_id,typ,degree,bonus,wife,child):
        if (typ=='complex') and (wife==3):      
            irni=0
            family_relai=self.family_relai()
            if len(family_relai)>0:
                for j in family_relai:
                    if j['age']==0:
                        irni+=1*j['s_mount']
                    else:
                        if j['age']>0:
                            irni+=2*j['s_mount']

            return irni
        else:
          self.cr.execute('''SELECT 
      hr_employee_salary.amount as alw_mount
    FROM 
      public.hr_employee_salary, 
      public.hr_employee
    WHERE 
      hr_employee_salary.employee_id = hr_employee.id AND
      hr_employee.bonus_id =%s  AND 
      hr_employee.degree_id =%s AND 
      hr_employee_salary.allow_deduct_id=%s''',(bonus,degree,alw_id))
          pre_allownace= self.cr.dictfetchall()
          if len(pre_allownace)>0:
             return pre_allownace[0]['alw_mount']
          else:
              if (typ=='amount'):
                  pre_allownace= self.alw_4rm_scale(alw_id,degree)
                  if len(pre_allownace)>0 :
                        return pre_allownace[0]['alw_mount']
              else:
                  if (typ=='complex'): 
                        oho=0
                        hold=0
                        mount_1=0
                        pre_allownace= self.alw_4rm_scale(alw_id,degree)
                        if len(pre_allownace)>0 :
                              if (pre_allownace[0]['alw_mount']>0):
                                    ch=self.check(alw_id)
                                    if ((ch['fam']=='no' ) and (ch['allow_type']!='substitution')  and (ch['allow_type']!='qualification')):
                                        component_alw=self.component_alw(alw_id)

                                        if len(component_alw)>0:
                                             hope_mount=self.deffirnciate(component_alw,1)
                                             if len (hope_mount)>0:
                                                  mount_1=0
                                                  mount_1=self.cal_basic_mount(degree,hope_mount)
                                             ambcious_mix=self.deffirnciate(component_alw,2)
                                             if ambcious_mix:
                                              if len (ambcious_mix)>0:
                                                  hold_s=0
                                                  for s in ambcious_mix:
                                                    copo_alw=[]
                                                    mon=0
                                                    have=self.alw_4rm_scale(s,degree)
                                                    if have:
                                                     if have[0]['alw_mount']>0:
                                                        copo_alw=self.component_alw(s)
                                                        if copo_alw:
                                                            ho_mount=self.deffirnciate(copo_alw,1)
                                                            if ho_mount:
                                                              if len (ho_mount)>0:
                                                                  mon=self.cal_basic_mount(degree,ho_mount)
                                                                  hold_s+=mon*(float(have[0]['alw_mount'])/100)
                                                                  hold+=hold_s
                                        oho=(hold+mount_1)*(float(pre_allownace[0]['alw_mount'])/100)
                                        return  oho
                                    else:
                                         if ((ch['fam']=='yes' ) and (ch['allow_type']!='substitution')  and (ch['allow_type']!='qualification')):
                                              hold_s=0
                                              hold=0
                                              oho=0
                                              pre_alwnc= self.alw_4rm_scale(alw_id,degree)
                                              if pre_alwnc:
                                                   if (pre_alwnc[0]['alw_mount']>0):
                                                        co_alw=self.component_alw(alw_id)
                                                        if co_alw:
                                                            hope_mount=self.deffirnciate(co_alw,1)
                                                            if hope_mount:
                                                                 mount_1=0
                                                                 mount_1=self.cal_basic_mount(degree,hope_mount)

                                                            ambcious_mix=self.deffirnciate(co_alw,2)
                                                            if ambcious_mix:
                                                                 if len (ambcious_mix)>0:
                                                                      hold_s=0
                                                                      for s in ambcious_mix:
                                                                            copo_alw=[]
                                                                            mon=0
                                                                            have=self.alw_4rm_scale(s,degree)
                                                                            if have:
                                                                               if have[0]['alw_mount']>0:
                                                                                     
                                                                                      copo_alw=self.component_alw(s)
                                                                                      if copo_alw:

                                                                                           ho_mount=self.deffirnciate(copo_alw,1)
                                                                                           if ho_mount:
                                                                                                 if len (ho_mount)>0:
                                                                                                       mon=self.cal_basic_mount(degree,ho_mount)

                                                                                                       hold_s+=mon*(float(have[0]['alw_mount'])/100)
                                                                                                       hold+=hold_s

                                                            oho=(hold+mount_1)*(float(pre_alwnc[0]['alw_mount'])/100)

                                                            return  oho 
                                                   else:
                                                         return 0
                                              else :
                                                  return 0
                                         else :
                                             return 0
    #------------------------------------------------------------------------------
                              else :
                                  return 0 
                        else:            
                             return 0


    def alw_4rm_scale(self,alw_id,degree):

      self.cr.execute('''SELECT 
  hr_salary_allowance_deduction.amount as alw_mount
FROM 
  public.hr_salary_allowance_deduction
WHERE 
  hr_salary_allowance_deduction.degree_id =%s AND 
  hr_salary_allowance_deduction.allow_deduct_id =%s''',(degree,alw_id))
      pre_allownace= self.cr.dictfetchall()
      return pre_allownace


    def check(self,alw_id):
      self.cr.execute('''SELECT 
  hr_allowance_deduction.related_marital_status as fam, 
  hr_allowance_deduction.allowance_type as  allow_type, 
  hr_allowance_deduction.type  
FROM 
  public.hr_allowance_deduction
WHERE 
  hr_allowance_deduction.id =%s'''%alw_id)
      pre_allownace= self.cr.dictfetchall()
      return pre_allownace[0]



    def deffirnciate(self,alw_ids,typ):
      l_lis=[]
      self.cr.execute('''SELECT 
  hr_allowance_deduction.id
FROM 
  public.hr_allowance_deduction
WHERE 
  hr_allowance_deduction.type = '%s' and
  hr_allowance_deduction.id in %s''',(typ,tuple(alw_ids)))
      res= self.cr.dictfetchall()
      if res:
          for c in res:
               l_lis.append(c['id'])
      return l_lis


    def consultant(self):

     di = {}
     try:      
      x_add=0
      x_add_count=0
      c_add=0
      c_add_count=0
      e_list=[]
      self.cr.execute('''SELECT distinct
  hr_allowance_deduction.id AS alw_id, 
  hr_allowance_deduction.name, 
  hr_allowance_deduction.sequence,
  hr_allowance_deduction.type
FROM 
  public.hr_allowance_deduction, 
  public.hr_salary_allowance_deduction
WHERE 
  hr_salary_allowance_deduction.allow_deduct_id = hr_allowance_deduction.id AND
  hr_allowance_deduction.active = True AND
  hr_allowance_deduction.in_salary_sheet = True AND 
  hr_allowance_deduction.name_type = 'allow' AND 
  hr_salary_allowance_deduction.payroll_id = '3' 
ORDER BY
  hr_allowance_deduction.sequence ASC ''')
      consl= self.cr.dictfetchall()
      if len(consl)>0:
        self.cr.execute('''select id as e_id from hr_employee where payroll_id=3''')
        consl_ids= self.cr.dictfetchall()
        if (len(consl_ids)>0):
            for c in consl_ids:
              e_list.append(c['e_id'])
        for g in range(4, len(consl)):
           if (len(e_list)>0):
                self.cr.execute('''SELECT 
  sum( hr_employee_salary.amount) as mount, 
  count( hr_employee_salary.employee_id) as count
FROM 
  public.hr_employee_salary
WHERE 
  hr_employee_salary.allow_deduct_id =%s and
  hr_employee_salary.employee_id in %s''',(consl[g]['alw_id'],tuple(e_list)))
                cur_allownace= self.cr.dictfetchall()
                if len(cur_allownace)>0:
                      cur_alw_mou= cur_allownace
                else:
                      cur_alw_mou= [{'mount':0,'count':0,}]
                bufer=consl[g]
                if not (cur_allownace[0]['count'])>0:
                         cur_alw_mou[0]['mount']=0
                c_add+=cur_alw_mou[0]['mount']*12
                if(c_add_count < cur_alw_mou[0]['count']):
                     c_add_count=cur_alw_mou[0]['count']
                for r in globals()['no_exp_res']:
                      temp=0
                      b_mount=self.pre_allowance(bufer['alw_id'],bufer['type'],r['degree_id'],r['bon_id'],1,2)
                      if b_mount :
                          if(x_add_count<r['no_exp']):
                              x_add_count=r['no_exp']
                          temp=(b_mount*r['no_exp'])*12
                          x_add+=temp
        di={
                      'name':3,
                      'current':c_add,
                      'cur_co': c_add_count,
                      'predict':x_add+c_add,
                      'pre_co': x_add_count+c_add_count,
                      'differ':round(x_add,2),
                      'percent':round((float(x_add)/float(x_add+c_add))*100,4)
                         }
     except: pass
     return di


    def trainee(self,data):
     di ={}
     try:
      x_add=0
      x_add_count=0
      c_add=0
      c_add_count=0
      ppp=int(data['form']['year'])-1
      self.cr.execute('''SELECT 
 count( recruits_trainers.id) as count
FROM 
  recruits_trainers
WHERE 
  to_char(recruits_trainers.nat_ser_date,'YYYY') = '%s' or
  to_char(recruits_trainers.nat_ser_date_end,'YYYY') ='%s' and
  recruits_trainers.states='inside' 
 ''',(ppp,ppp))
      cur_count= self.cr.dictfetchall()
      self.cr.execute('''SELECT 
  sum(training_trainee_payrol.payrol) as mount
FROM 
  public.training_trainee_payrol
WHERE 
  training_trainee_payrol.year = %s 
 '''%ppp)
      cur_mount= self.cr.dictfetchall()
      if len(cur_mount)>0:
         if(cur_mount[0]['mount']>0):
               c_add=cur_mount[0]['mount']
         else :
           c_add=0
         c_add_count=cur_count[0]['count']


      self.cr.execute('''SELECT 
  no_training_exp.payroll, 
  no_training_exp.no_exp
FROM 
  public.no_training_exp
WHERE 
  no_training_exp.year  = %s AND 
  no_training_exp.type  ='2' '''%data['form']['year'])
      pre_mount= self.cr.dictfetchall()
      if len(pre_mount)>0:
         x_add_count= pre_mount[0]['no_exp'] 
         x_add=pre_mount[0]['no_exp']*pre_mount[0]['payroll']*12
         
      di={
                      'name':2,
                      'current':round(c_add,2),
                      'cur_co': c_add_count,
                      'predict':round(x_add,2),
                      'pre_co': x_add_count,
                      'differ':round((x_add-c_add),2),
                      'percent':round((float(x_add-c_add)/float(x_add+c_add))*100,4)
                         }
     except: pass
     return di


    def requit(self,data):
     di = {}
     try:
      x_add=0
      x_add_count=0
      c_add=0
      c_add_count=0
      ppp=int(data['form']['year'])-1
      self.cr.execute('''SELECT 
 count( recruits.id) as count
FROM 
  public.recruits
WHERE 
  to_char(recruits.nat_ser_date,'YYYY') = '%s' or
  to_char(recruits.nat_ser_date_end,'YYYY') ='%s' and
  recruits.states='inside' 
 ''',(ppp,ppp))
      cur_count= self.cr.dictfetchall()
      self.cr.execute('''SELECT 
  sum(training_trainee_payrol.payrol) as mount
FROM 
  public.training_trainee_payrol, 
  public.recruits_trainers
WHERE 
  recruits_trainers.id = training_trainee_payrol.trainee_id AND
  training_trainee_payrol."year" = %s '''%ppp)
      cur_mount= self.cr.dictfetchall()
      if len(cur_mount)>0:
         if(cur_mount[0]['mount']>0):
               c_add=cur_mount[0]['mount']
         else :
           c_add=0
         c_add_count=cur_count[0]['count']
      self.cr.execute('''SELECT 
  no_training_exp.payroll, 
  no_training_exp.no_exp
FROM 
  public.no_training_exp
WHERE 
  no_training_exp.year  = %s AND 
  no_training_exp.type  ='1' '''%data['form']['year'])
      pre_mount= self.cr.dictfetchall()
      if len(pre_mount)>0:
         x_add_count= pre_mount[0]['no_exp'] 
         x_add=pre_mount[0]['no_exp']*pre_mount[0]['payroll']*12
         
      di={
                      'name':4,
                      'current':round(c_add,2),
                      'cur_co': c_add_count,
                      'predict':round(x_add,2),
                      'pre_co': x_add_count,
                      'differ':round((x_add-c_add),2),
                      'percent':round((float(x_add-c_add)/float(x_add+c_add))*100,4)
                         }
     except: pass
     return di

#--------------------------   retirement  retirement----------------------------

    def retirement(self,data):
     di = {}
     try:
      x_add=0
      x_add_count=0
      c_add=0
      c_add_count=0
      emps=self.salary_scale(data)
      termin_alw=self.termination_alw(1)
      compo_alw=self.component_alw(termin_alw[0]['alw_id'])  
      cur_count=self.cur_allowance(termin_alw[0]['alw_id'])
      milx_0=self.multiplix(termin_alw[0]['alw_id'],'f',0)
      milx_1=self.multiplix(termin_alw[0]['alw_id'],'t',0)
      milx_2=self.multiplix(termin_alw[0]['alw_id'],'t',1)
      milx_3=self.multiplix(termin_alw[0]['alw_id'],'t',2)
      if (c_add_count< cur_count[0]['count']):
        c_add_count=cur_count[0]['count']
      if cur_count[0]['mount']>0:
         c_add+=cur_count[0]['mount']       
#-------------------- furnatur movement----------
      termination_alw=self.termination_alw(2)
      cur_count=self.cur_allowance(termination_alw[0]['alw_id'])
      if (c_add_count< cur_count[0]['count']):
            c_add_count=cur_count[0]['count']
      if cur_count[0]['mount']>0:
         c_add+=cur_count[0]['mount']        
      component_alw=self.component_alw(termination_alw[0]['alw_id'])
      multip_mount =(self.cal_alow_mount(termination_alw[0]['alw_id']))/100
      if len(globals()['emp'])> 0:
       if len(component_alw)>0:
        for b in globals()['emp']:
          self.cr.execute('''select max (year) as year from hr_allowance_deduction_archive where employee_id=%s and type='allow' '''%b['e_id'])
          res= self.cr.dictfetchall()
          year=res[0]['year']
          self.cr.execute('''select max (month) as month from hr_allowance_deduction_archive where employee_id=%s and year=%s and type='allow' ''',(b['e_id'],year))
          re= self.cr.dictfetchall()
          month=re[0]['month']
          mou=self.cal_emp_alow_mount(b['e_id'],month,year,component_alw)
          x_add+=mou*multip_mount
#--------------------  movement ve family----------
          fami=self.family_count(b['e_id'])
          if fami==0:
              mo=self.cal_emp_alow_mount(b['e_id'],month,year,compo_alw)
              x_add+=mo*milx_0
          else:
              if fami==1:
                 mo=self.cal_emp_alow_mount(b['e_id'],month,year,compo_alw)
                 x_add+=mo*milx_1
              else:
                  if fami==2:
                    mo=self.cal_emp_alow_mount(b['e_id'],month,year,compo_alw)
                    x_add+=mo*milx_2
                  else:
                      if fami>2:
                         mo=self.cal_emp_alow_mount(b['e_id'],month,year,compo_alw)
                         x_add+=mo*milx_3
#---------------------------------------------------------------------       
      di={
                      'name':7,
                      'current':round(c_add),
                      'cur_co': c_add_count,
                      'predict':round(x_add),
                      'pre_co': len(globals()['emp']),
                      'differ':round((x_add-c_add),2),
                      'percent':round((float(x_add-c_add)/float(x_add+c_add))*100,4)
                         }
     except: pass
     return di


    def salary_scale(self,data):
      globals()['emp']=[]
      self.cr.execute('''SELECT age_pension
                         FROM hr_config_settings''' )
      scale= self.cr.dictfetchall()
      if len (scale)>0:
          for c in scale:
              awesome=int(int(data['form']['year'])-c['p_age'])
              self.cr.execute('''SELECT id as e_id, marital,degree_id
                                 FROM hr_employee
                                 where service_terminated=False 
                                 and birthday <= '%s-12-31' ''',(c['s_id'],awesome))
              res= self.cr.dictfetchall()
              if len(res)>0:
                  for n in res:
                       globals()['emp'].append(n)  



    def termination_alw(self,alw_id):
        self.cr.execute('''SELECT name,type,id AS alw_id
                           FROM hr_allowance_deduction
                           WHERE name_type = 'allow' AND
                           pay_sheet ='second' AND 
                           allowance_typ ='general' AND  
                           related_marital_status ='%s' AND  
                           active = True 
                           ORDER BY sequence ASC'''%alw_id )
        alw= self.cr.dictfetchall()
        return alw

    def component_alw(self,alw_id):
      
        self.cr.execute('''SELECT allowance_id
                           FROM  com_allow_deduct_rel
                           WHERE com_allow_deduct_id = %s'''%alw_id )
        res= self.cr.dictfetchall()
        return [r['allowance_id'] for r in res]


    def cal_alow_mount(self,alw_id):
        self.cr.execute('''SELECT distinct amount as mount
                           FROM hr_salary_allowance_deduction
                           WHERE allow_deduct_id  = %s'''%alw_id )
        res= self.cr.dictfetchall()[0]['alw_mount']
        return res



    def cal_emp_alow_mount(self,e_id,month,year,alw_id):

      self.cr.execute('''SELECT 
   sum(hr_allowance_deduction_archive.amount)
FROM 
  public.hr_allowance_deduction_archive
where
  month=%s and
  year='%s' and
  and type='allow' and 
  allowance_id in %s and
  employee_id= %s ''',(month,year,tuple(alw_id),e_id))
      res= self.cr.fetchall()
      if res :
         return res[0][0]
      else:
         return 0


    def family_count(self,e_id):
      self.cr.execute('''SELECT 
  count(hr_employee_family.id) as co
FROM 
  public.hr_employee_family
where
  hr_employee_family.employee_id= %s'''%e_id )
      res= self.cr.dictfetchall()
      if res :
         return res[0]['co']
      else:
         return 0


    def multiplix(self,alw_id ,waif,child):
      self.cr.execute('''SELECT 
  (hr_allow_marital_status.percentage)/100 as multiplix, 
  hr_allow_marital_status.married, 
  hr_allow_marital_status.children_no
FROM 
  public.hr_allow_marital_status
WHERE 
  hr_allow_marital_status.alternative_cash = %s  and
  hr_allow_marital_status.married=%s and 
  hr_allow_marital_status.children_no=%s
''',(alw_id,waif,child) )
      res= self.cr.dictfetchall()[0]['multiplix']
      return res
   

    def family_relai(self):
      self.cr.execute('''SELECT 
  hr_family_relation.max_age as age, 
  hr_family_relation.social_benefit_amount as s_mount
FROM 
  public.hr_family_relation
WHERE 
  hr_family_relation.active = 'True'
''')
      res= self.cr.dictfetchall()
      return res

#----------------------------------------------  additional wage   --------------------------------------

    """def additional_wage(self,data):
       di = {}
       try:
        x_add=0
        x_add_count=0
        c_add=0
        c_add_count=0
        addi_alw=self.additional_work_alw()
        if len (addi_alw)>0:
              c_add,c_add_count=self.cur_addi_wage(data)
              component_alw=self.component_alw(addi_alw[0]['alw_id'])
              if len(component_alw)>0:
                    degrees=self.addi_work_degrees(addi_alw[0]['alw_id'])
                    if len(degrees)>0:
                          for c in degrees:
                                no_emps=0
                                no_emps=self.count_emps_no(c['degree_id'])
                                if no_emps > 0:
                                      basic=self.cal_basic_mount(c['degree_id'],component_alw)
                                      if basic >0:
                                              x_add+=12*((basic*no_emps*addi_alw[0]['max_hours'])/addi_alw[0]['distributed'])
                                              x_add_count+=no_emps
        di={
                          'name':addi_alw and addi_alw[0]['name'] or '/',
                          'current':c_add,
                          'cur_co': c_add_count,
                          'predict':x_add,
                          'pre_co': x_add_count,
                          'differ':x_add-c_add,
                          'percent':(x_add+c_add) != 0 and (x_add-c_add)/(x_add+c_add)*100 or 0
                             }

       except: pass
       return di


    def additional_work_alw(self):
        self.cr.execute('''SELECT name,max_hours,distributed,type,id AS alw_id
                         FROM hr_allowance_deduction
                         WHERE name_type = 'allow'
                         AND pay_sheet ='second' 
                         AND active = True 
                         AND in_cycle = True 
                         AND taxable = True 
                         AND max_hours > 0 
                         AND sequence > 0
                         ORDER BY sequence ASC''')
        res= self.cr.dictfetchall()   
        return res

    def addi_work_degrees(self,alw_id):
        self.cr.execute('''SELECT amount as alw_mount,degree_id 
                           FROM hr_salary_allowance_deduction
                           WHERE allow_deduct_id=%s'''%alw_id)
        res= self.cr.dictfetchall()   
        return res"""

    def cal_basic_mount(self,alws):
        self.cr.execute('''SELECT sum(amount) as amount degree_id
                           FROM  hr_salary_allowance_deduction
                           WHERE allow_deduct_id  in %s
                           GROUP BY degree_id''',(tuple(alws),) )
        res= self.cr.dictfetchall()
        return res['amount']

    def count_emps_no(self,degree):
        counter=0
        self.cr.execute('''SELECT sum(no_exp) AS no_exp
                           FROM  no_expextation
                           where degree_id =%s''' %degree)
        res1= self.cr.dictfetchall()
        counter+=res1['no_exp']
        self.cr.execute('''SELECT count(id) as count 
                       FROM  hr_employee
                       where degree_id=%s and
                       service_terminated=False'''%degree)
        res2= self.cr.dictfetchall()
        counter+=res2['count']
        return counter
 
    def cur_addi_wage(self,data):
      self.cr.execute('''SELECT sum(line.amounts_value+line.imprint+line.taxs) as sm ,count( distinct line.employee_id) as count
                           FROM  hr_additinal_allowance_line line
                           LEFT JOIN hr_additinal_allowance hra ON (hra.id=line.additinal_allowance_id)
                           WHERE hra.year = %s '''%int(data['form']['year'])-1)
      res= self.cr.dictfetchall()
      amount=res[0]['sm']
      count=res[0]['count']
      return count,amount
#---------------------------------------------- total--------------------------------------

    def _get_total(self,data):
        top_res=[]
        res=[]
        try:
         margin=data['margin']
         difr=round((globals()['sum_predect']-globals()['sum_current']),2)
         per=round(((float(difr)/float(globals()['sum_predect']+globals()['sum_current']))*100),2)
         res.append(round(globals()['sum_predect'],2))
         res.append(round(globals()['sum_current'],2))
         res.append(difr)
         res.append(per)
         top_res.append(res)
        except: pass
        return top_res

    def totalz(self,data):
        top_res=[]
        res=[]
        try:
         margin=data['margin']
         gross=round(((margin*globals()['sum_predect'])/100),2)
         res.append(gross)
         top_res.append(res)
        except: pass
        return top_res

    def _get_totalz(self,data):
        res=[]
        top_res=[]
        margin=data['margin']
        try:
         gross=round(((margin*globals()['sum_predect'])/100),2)
         res.append(round((gross+globals()['sum_predect']),2))
         difr=round(((gross+globals()['sum_predect'])-globals()['sum_current']),2)
         per=round(((float(difr)/float((gross+globals()['sum_predect'])+globals()['sum_current']))*100),2)
         res.append(difr)
         res.append(globals()['sum_current'])
         res.append(per)
         top_res.append(res)
         globals()['sum_predect']=0
         globals()['sum_current']=0
        except: pass
        return top_res


report_sxw.report_sxw('report.payroll.budgets', 'hr.payroll.main.archive', 'addons/hr_payroll_custom/report/payroll_budgets.rml' ,parser=payroll_budgets ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

 
