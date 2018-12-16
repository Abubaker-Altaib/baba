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
            'line1':self._getitem,
        })
    def _getdata(self,data):
           where_condition = "where (to_char(b.accident_date,'YYYY-mm-dd')>=%s and to_char(b.accident_date,'YYYY-mm-dd')<=%s) """ 
           args_list = (data['form']['Date_from'],data['form']['Date_to'],)
           if data['form']['accident_type_id']:
              where_condition +=  "and l.accident_type=%s"
              args_list +=(data['form']['accident_type_id'][0],)
           if data['form']['building_id']:
              where_condition +=  "and b.building_id=%s"
              args_list +=(data['form']['building_id'][0],)
           if data['form']['partner_id'] :
              where_condition +=  "and b.partner_id=%s"
              args_list +=(data['form']['partner_id'][0],)
           if data['form']['company_id']:
              where_condition +=  "and b.company_id=%s"
              args_list +=(data['form']['company_id'][0],)
           if data['form']['state']:
              where_condition += "and b.state=%s"
              args_list +=(data['form']['state'],)
	   self.cr.execute("""
                SELECT 
                                  distinct (b.id) as accident_id,
                                  b.name as detail_name ,
				  b.accident_date as accident_date ,
				  m.name as building_name , 
				  b.coverage_date as coverage_date ,
				  b.repayment_cost as repayment_cost ,
				  b.estimated_cost as estimated_cost,
				  b.state as state ,
				  res.name as company ,
				  p.name as partner 
                FROM building_accident b
                left join accident_lines l on (b.id = l.accident_id)
		left join building_building m on (b.building_id = m.id)
		left join res_partner p on (b.partner_id = p.id)
		left join res_company res on (b.company_id = res.id)""" + where_condition + """
		ORDER BY b.name """, args_list)
           res = self.cr.dictfetchall()
           return res

    def _getitem(self,accident_id):
        accident_obj = self.pool.get('building.accident')
        return accident_obj.browse(self.cr,self.uid,accident_id).lines_ids

report_sxw.report_sxw('report.building_accident.report', 'building.accident', 'addons/building_management/report/building_accident.rml' ,parser=building_accident , header=False)
