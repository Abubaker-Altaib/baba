#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Foreigners Procedur report  
# Report to print Foreigners in a certain period of time, according to certain options
# 1 - Department
# 2 - States       ----------------------------------------------------------------------------------------------------------------
class foreigners_procedures_specific(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(foreigners_procedures_specific, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
#            'line2':self._getforeigner,
#            'line3':self._getprocedure,
#            'line4':self._getcount,
#            'line5':self._getcount_done,
#            'line6':self._getcount_notdone,

        })
    def _getdata(self,data):
	   date_from= data['form']['Date_from']
	   date_to= data['form']['Date_to']
           data_department = data['form']['department_id']
	   data_state = data['form']['state']
	   company = data['form']['company_id']
	   procedure_for = data['form']['procedure_for']
           where_condition = ""
           where_condition += data_state and " and p.state='%s'"%data_state or ""
           where_condition += data_department and " and p.department_id=%s"%data_department[0] or ""
           where_condition += company and " and p.company_id=%s"%company[0] or ""
           where_condition += procedure_for and " and p.procedure_for='%s'"%procedure_for or ""
                    	
           self.cr.execute("""
				select p.name as request_name,
					f.name as procedure ,
					p.request_date as request_date ,
					p.procedure_date as procedure_date ,
					p.state as state,
				       	h.name as dept ,
					p.procedure_for as procedure_for ,
					c.name as company ,
					s.sudanese_name as sudanese_name ,
					s.passport_num as passport_num ,
					fp.foreigner_name as foreigner_name ,
					fp.passport_num as fore_passport_num,
					pu.name as  purpose ,
					p.notes as notes 

				from foreigners_procedures_request p
				left join hr_department h on (p.department_id = h.id)
				left join res_company c on (p.company_id = c.id)
				left join foreigners_procedures f on (p.procedure_id = f.id)
				left join sudanese_procedures_lines s on (p.id=s.request_id)
				left join foreigners_procedures_lines fp on (p.id = fp.request_id)
				left join foreigners_purpose pu on (p.purpose = pu.id)
			where (to_char(p.request_date,'YYYY-mm-dd')>=%s and to_char(p.procedure_date,'YYYY-mm-dd')<=%s)""" + where_condition + "order by p.name ",(date_from,date_to)) 
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.foreigners.procedures.specific.report', 'foreigners.procedures.request', 'addons/public_relation/report/foreigners_procedures_for_specific_time.rml' ,parser=foreigners_procedures_specific,header=False)
