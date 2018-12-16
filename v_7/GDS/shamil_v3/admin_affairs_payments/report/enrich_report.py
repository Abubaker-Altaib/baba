# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw

class enrich_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(enrich_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line1':self._get_sum,
            'line2':self._get_dept,
            'line3':self._get_data,

        })
    def _get_sum(self,data):
            date_company= data['form']['company_id']
            date_month= data['form']['month']
            date_year= data['form']['year']
            enrich = data['form']['payment_enrich']
            where_condition = ""
            where_condition += date_month and " p.month = '%s'"%date_month or ""
            where_condition += date_year and " and p.year='%s' "%date_year or ""
            where_condition += enrich and " and p.id=%s"%enrich[0] or ""
            where_condition += date_company and " and p.company_id=%s"%date_company[0] or ""
            self.cr.execute("""select distinct c.name as enrich_name , 
                                                   p.amount as amount , 
                                                   p.residual_amount as residual_amount , 
                                                   p.paid_amount as paid_amount
	                              from payment_enrich p
	                              left join enrich_category c on (p.enrich_category = c.id)
	                              left join res_company r on (p.company_id = r.id)
 	                              where """+where_condition)
            res = self.cr.dictfetchall()
            return res

    def _get_dept(self,data):
            date_company= data['form']['company_id']
            date_month= data['form']['month']
            date_year= data['form']['year']
            enrich = data['form']['payment_enrich']
            res=[]
            result=[]
            result2=[]
            dic = {}
            where_condition = ""
            where_condition += date_month and " p.month = '%s'"%date_month or ""
            where_condition += date_year and " and p.year='%s' "%date_year or ""
            where_condition += enrich and " and p.id=%s"%enrich[0] or ""
            where_condition += date_company and " and p.company_id=%s"%date_company[0] or ""
            self.cr.execute("""select distinct l.department_id as dept 
                                from payment_enrich p 
                                left join payment_enrich_lines l on (l.enrich_id = p.id)
 	                              where """+where_condition)
            result = self.cr.dictfetchall()
            for r in result : 
                self.cr.execute("""select min(h.id) as dept_id,min(h.name) as dept_name , 
                                          sum(l.cost) as total 
                                   from payment_enrich p 
                                    left join payment_enrich_lines l on (l.enrich_id = p.id)
		                            left join hr_department h on (l.department_id = h.id)
                                    where l.department_id = %s and p.id=%s""",(r['dept'],enrich[0]))
                result2 = self.cr.dictfetchall()
                for record in result2 : 
                    dic = {'dept_id':record['dept_id'],'dept_name':record['dept_name'],'amount':record['total']}
                res.append(dic)
            return res

    def _get_data(self,data,dept_id):
            date_company= data['form']['company_id']
            date_month= data['form']['month']
            date_year= data['form']['year']
            enrich = data['form']['payment_enrich']
            self.cr.execute("""select l.name as details , l.date as date , l.cost as amount  
                                    from payment_enrich p 
                                    left join payment_enrich_lines l on (l.enrich_id = p.id)
		                            left join hr_department h on (l.department_id = h.id)
                                    where l.department_id = %s and p.id=%s """,(dept_id,enrich[0]))
            res = self.cr.dictfetchall()
            return res

report_sxw.report_sxw('report.enrich_report.report','payment.enrich','addons/admin_affairs_payments/report/enrich_report.rml',parser=enrich_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
