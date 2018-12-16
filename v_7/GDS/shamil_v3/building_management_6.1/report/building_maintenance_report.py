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

#----------------------------------------
# Class building maintenance report
#----------------------------------------
class building_maintenance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_maintenance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        maintenance_type = data['form']['maintenance_type']
        state= data['form']['state']
        building_id= data['form']['building_id']
        partner_id= data['form']['partner_id']
        where_condition = ""
        where_condition += maintenance_type and " and t.id=%s"%maintenance_type[0] or ""
        where_condition += state and (state == 'completed' and " and b.state= 'done' " or " and b.state != 'done' ") or ""
        where_condition += building_id and " and bm.id=%s"%building_id[0] or ""
        where_condition += partner_id and " and p.id=%s"%partner_id[0] or ""
        self.cr.execute('''
            select
                b.name as name , 
                b.date as date,
                b.cost as cost, 
                b.state as state, 
                t.name as type_name , 
                d.name as department_name,
                p.name as partner_name,
                bm.name as building_name
            from building_maintenance b
                left join building_maintenance_type t on (t.id=b.maintenance_type)
                left join hr_department d on (d.id=b.department_id)
                left join res_partner p on (p.id= b.partner_id)
                left join building_manager bm on (bm.id= b.building_id)
                where
                (to_char(b.date,'YYYY-mm-dd')>=%s and to_char(b.date,'YYYY-mm-dd')<=%s)
                '''  + where_condition + " order by b.name",(date_from,date_to)) 
        res = self.cr.dictfetchall()
        return res
    
report_sxw.report_sxw('report.building_maintenance.report', 'building.maintenance', 'addons/building_management/report/building_maintenance_report.rml' ,parser=building_maintenance_report,header=False)
