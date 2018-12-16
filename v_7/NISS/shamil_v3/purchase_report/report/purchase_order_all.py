# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import datetime
#------------ purchase Order All ------------------ -------------------
class Purchase_Order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Purchase_Order_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self.get_order_number,
            'line3':self.get_amount,
            'line4':self.get_report_name,
        })
    def get_amount(self,data):
        date1 = data['form']['Date_from']
        date2 = data['form']['Date_to']
        purchase_type = data['form']['type']


        self.cr.execute("""SELECT sum(s.amount_total) AS amount , 
                                  min(ir.purchase_type) as type  
                                  From purchase_order s 
                                       left join ireq_m ir on (s.ir_id=ir.id) where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (s.state NOT IN ('cancel')) and ir.purchase_type=%s   """,(date1,date2,purchase_type))

        res = self.cr.dictfetchall()

        return res
    def get_report_name(self,data):

           date1 = data['form']['Date_from']
           date2 = data['form']['Date_to']
           d1 = datetime.strptime(date1,"%Y-%m-%d")
           d2 = datetime.strptime(date2,"%Y-%m-%d")      
	   dif = d2 - d1
	   no_days = dif.days
           if no_days > 0 :
              if no_days in [89,90,91,92] :
                 
                 res = {'name' : 'Quarterly' } 
              elif no_days in [180,181,182,183,184] :

                  res = {'name' : 'Biannual' }

              elif no_days in [364,365,366] :
                  res = {'name' : 'Yearly' }

              else :

                  res = {'name' : 'Nothing' }


           return res


    def get_order_number(self,data):
        date1 = data['form']['Date_from']
        date2 = data['form']['Date_to']
        purchase_type = data['form']['type']
        self.cr.execute("""SELECT count(s.name) AS order_n ,
                                  min(ir.purchase_type) as type  
                                  From purchase_order s 
                                       left join ireq_m ir on (s.ir_id=ir.id) where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (s.state NOT IN ('cancel')) and ir.purchase_type=%s""",(date1,date2,purchase_type))

        res = self.cr.dictfetchall()
        

        return res

    def _getdata(self,data):
           
           date1 = data['form']['Date_from']
           date2 = data['form']['Date_to']
           purchase_type = data['form']['type']

           
              
           self.cr.execute( """
           select
                    min(d.name) as department,
                    min(s.name) as name,
                    min(s.state) as state,
                    min(p_cat.name) as catg,
            CASE min(s.state) WHEN 'done' THEN 'تم'
                     WHEN 'approved' THEN 'تم تصديقه '
            END "state2" ,
                    min(s.date_order) as order_date,
                    min(rp.name) as partner_name,
                    
                    s.amount_total as price_total ,
                    min(ir.purchase_type) as type  
                    From purchase_order s 
                    left join ireq_m ir on (s.ir_id=ir.id) 
                    left join res_partner rp on (s.partner_id=rp.id)
                    left join purchase_order_line l on (s.id=l.order_id)
                    left join hr_department d on (s.department_id=d.id)
                    left join product_category p_cat on (s.cat_id=p_cat.id)
                where (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s) and (s.state NOT IN ('cancel')) and ir.purchase_type=%s
                group by
                    s.id , s.amount_total 
                order by
                    name
        """,(date1,date2,purchase_type)) 
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.Purchase_Order.report', 'purchase.order', 'addons/purchase_report/report/Purchase_Order_All.rml' ,parser=Purchase_Order_report ,header=False)
