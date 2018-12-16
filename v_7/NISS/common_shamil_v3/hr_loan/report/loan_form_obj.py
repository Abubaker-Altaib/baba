# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import re
from report import report_sxw
from openerp.osv import osv, fields, orm
import calendar
import datetime
from openerp.tools.translate import _

class loan_form_obj(report_sxw.rml_parse):
     def __init__(self, cr, uid, name, context):
            super(loan_form_obj, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
                'loan':self._get_loan,
                'get_employee':self._get_employee,
                'info':self._loan_info,
            })

     def _get_employee(self,emp):
            payroll_obj= self.pool.get('hr.payroll.main.archive')
            self.cr.execute (''' select id as id from hr_payroll_main_archive \
                                 where month=(select max(month)from hr_payroll_main_archive where year =(select max(year)\
                                 from hr_payroll_main_archive)) and employee_id= %s'''%(emp.id))
            try :
               emp_id=self.cr.dictfetchall()[0]['id']
            except Exception, exc:
               self.cr.rollback()
               raise osv.except_osv(_('ERROR'), _('This employee has not salary'))
            emp_detail= payroll_obj.search(self.cr, self.uid,[('id','=',emp_id),])
            archive_obj=payroll_obj.browse(self.cr,self.uid,emp_detail)
            res={}
            for arc in archive_obj: 
                res={
                     'net':arc.net,
                     'total_deduction':arc.total_deduction,
                     'total_allownce':arc.total_allowance,
                     'total_loans':arc.total_loans,
                }
            return [res]

     def _loan_info(self,j):
         self.cr.execute(''' 
                        SELECT 
                        start_date as s_date,installment_amount as instal,loan_amount as loan,ceil(loan_amount/installment_amount) as coun
                        FROM hr_employee_loan 
                        where id=%s''',(j.id)) 
         res=self.cr.dictfetchall()
         dic={
               's_date':res[0]['s_date'],
               'instal':round(res[0]['instal'],2),
               'loan':round(res[0]['loan'],2),
               'coun':int(res[0]['coun']),
             }
         return dic
     def _get_loan(self,emp,loan):
        self.cr.execute('''select reject_reasons as reason from hr_employee_loan where employee_id =%s and loan_id=%s''',(emp.id,loan.id))
        res = self.cr.dictfetchall()
        if(len(res) > 0):
             return res
        else: 
             li = []
             a = {'reason':'10',}
             li.append(a)
             return li


report_sxw.report_sxw('report.loan.form.report.obj', 'hr.employee.loan', 'addons/hr_loan/report/loan_form_obj.rml' ,parser=loan_form_obj ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
