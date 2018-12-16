#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


class building_accident(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_accident, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })
    def _getdata(self,data):
           date_company= data['form']['company_id']
           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           data_building = data['form']['building_id']
	   data_car = data['form']['car_id']
	   data_station = data['form']['station_id']
	   data_category = data['form']['accident_category']
	   data_state = data['form']['state']
	   data_accident = data['form']['accident_type_id']
	   data_partner = data['form']['partner_id']
           where_condition = ""
           where_condition += data_category and " and b.accident_category='%s'"%data_category or ""
           where_condition += data_accident and "and b.accident_type_id=%s"%data_accident[0] or ""
           where_condition += data_state and "and b.state ='%s'" %data_state or ""
           where_condition += data_building and " and b.building_id=%s"%data_building[0] or ""
           where_condition += data_car and " and b.car_id=%s"%data_car[0] or ""
           where_condition += date_company and " and b.company_id=%s"%date_company[0] or ""
           where_condition += data_station and " and b.station_id=%s"%data_station[0] or ""
           where_condition += data_partner and " and b.partner_id=%s"%data_partner[0] or ""
	   self.cr.execute("""
                SELECT 
                                  b.name as detail_name ,
				  b.accident_date as accident_date ,
				  m.name as building_name , 
				  ms.name as station_name , 
				  h.name as dept ,
				  t.name as accident_type ,
				  b.accident_category as accident_category ,
				  b.accident_desc as accident_desc ,
				  f.name as car_name ,
				  b.coverage_date as coverage_date ,
				  b.repayment_cost as repayment_cost ,
				  b.accident_location as accident_location ,
				  b.estimated_cost as estimated_cost,
				  b.state as state ,
				  r.name as building_company ,
				  rs.name as station_company ,
				  res.name as company ,
				  p.name as partner ,
				  b.maintenance_desc as maintenance_desc
                FROM building_accident b
		left join building_manager m on (b.building_id = m.id)
		left join building_manager ms on (b.station_id = ms.id)
		left join hr_department h on (b.car_department_id = h.id)
		left join accident_type t on (b.accident_type_id=t.id)
		left join fleet_vehicles f on (b.car_id = f.id)
		left join res_partner p on (b.partner_id = p.id)
		left join res_company r on (b.building_company_id= r.id)
		left join res_company rs on (b.station_company_id= rs.id)
		left join res_company res on (b.company_id = res.id)
		where (to_char(b.accident_date,'YYYY-mm-dd')>=%s and to_char(b.accident_date,'YYYY-mm-dd')<=%s)"""  + where_condition + """ORDER BY b.name """,(date_from,date_to))
           res = self.cr.dictfetchall()
           return res

report_sxw.report_sxw('report.building_accident.report', 'building.accident', 'addons/building_management/report/building_accident.rml' ,parser=building_accident , header=False)
