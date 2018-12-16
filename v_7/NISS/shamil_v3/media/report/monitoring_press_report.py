#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Report to print information of daily newspapers in a certain period of time, according to certain paper
#----------------------------------------
# Class monitoring press report
#----------------------------------------
class monitoring_press_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(monitoring_press_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getdata2,
        })

    def _getdata2(self,data):
	""""Old code to count the total topics 
			    (select count(1) from monitoring_press_lines ll where (ll.p_name = p.id)) as total_topics 		"""
        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        data_paper = data['form']['paper_id']
        evaluation= data['form']['evaluation']
        where_condition = ""
        where_condition += evaluation and " and l.evaluation='%s'"%evaluation or ""
        where_condition += data_paper and " and p.id=%s"%data_paper[0] or ""  
        self.cr.execute("""
                SELECT distinct
                    min(p.id) as id ,
                    min(p.name) as paper_name,
		    count(p.id) as total_topics
                FROM 
                    monitoring_press_lines l 
                    left join news_papers p on (l.p_name = p.id)
                    left join monitoring_press m on (l.press_id = m.id)
                where
                    (to_char(l.release_date,'YYYY-mm-dd')>=%s and to_char(l.release_date,'YYYY-mm-dd')<=%s)""" + where_condition,(date_from,date_to))
        res = self.cr.dictfetchall()
        return res

    def _getdata(self,data,paper_data):
           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           paper_id = paper_data
           evaluation= data['form']['evaluation']
           where_condition = ""
           where_condition += evaluation and " and l.evaluation='%s'"%evaluation or ""
           self.cr.execute("""
                 SELECT
		m.name as monitoring_no,
                l.paper_number as paper_number , 
                l.no_page as no_page , 
                l.release_date as release_date , 
                l.subject as subject , 
                l.writer as writer ,
                l.template_press as template_press ,
		l.evaluation as evaluation 
                FROM 
                    monitoring_press_lines l 
                    left join news_papers p on (l.p_name = p.id)
                    left join monitoring_press m on (l.press_id = m.id)
                where
                     (to_char(l.release_date,'YYYY-mm-dd')>=%s and to_char(l.release_date,'YYYY-mm-dd')<=%s) and
                     l.p_name =%s""" + where_condition + "order by m.name",(date_from,date_to,paper_id)) 
           res = self.cr.dictfetchall()
           return res

report_sxw.report_sxw('report.monitoring_press.report', 'monitoring.press', 'addons/media/report/monitoring_press_report.rml' ,parser=monitoring_press_report , header=False)
