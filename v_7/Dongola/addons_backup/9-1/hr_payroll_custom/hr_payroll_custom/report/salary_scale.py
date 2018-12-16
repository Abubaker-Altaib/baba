# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class salary_scale(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(salary_scale, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._process,
            'allow':self._get_allowance,
            'get_degree':self.get_degree,
            
        })

    def get_degree(self,form):
        result = []
        result = self.pool.get('hr.salary.degree').browse(self.cr,self.uid, form['degree_ids'])
        return result

    def _process(self,degree):
        self.cr.execute('''SELECT m.basic_salary AS basic_salary,m.name AS bonus_name 
                           FROM hr_salary_bonuses AS m 
                           WHERE m.degree_id =%s  '''%(degree)) 
        res = self.cr.dictfetchall()
        return res

    def _get_allowance(self,data,degree_id):
        salary_obj = self.pool.get('hr.salary.allowance.deduction')
        al_de_ids= salary_obj.search(self.cr,self.uid, [('payroll_id','=',data['payroll_id'][0]),('degree_id','=',degree_id),('allow_deduct_id.in_salary_sheet','=',True)])
        return salary_obj.browse(self.cr,self.uid, al_de_ids)

report_sxw.report_sxw('report.salary.scale', 'hr.salary.scale', 'addons/hr_payroll_custom/report/salary_scale.rml' ,parser=salary_scale)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
