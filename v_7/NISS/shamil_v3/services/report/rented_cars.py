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

class rented_cars(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rented_cars, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
	    'total':self._gettotal,
#            'line3':self.get_department,
#            'genral':self._genral,
#           'final':self._final,
#            'choose':self._get_choose
        })
    def _getdata(self,data):
           month= data['form']['month']
           year= data['form']['year']
	   department = data['form']['department_id']
	   partner = data['form']['partner_id']
	   company = data['form']['company_id']
           """chose=data['form']['choose_type']
           depat_type=""
           if num==3 :
             different_list=tuple(list(set(self.get_department(3)) - set(self.get_department(10))) )
           else :
             different_list=tuple(self.get_department(num))
           no=0          
           if chose=='project':
               depat_type=" and a.project=true " 
               different_list=tuple(self.get_department(num))
               
           else:
               depat_type=" and a.main_dept=true "
           """
           mang_total=0.00
           all_dep=[]
           where_condition = "" 
           where_condition += department and " and all_line.department_id=%s"%department[0] or ""
           where_condition += partner and " and all_ar.partner_id=%s"%partner[0] or ""
           where_condition += company and " and all_ar.company_id=%s"%company[0] or ""
           self.cr.execute("""
                   SELECT distinct
                                  r.name as detail_name ,
				  p.name as partner ,
				  all_line.amount_total as total ,
				  f.name as car_name ,
				  f.license_plate as car_num ,
				  res.name as emp_name ,
				  h.name as dept ,  
				  r.date_of_rent as start_rent ,
				  r.date_of_return as end_rent


                FROM rented_cars r
                left join rented_cars_allowances_lines as all_line on (r.id=all_line.rent_id)
                left join rented_cars_allowances_archive as all_ar on (all_ar.id=all_line.rented_cars_allow_id)
		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.employee_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)
                left join account_analytic_account as a on (h.analytic_account_id = a.id)
		where r.state = 'confirmed' 
 and all_ar.month=%s and all_ar.year='%s'
 """ +where_condition+ " order by partner ",(month,year)) 
           res = self.cr.dictfetchall()
           return res



    def _gettotal(self,data):
           month= data['form']['month']
           year= data['form']['year']
	   department = data['form']['department_id']
	   partner = data['form']['partner_id']
	   company = data['form']['company_id']
           """chose=data['form']['choose_type']
           depat_type=""
           if num==3 :
             different_list=tuple(list(set(self.get_department(3)) - set(self.get_department(10))) )
           else :
             different_list=tuple(self.get_department(num))
           no=0          
           if chose=='project':
               depat_type=" and a.project=true " 
               different_list=tuple(self.get_department(num))
               
           else:
               depat_type=" and a.main_dept=true "
           """
           mang_total=0.00
           all_dep=[]
           where_condition = "" 
           where_condition += department and " and all_line.department_id=%s"%department[0] or ""
           where_condition += partner and " and all_ar.partner_id=%s"%partner[0] or ""
           where_condition += company and " and all_ar.company_id=%s"%company[0] or ""
           self.cr.execute("""
                   SELECT distinct
				  sum (all_line.amount_total) as final_total 


                FROM rented_cars r
                left join rented_cars_allowances_lines as all_line on (r.id=all_line.rent_id)
                left join rented_cars_allowances_archive as all_ar on (all_ar.id=all_line.rented_cars_allow_id)
		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_department h on (f.department_id = h.id)
                left join account_analytic_account as a on (h.analytic_account_id = a.id)
		where r.state = 'confirmed' 
 and all_ar.month=%s and all_ar.year='%s'
 """ +where_condition+ " order by final_total ",(month,year)) 
           res = self.cr.dictfetchall()
           return res


################################# old code for SECTO Project  ##############################


    """def _get_choose(self,data):
       chose=data['form']['choose_type']
       return chose

    def get_department(self,dept):
        top=[int(dept)]
        def inner(dept):
            res=[]
            self.cr.execute(
SELECT 
  hr_department.id AS dep_id
FROM 
  public.hr_department,
  res_company 
WHERE
   hr_department.company_id=res_company.id and 
hr_department.parent_id=%s%dept)
            result=self.cr.dictfetchall()
            if result:
                 res=[ele['dep_id'] for ele in result]
            return res
        if inner(dept):
                top+=inner(dept)
                for h in inner(dept):
                    if inner(h):
                        top+=inner(h)
                        for j in inner(h):
                             top+=inner(j)

        return top
    def _genral(self,data):
        gen_list=[]
        chose=data['form']['choose_type']
        data_dept = data['form']['department_id']
        if data_dept !=0  :
           self.cr.execute('''SELECT distinct id as depid ,name as dept FROM hr_department as hr where id=%s '''%data['form']['department_id'][0])
           gen_dep = self.cr.dictfetchall()
        else:
           self.cr.execute('''SELECT distinct hr.id as depid ,hr.name as dept FROM hr_department as hr where hr.id!=41 and gen_dep=True ''')
           gen_dep = self.cr.dictfetchall()
        if chose=='project':
           self.cr.execute('''SELECT distinct hr.id as depid ,hr.name as dept FROM hr_department as
 hr,account_analytic_account as a ,fleet_vehicle as f,rented_cars as r where hr.id!=41 and hr.analytic_account_id = a.id and
 a.project=true and f.department_id=hr.id and r.car_id=f.id''')
           gen_dep = self.cr.dictfetchall()
        for dep in gen_dep:
            dic={'depid':dep['depid'],
           'dept':dep['dept'] 
                  }
            gen_list.append(dic)
        return gen_list"""
    """def _final(self,data):
            chose=data['form']['choose_type']
            if chose=='project':
               depat_type=" and a.project=true "
            else:
               depat_type=" and a.main_dept=true "
            department = data['form']['department_id']
            final_mang_total=0.00
            final_total=[]
            month= data['form']['month']
            year= data['form']['year']
            self.cr.execute(
                  SELECT distinct
                 sum(all_line.amount_total) as total 
                FROM rented_cars r
                left join rented_cars_allowances_lines as all_line on (r.id=all_line.rent_id)
                left join rented_cars_allowances_archive as all_ar on (all_ar.id=all_line.rented_cars_allow_id)
		left join fleet_vehicle f on (r.car_id = f.id)
		left join res_partner p on (r.partner_id = p.id)
		left join hr_employee emp on (f.employee_id = emp.id)
		left join resource_resource res on (emp.resource_id = res.id)
		left join hr_department h on (f.department_id = h.id)  
                left join account_analytic_account as a on (h.analytic_account_id = a.id)
		where r.state = 'confirmed' and  all_ar.month=%s and all_ar.year='%s' ,(month,year)) 
            final = self.cr.dictfetchall()
            return final[0]['total']"""

report_sxw.report_sxw('report.rented_cars.report', 'rented.cars', 'addons/services/report/rented_cars.rml' ,parser=rented_cars , header=False)
