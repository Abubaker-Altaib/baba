#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import timedelta,date

# Fuel plan report  
# Report to print Fuel plan in a specific month and year.

class fuel_plan_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fuel_plan_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self._getdata1,
            'line2':self._getdata2,
            'line3':self._getdata3,
        })

    def _getdata(self,data):
        month= data['form']['month']
        year= data['form']['year']
        department = data['form']['department_id']
        department_obj = self.pool.get('hr.department')
        department_condition = ""
        if department:
            department_id = department[0]
            department_ids = department_obj.search(self.cr,self.uid,[('id','child_of',department_id)])
            if len(department_ids) == 1:
                department_condition = " and d.id in (%s)"%department_ids[0]
            else:
                department_ids = tuple(department_ids)
                department_condition = " and d.id in %s"%str(department_ids)
        self.cr.execute('''
                select
                v.name as vehicles_name , 
                t.name as product_name, 
                l.product_qty as product_qty, 
                l.price_unit * l.product_qty as product_cost,
                pr.fuel_type as fuel_type, 
                d.name as department_name, 
                r.name as employee_name
                from fuel_plan p
                left join fuel_quantity q on (p.id=q.plan_id)
                left join fuel_qty_line l on (q.id=l.qty_id)
                left join fleet_vehicle v on (v.id= l.vehicles_id)
                left join hr_department d on (d.id= v.department_id)
                left join hr_employee e on (e.id= v.employee_id)
                left join resource_resource r on (r.id= e.resource_id)
                left join product_product pr on (pr.id= l.product_id)
                left join product_template t on (t.id= pr.product_tmpl_id)
                left join product_uom u on (t.uom_id= u.id)
                where 
                    q.fuel_type = 'fixed_fuel' and p.type_plan='constant_fuel' and p.month = %s and p.year=%s
		        '''  + department_condition + " order by d.name",(str(month),str(year))) 
        res = self.cr.dictfetchall()
        return res

    def _getdata1(self,data):
        month= data['form']['month']
        year= data['form']['year']
        self.cr.execute('''
                select p.id as plan_id,
            p.name as name,
		    p.date as date,
		    p.month as month,	
		    p.year as year
                from fuel_plan p
                where p.month = %s and p.year=%s and p.type_plan='constant_fuel'
                ''',(month,str(year)))  
        res = self.cr.dictfetchall()
        return res
    
    def _getdata2(self,data):
        """This function compute the total of gasoline and petrol for the report
        """
        res = self._getdata(data)
        gasoline_qty = 0.0
        petrol_qty = 0.0
        for line in res:
            gasoline_qty += line.get('product_qty') if line['fuel_type'] == 'gasoline' else 0
            petrol_qty += line.get('product_qty') if line['fuel_type'] == 'petrol' else 0
        res_qty = {}
        res_qty['gasoline_qty'] = gasoline_qty  
        res_qty['petrol_qty'] = petrol_qty  
        return [res_qty]                       

    def _getdata3(self,data):
        """This function return the department name """
        department = data['form']['department_id']
        department_id = department and department[0] or 0
        self.cr.execute('''
                select 
                    d.name as department_name
                from hr_department d
                where  d.id = %s
                ''',(department_id,) )  
        res = self.cr.dictfetchall()
        return res

report_sxw.report_sxw('report.fuel.plan.report', 'fuel.plan', 'addons/fuel_management/report/fuel_plan_report.rml' ,parser=fuel_plan_report,header=False)

