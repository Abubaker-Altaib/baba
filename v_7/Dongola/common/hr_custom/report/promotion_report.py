# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp.tools.translate import _


class promotion_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(promotion_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_emp':self._get_emp,
            'line5':self.get_promotion_total,
        })

    def get_promotion_total(self,data,choice,date1_v,date2_v):
        process_archive=self.pool.get('hr.process.archive')
        # res = process_archive.self(self,choice,'promotion_date','promotion_date',date1_v,date2_v)
        res = process_archive._archive_count(self,choice,'promotion_date','promotion_date',date1_v,date2_v)
        return res
    
    def _get_emp(self,data):
        date1 = data['form']['fromm']
        date2 = data['form']['to'] 
        self.cr.execute('''
            SELECT ROW_NUMBER ( ) 
                OVER (order by p.id) as no,e.emp_code as code,r.name as emp,p.approve_date as date,
            d.name AS degree FROM hr_process_archive AS p 
            left join hr_employee AS e on (p.employee_id=e.id) 
            left join  resource_resource AS r on (e.resource_id=r.id) 
            left join hr_salary_degree AS d on (e.degree_id=d.id)
            where 
            e.employment_date < p.approve_date and
            p.approve_date between %s and %s 
            ''',(date1,date2)) 
        
        res = self.cr.dictfetchall()
        if not res:
            raise osv.except_osv(_('Error'), _('No  Data Found ...'))
        return res
      

report_sxw.report_sxw('report.promotion.report', 'hr.process.archive','addons/hr_custom/report/promotion_report.rml', parser=promotion_report, header=True)
