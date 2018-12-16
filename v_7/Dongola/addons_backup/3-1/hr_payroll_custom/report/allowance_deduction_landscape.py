# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw
from mako.template import Template
from openerp.report.interface import report_rml
from openerp.report.interface import toxml

class allowance_deduction_landscape(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(allowance_deduction_landscape, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._process,  
        })

    def _process(self,data):
        row=[]
        col=[]
        sums=[]
        allow_deduct_ids=self.pool.get('hr.allowance.deduction').browse(self.cr,self.uid, data['allow_deduct_ids'])
        employee_ids=self.pool.get('hr.employee').browse(self.cr,self.uid, data['employee_ids'])
        self.cr.execute(
            '''SELECT adr.amount AS amount,
            pm.employee_id AS employee, adr.allow_deduct_id AS allow_deduct
            FROM hr_allowance_deduction_archive adr
            LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id)
            WHERE pm.month =%s and pm.year =%s 
            and pm.employee_id IN %s 
            and adr.allow_deduct_id IN %s ''',(data['month'],data['year'],tuple(data['employee_ids']),tuple(data['allow_deduct_ids']))) 
        res = self.cr.dictfetchall()
        amounts=dict([((r['employee'],r['allow_deduct']), r['amount']) for r in res])
        self.cr.execute(
            '''SELECT pm.basic_salary AS basic_salary,
            pm.employee_id AS employee
            FROM hr_payroll_main_archive pm 
            WHERE pm.month =%s and pm.year =%s
            and pm.employee_id IN %s ''',(data['month'],data['year'],tuple([data['employee_ids'][0]]),)) 
        res2 = self.cr.dictfetchall()
        basics=dict([(r['employee'], r['basic_salary']) for r in res2])
        for allow_deduct in allow_deduct_ids:
            col.append(allow_deduct.name)
            sums.append(0)
        col.append(u'المرتب الاساسي ')
        col.append(u'الموظف/الاستحقاق ')
        row.append(col)
        for emp in employee_ids:
            col=[]  
            for allow_deduct in allow_deduct_ids:
                amount= amounts.get((emp.id,allow_deduct.id), 0.0)
                col.append(amount)
            basic_salary= basics.get(emp.id, 0.0)
            col.append(basic_salary)
            col.append(emp.name)
            row.append(col)
         
        return row

report_sxw.report_sxw('report.allowance.deduction.landscape', 'hr.allowance.deduction.archive', 'hr_payroll_custom/report/allowance_deduction_landscape.mako' ,parser=allowance_deduction_landscape,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