# fuel outgoing wizard report for specific month
class fuel_outgoing_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fuel_outgoing_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self._getdata1,
            'line2':self._getdata2,
            'genarl':self._gen,


        })
        self.context = context
    def _getdata(self,data):
        month= data['form']['month']
        year= data['form']['year']
        c = data['form']['company_id']
        first_date = date(year= year, month= int(month), day=1)
        # Last Day of the Month 
        if first_date.month < 12:
            next_month = date(year=first_date.year, month=first_date.month+1, day=1)
        else:
            next_month = date(year=first_date.year + 1, month=1, day=1)
        
        last_day = next_month - timedelta(days=1)
        self.cr.execute('''select * from(
                select v.name as vehicles_name,
                t.name as product_name, 
                l.product_qty as product_qty,
                t.standard_price * product_qty as product_cost,
                pr.fuel_type as fuel_type, 
                hs.purpose as product_purpose, 
                d.name as department_name, 
                r.name as employee_name 
                from fuel_request hs
                left join fuel_request_lines l on (hs.id=l.fuel_id)
                left join product_product pr on (pr.id= l.product_id)
                left join product_template t on (t.id= pr.product_tmpl_id)
                left join fleet_vehicle v on (hs.car_id = v.id)
                left join hr_employee e on (e.id= v.employee_id)
                left join resource_resource r on (r.id= e.resource_id)
                left join hr_department d on (d.id= v.department_id)
                where hs.state = 'done' and hs.date between %s and %s and t.company_id=%s
        union all  select
                v.name as vehicles_name , 
                t.name as product_name, 
                l.product_qty as product_qty,
                l.price_unit * product_qty as product_cost,
                pr.fuel_type as fuel_type, 
                'monthly' as product_purpose, 
                d.name as department_name, 
                r.name as employee_name 
                from fuel_plan p
                left join fuel_quantity q on (p.id=q.plan_id)
                left join fuel_qty_line l on (q.id=l.qty_id)
                left join fleet_vehicle v on (v.id= l.vehicles_id)
                left join hr_department d on (d.id= v.department_id)
                left join hr_employee e on (e.id= v.employee_id)
                left join resource_resource r on (r.id= e.resource_id)
                left join product_product pr on (pr.id= l.product_id)
                left join product_template t on (t.id= pr.product_tmpl_id)
                left join product_uom u on (t.uom_id= u.id)
                where q.fuel_type = 'fixed_fuel' and p.month = %s and p.year=%s and t.company_id=%s
        ) as fuel_details
        order by department_name,vehicles_name ''',(first_date,last_day,c[0], str(month),str(year),c[0])) 

        res = self.cr.dictfetchall()
        return res

    def _getdata1(self,data):
        month= data['form']['month']
        year= data['form']['year']
        res = {}
        res['month'] = month
        res['year'] = year
        return [res]

    
    def _getdata2(self,data):
        """This function compute the total of gasoline and petrol
        """
        res = self._getdata(data)
        gasoline_qty = 0.0
        petrol_qty = 0.0
        for line in res:
            gasoline_qty += line.get('product_qty') if line['fuel_type'] == 'gasoline' else 0
            petrol_qty += line.get('product_qty') if line['fuel_type'] == 'petrol' else 0
        res_qty = {}
        res_qty['gasoline_qty'] = gasoline_qty  
        res_qty['petrol_qty'] = petrol_qty  
        return [res_qty]
    def _gen(self,data):
        month= data['form']['month']
        year= data['form']['year']
        c = data['form']['company_id']
        month_add='0'+month
        listt=[]
        dic={}
        check=0
        check1=0
        no=0
        self.cr.execute('''SELECT 
  sum(s.product_qty) as summ,  
  req.parent_id as par,
  s.name as sname
FROM 
  public.fuel_request as req, 
  public.fuel_request_lines as req_lin, 
  public.stock_move as s,
  public.fuel_picking as f, 
  hr_department as hr,
  res_company as res

WHERE 
  req.id = req_lin.fuel_id AND
  req_lin.move_id = s.id and 
  f.department_id = hr.id AND hr.company_id=res.id and
  f.id = s.fuel_picking_id  and s.location_id=367 and 
  to_char(f.date,'mm')>=%s and to_char(f.date,'mm') <=%s
and res.id=%s  GROUP BY   req.parent_id ,sname ''',(month_add,month_add,c[0]))
        res = self.cr.dictfetchall()
        for dep in res:
              no=+1
              self.cr.execute('''select                
                l.product_qty as product_qty ,
                d.name  as hname,
                d.id as hid
                from fuel_plan p
                left join fuel_quantity q on (p.id=q.plan_id)
                left join fuel_qty_line l on (q.id=l.qty_id)
                left join hr_department d on (d.id= q.department_id)
                left join product_product pr on (pr.id= l.product_id)
                left join product_template t on (t.id= pr.product_tmpl_id)
                left join product_uom u on (t.uom_id= u.id)
                where q.fuel_type = 'extra_fuel' and p.month =%s and d.id=%s and p.year='%s' and t.company_id=%s
        order by hname''',(month,dep['par'],year,c[0]))
              quty_plan= self.cr.dictfetchall()
              i=0
              if len(quty_plan) > i :
               check=quty_plan[i]['hname']
               check1=quty_plan[i]['product_qty']
              dic={'product_qty':check1,'hname':check,'qtsum':dep['summ'],'sname':dep['sname'],'store_fuel':float(check1-dep['summ'])}
              listt.append(dic)
        return listt
    
        
report_sxw.report_sxw('report.fuel.outgoing.report', 'fuel.plan', 'addons/fuel_management/report/fuel_outgoing_report.rml' ,parser=fuel_outgoing_report,header=False)
report_sxw.report_sxw('report.gen.extra.report', 'fuel.plan', 'addons/fuel_management/report/gen_extra_report.rml' ,parser=fuel_outgoing_report,header=False)
