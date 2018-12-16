# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# fuel monthly compare         ----------------------------------------------------------------------------------------------------------------
class compare_fuel(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(compare_fuel, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
	    'line2':self._getdata2,
	    'line3':self._getsum,
	    'line4':self._getsum2,
	    'line5':self._getextrafuel,
	    'line6':self._getextrafuel2,
        })

    def _getdata(self,data):

           month= data['form']['first_month']
           year= data['form']['first_year']

           self.cr.execute("""
                 select q.department_id as id , h.name as dept  , q.gasoline_qty  as gaz , q.petrol_qty as benz 


			from fuel_plan p 

		left join fuel_archive_quantity q on (q.plan_id = p.id)
		left join hr_department h on (q.department_id = h.id)

		where q.fuel_type ='fixed_fuel' and p.month=%s  and p.year=%s """,(month,year)) 
           res = self.cr.dictfetchall()
           return res






    def _getdata2(self,data,num):


           month= data['form']['second_month']
           year= data['form']['second_year']

           self.cr.execute("""
                 select q.gasoline_qty  as gaz , q.petrol_qty as benz 


			from fuel_plan p 

		left join fuel_archive_quantity q on (q.plan_id = p.id)

		where q.fuel_type ='fixed_fuel' and q.department_id=%s and p.month=%s  and p.year=%s """,(num,month,year)) 
           res = self.cr.dictfetchall()
           return res

    def _getsum(self,data):


           month= data['form']['first_month']
           year= data['form']['first_year']

           self.cr.execute("""
                 select sum(q.gasoline_qty)  as gaz , sum(q.petrol_qty) as benz 


			from fuel_plan p 

		left join fuel_archive_quantity q on (q.plan_id = p.id)

		where p.month=%s  and p.year=%s """,(month,year)) 
           res = self.cr.dictfetchall()
           return res

    def _getsum2(self,data):


           month= data['form']['second_month']
           year= data['form']['second_year']

           self.cr.execute("""
                 select sum(q.gasoline_qty)  as gaz , sum(q.petrol_qty) as benz 


			from fuel_plan p 

		left join fuel_archive_quantity q on (q.plan_id = p.id)

		where p.month=%s  and p.year=%s and p.state='done' """,(month,year)) 
           res = self.cr.dictfetchall()
           return res 


    def _getextrafuel(self,data):

           month= data['form']['first_month']
           year= data['form']['first_year']

           self.cr.execute("""
                 select sum(q.gasoline_qty)  as gaz , sum(q.petrol_qty) as benz 


			from fuel_plan p 

		left join fuel_archive_quantity q on (q.plan_id = p.id)

		where q.fuel_type ='extra_fuel' and p.month=%s  and p.year=%s """,(month,year)) 
           res = self.cr.dictfetchall()
           return res






    def _getextrafuel2(self,data):


           month= data['form']['second_month']
           year= data['form']['second_year']

           self.cr.execute("""
                 select sum(q.gasoline_qty)  as gaz , sum(q.petrol_qty) as benz 


			from fuel_plan p 

		left join fuel_archive_quantity q on (q.plan_id = p.id)

		where q.fuel_type ='extra_fuel' and p.month=%s  and p.year=%s """,(month,year)) 
           res = self.cr.dictfetchall()
           return res


 
report_sxw.report_sxw('report.compare_fuel.report', 'fuel.plan', 'addons/fuel_management/report/compare_fuel.rml' ,parser=compare_fuel,header=False )
