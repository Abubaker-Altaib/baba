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
# Class Ticket Booking report
#----------------------------------------
class ticket_booking_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ticket_booking_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        ticket_type = data['form']['type']
        state= data['form']['state']
        partner_id= data['form']['partner_id']
        department_id= data['form']['department_id']
        employee_id= data['form']['employee_id']
        foreigner_id= data['form']['foreigner_id']
        procedure_for= data['form']['procedure_for']
        company_id= data['form']['company_id']
        travel_purpose= data['form']['travel_purpose']
        where_condition = ""
        where_condition += ticket_type and " and t.type='%s'"%ticket_type or ""
        where_condition += travel_purpose and " and t.travel_purpose='%s'"%travel_purpose or ""
        where_condition += procedure_for and (procedure_for == 'both' and "" or procedure_for == 'sudanese' and " and t.procedure_for='sudanese' " or procedure_for == 'foreigners' and " and t.procedure_for='foreigners'") or ""
        where_condition += state and "and t.state ='%s'" %state or ""
        where_condition += department_id and " and t.department_id=%s"%department_id[0] or ""
        where_condition += employee_id and " and e.emp_id=%s"%employee_id[0] or ""
        where_condition += company_id and " and t.company_id=%s"%company_id[0] or ""
        where_condition += foreigner_id and " and l.foreigner_id=%s"%foreigner_id[0] or ""
        where_condition += partner_id and " and t.travel_agency=%s"%partner_id[0] or ""
        self.cr.execute('''
           select
                t.name as name , 
                t.date as date,
                t.procedure_for as procedure_for, 
                t.state as state, 
                t.type as type , 
                d.name as department_name,
                t.date_of_travel as date_of_travel,
                t.date_of_return as date_of_return,
		t.cost_of_travel as cost_of_travel,
		t.travel_route as travel_route ,
		t.carrier as carrier ,
		r.name as emp_name ,
		p.name as partner_name ,
		l.foreigner_name as foreigner_name ,
		t.travel_purpose as travel_purpose
            from ticket_booking t
                left join hr_department d on (d.id=t.department_id)
                left join foreigners_ticket_lines l on (t.id= l.request_id)
                left join employee_ticket_booking_rel e on (t.id= e.ticket_booking_id)
		left join hr_employee hr on (e.emp_id=hr.id)
		left join resource_resource r on (hr.resource_id = r.id )
		left join res_partner p on (t.travel_agency = p.id)
                where
                (to_char(t.date,'YYYY-mm-dd')>=%s and to_char(t.date,'YYYY-mm-dd')<=%s)
                '''  + where_condition + " order by t.name",(date_from,date_to)) 
        res = self.cr.dictfetchall()
        return res
    
report_sxw.report_sxw('report.ticket_booking.report', 'ticket.booking', 'addons/public_relation/report/ticket_booking.rml' ,parser=ticket_booking_report,header=False)
