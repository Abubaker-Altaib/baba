#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv ,fields
import time
from report import report_sxw
import pooler
from base_custom import amount_to_text_ar 
from openerp.tools.translate import _

class ousite_contract_atten_over(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ousite_contract_atten_over, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'attent_count':self.attent_count,
            'total_mount':self.total_mount,
            'over_time':self.over_time,
            'company_depart':self.company_depart,
            'all_company':self.all_company,
            'multi_company_sum':self.multi_company_sum,
           'text':self._pars,

        })
    def _pars(self,d): 
       
       res1 = amount_to_text_ar.amount_to_text(d,'ar')
       return res1
   
    def company_depart(self,data):
        comp=data['form']['ref'].split(',')[1]
        if data['form']['ref'][0]=='r':
           self.cr.execute("select name from res_company as comp where  comp.id=%s" %comp)
           depcom = self.cr.dictfetchall()
        else:
            self.cr.execute("select name from hr_department as hr where hr.id=%s" %comp)
            depcom = self.cr.dictfetchall()
        return depcom[0]['name']

    def attent_count(self,data):
        comp=data['form']['ref'].split(',')[1]
        month=data['form']['month']
        year=data['form']['year']
        if data['form']['ref'][0]=='r':
           depcom =" and comp.id=%s" %comp +"and part.id=%s" %data['form']['partner_id'][0]
        else:
            depcom =" and hr.id=%s" %comp
        data_list=[]
        attent_day=30
        apsent_day=0
        month_mount=0.0
        last_total=0.0
        tax=0.0
        no=0
        self.cr.execute('''SELECT emp_name.name as name ,job.name as job, hr.name as depname,comp.name as company_name,
        emp_name.id as empid
FROM 
  public.outsite_contract as emp_name, 
  public.res_company as comp, 
  public.hr_department as hr, 
  public.outsite_job_config as job,
  res_partner as part
WHERE 
  emp_name.company_id = comp.id AND hr.id = emp_name.department_id AND job.id = emp_name.job_id and emp_name.partner_id=part.id 
    '''+depcom)
        emp_ids_list = self.cr.dictfetchall()
        if emp_ids_list==[]:
           raise osv.except_osv(_('Warning'), _("No Employee in This Department "))
        else :
           for l in emp_ids_list:
            self.cr.execute('''SELECT mount.no_day as no_day
FROM 
  public.outsite_contract as out,
  public.contract_payroll_amount as mount
WHERE  
  out.id = mount.employee AND out.id=%s and mount.month=%s and mount.year='%s' ''',(l['empid'],month,year))
            emp_attent = self.cr.dictfetchall()
            if len(emp_attent)>0:
               apsent_day=int(0 if emp_attent[0]['no_day'] is None else emp_attent[0]['no_day'])
               attent_day=int(30 if emp_attent[0]['no_day'] is None else 30-apsent_day)
            no+=1
            self.cr.execute('''SELECT 
  outt.appsent_amount as apsent_mount, 
  outsite_job.total_amount as month_mount
FROM 
  public.outsite_contract as cont, 
  public.outsite_contract_main_archive as outt, 
  public.outsite_job_config as outsite_job 
WHERE 
  cont.job_id = outsite_job.id AND  
  outt.employee_id = cont.id and outt.month=%s and outt.year='%s' and outt.employee_id=%s''',(month,year,l['empid']))
            emp_mount = self.cr.dictfetchall()
            apsent=(0.0 if emp_mount[0]['apsent_mount'] is None else emp_mount[0]['apsent_mount'])
            month_mount=float(emp_mount[0]['month_mount'])-float(apsent)
            last_total+=month_mount
            dic={'name':l['name'],'job':l['job'],'attent':attent_day ,'apsent':apsent_day,'no':no,'total':month_mount,'all_total':last_total,
                 'depname':l['depname'] }
            data_list.append(dic)
        tax=(last_total*17)/100
        globals()['tax']=tax
        globals()['final_total']=last_total+tax
        globals()['company_name']=emp_ids_list[0]['company_name']
        return data_list
    
    def over_time(self,data,type):  
        listt=[]   
        comp=data['form']['ref'].split(',')[1]
        month=data['form']['month']
        year=data['form']['year']
        part=data['form']['partner_id'][0]
        if data['form']['ref'][0]=='r':
           depcom =" and comp.id=%s" %comp
        else:
            depcom =" and hr.id=%s" %comp
        globals()['dep@comp']=depcom
        self.cr.execute('''SELECT distinct
  emp.name as name, 
  jobb.name as job, 
  mount.no_hours_holi/8 as holi, 
  mount.no_hours/8 as hours,
  comp.name as company_name,
  hr.name as depname,
mount.gross_amount as sum
FROM 
  public.outsite_contract as emp, 
  public.outsite_allow_detuct as allow, 
  public.outsite_job_config as jobb, 
  public.contract_payroll_amount as mount,
  res_company as comp,
  hr_department as hr,
   res_partner as part
WHERE 
  emp.company_id=comp.id and emp.department_id=hr.id and
  emp.job_id = jobb.id AND emp.id = mount.employee AND emp.partner_id=part.id and
  mount.overtime_name = allow.id and allow.id = %s and 
  mount.month=%s and mount.year='%s' and part.id=%s
'''+ depcom + "order by emp.name",(type,month,year,part))
        over_miss = self.cr.dictfetchall()
        if not over_miss :
            raise osv.except_osv(_('Warning'), _("Sorry No Data To Print"))
        return over_miss
    
    def all_company(self,data):
        com_list=[]
        pay_total=0.0
        mount_overtime=0.0
        all_total=0.0
        month=data['form']['month']
        year=data['form']['year']
        part=data['form']['partner_id'][0]
        company_select=data['form']['all_company']
        for c in company_select:
            self.cr.execute('''SELECT  
  comp.name as com_name, 
  sum(main.net) as mount_pay, 
  sum(main.total_allowance)+sum(main.total_mission) as mount_overtime,
  sum(main.gross) as all_total
FROM 
  public.res_company as comp, 
  public.outsite_contract_main_archive as main,
  res_partner as part
WHERE 
  comp.id = main.company_id AND 
  part.id=main.partner_id and
  main.month=%s  and main.year='%s' and main.company_id=%s and part.id=%s
GROUP BY com_name order by com_name ''',(month,year,c,part))
            total_company= self.cr.dictfetchall()
            if not total_company :
                  return com_list
            dic={'com_name':total_company[0]['com_name'],'mount_pay':total_company[0]['mount_pay'],
            'mount_overtime':total_company[0]['mount_overtime'],'all_total':total_company[0]['all_total'] }
            com_list.append(dic)
            pay_total+=total_company[0]['mount_pay']
            mount_overtime+=total_company[0]['mount_overtime']
            all_total+=total_company[0]['all_total']
        globals()['pay_total']= pay_total
        globals()['mount_overtime']= mount_overtime
        globals()['all_total']= all_total
        if not com_list :
            raise osv.except_osv(_('Warning'), _("Sorry No Data To Print"))
        return com_list
    
    def total_mount(self,data):
        type=(1,2)
        part=data['form']['partner_id'][0]
        month=data['form']['month']
        year=data['form']['year']
        select=data['form']['select_type']
        self.cr.execute('''SELECT 
sum(mount.gross_amount) as summ
FROM 
  public.outsite_contract as emp, 
  public.outsite_allow_detuct as allow, 
  public.outsite_job_config as jobb, 
  public.contract_payroll_amount as mount,
  res_company as comp,
  hr_department as hr,
 res_partner as part
WHERE 
  emp.company_id=comp.id and emp.department_id=hr.id and
  emp.job_id = jobb.id AND emp.id = mount.employee AND emp.partner_id=part.id and
  mount.overtime_name = allow.id and allow.id in %s and 
  mount.month=%s and mount.year='%s' and part.id=%s'''+ globals()['dep@comp'] + " order by summ",(type,month,year,part))
        sumion = self.cr.dictfetchall()
        tax_over=sumion[0]['summ']*17/100
        mount_over_final=sumion[0]['summ']+tax_over
        dic={'tax':globals()['tax'],'final_total':globals()['final_total'],'over_miss_total':sumion[0]['summ'],
             'tax_over':tax_over,'mount_over_final':mount_over_final}
        return dic
    
    def multi_company_sum(self):
        dic={'pay_total':globals()['pay_total'],'mount_overtime':globals()['mount_overtime'],'all_total':globals()['all_total']}
        return dic

report_sxw.report_sxw('report.print.emps.names.attent', 'outsite.contract', 'addons/services/report/outsite_contract_attent.rml' ,parser=ousite_contract_atten_over , header=False)
report_sxw.report_sxw('report.print.emps.names.overtime', 'outsite.contract', 'addons/services/report/overtime_misson.rml' ,parser=ousite_contract_atten_over , header=False)
report_sxw.report_sxw('report.print.out.multi.company', 'outsite.contract', 'addons/services/report/out.multi_company.rml' ,parser=ousite_contract_atten_over , header=False)
