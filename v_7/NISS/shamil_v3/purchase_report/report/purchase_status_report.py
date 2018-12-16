# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Purchases Statuses report 
class purchase_status_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(purchase_status_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2' :self._getamount,
            'line3' : self._getdepartment,
        })
      def _getamount(self,data):
          
          date1 = data['form']['from_date'] 
          date2 = data['form']['to_date'] 
          department= data['form']['department']
          purchase_type = data['form']['type']

          self.cr.execute(""" SELECT sum(s.amount_total) as total, 
                                     count(s.name) as counter ,
                                     min(ir.purchase_type) as type 
                                     from purchase_order s 
                                     left join ireq_m ir on (s.ir_id=ir.id)
                                     where s.state <> ('cancel') and (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (s.department_id = %s) and ir.purchase_type=%s """,(date1,date2,department[0],purchase_type))
          
          res = self.cr.dictfetchall()
          
          return res

      def _getdepartment(self,data):
          department= data['form']['department']

          if department :
             self.cr.execute(""" SELECT d.name as dept_name from hr_department d where (d.id = %s)""",(department[0],))
             res = self.cr.dictfetchall()
             return res

      def _getdata(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           department= data['form']['department']
           purchase_type = data['form']['type']
           self.cr.execute("""
                select

                    min(pt.name) as product_name,
                    min(pt.notes) as note,
                    min(pt.product_qty) as qty ,
                    min(pt.price_unit) as price_unit,
                    min(s.name) as name,
                    min(s.date_approve) as date,
                    min(rp.name) as partner_name,
                    min(d.name) as dept,
                    min(ir.purchase_type) as type 
                    from purchase_order s 
                    left join ireq_m ir on (s.ir_id=ir.id)
                    left join purchase_order_line pt on (s.id=pt.order_id)
                    left join res_partner rp on (s.partner_id=rp.id)
                    left join hr_department d on (s.department_id=d.id)
                where s.state <> ('cancel') and 
                (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (s.department_id = %s) and ir.purchase_type=%s
                 group by 
                     pt.id
                 order by
                     name
                
               """,(date1,date2,department[0],purchase_type ))
           res = self.cr.dictfetchall()
           print "res :::::::::::::::::",res
           return res
report_sxw.report_sxw('report.purchase_status.report', 'purchase.order', 'addons/purchase_report/report/purchase_status.rml' ,parser=purchase_status_report,header=False)
