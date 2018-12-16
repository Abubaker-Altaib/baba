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
class all_rented_cars(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(all_rented_cars, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'gov':self.get_gov,
        })


    def get_gov(self,data):
        chosing=data['form']['choose_type']
        owen=()
        if chosing=='goverment':
            owen=('owned',)
        elif chosing=='rented':
            owen=('rented',)
        elif chosing=='all_car':
            owen=('rented','owned') 
        status='active'
        
        self.cr.execute("""SELECT distinct
  f.ownership as owen, 
  f."name" as car_name, 
  f.monthly_plan as fuel, 
  h."name" as dep_name,
  res.name as emp_name,
  f.license_plate as car_no,
  h.name as dep_name

                FROM  fleet_vehicle f 
        left join hr_employee emp on (f.employee_id = emp.id)
        left join resource_resource res on (emp.resource_id = res.id)
        left join hr_department h on (f.department_id = h.id)
        where  f.status=%s and f.ownership in %s order by car_name
            """,(status,tuple(owen) ))
        result=self.cr.dictfetchall()
        print result,"roroooooooo"
        return result 
report_sxw.report_sxw('report.gov_rent.report', 'rented.cars', 'addons/services/report/gov_rented_cars.rml' ,parser=all_rented_cars , header=False)
