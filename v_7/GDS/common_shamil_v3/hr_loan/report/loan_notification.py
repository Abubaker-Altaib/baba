# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields, orm
import time
import re
from report import report_sxw
import calendar
import datetime
from base_custom import amount_to_text_ar
import decimal_precision as dp
from tools.translate import _

class loan_notification(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
            super(loan_notification, self).__init__(cr, uid, name, context)
            self.localcontext.update({
                'time': time,
                'line':self._pars,
                'employee':self._get_emp,
                'totol':self._total,
            })
        
            self.cr = cr
            self.uid = uid
            self.context = context

      def set_context(self, objects, data, ids, report_type=None):
            x=0
            for obj in self.pool.get('hr.employee.loan').browse(self.cr, self.uid, ids, self.context):
                x=obj.acc_number 
                if (x==False ):          
	               raise osv.except_osv(_('Error!'), _('You can not print notification. This loan is not transferred yet!'))

            return super(loan_notification, self).set_context(objects, data, ids, report_type=report_type)

      def _pars(self):
            res = amount_to_text_ar.amount_to_text(globals()['total'])
            return res

      def _total(self,p,h):
            koo=[]
            koo= self._get_emp(p.loan_id.id ,p.acc_number )
            return  globals()['total']


      def _get_emp(self,p,h):
            total=0
            top_res=[]
            self.cr.execute(''' 
                        select e.emp_code as code,  r.name AS emp_name,
                        start_date as s_dae, loan_amount as loan, installment_amount as install,
                        ceil(loan_amount/installment_amount) as num
                        from hr_employee as e
                        left join resource_resource as r on (e.resource_id=r.id)
                        left join hr_employee_loan l on (e.resource_id=l.employee_id)
                        where l.state='transfered' and l.loan_id=%s  and l.acc_number=%s''',(p,h))
            nw_res=self.cr.dictfetchall()
            i= 0
            while(i< len(nw_res)):
               total+=nw_res[i]['loan']
               dic={
                   'no':i+1,
                   'code':nw_res[i]['code'],
                   'emp_name':nw_res[i]['emp_name'],
                   's_dae':nw_res[i]['s_dae'],
                   'loan':round(nw_res[i]['loan'],2),
                   'install':round(nw_res[i]['install'],2),
                   'num':int(nw_res[i]['num']),
                    } 
               top_res.append(dic)
               i+=1
            globals()['total']=total
            return top_res
         
report_sxw.report_sxw('report.loan.notification.report', 'hr.employee.loan', 'addons/hr_loan/report/loan_notification.rml' ,parser=loan_notification ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
