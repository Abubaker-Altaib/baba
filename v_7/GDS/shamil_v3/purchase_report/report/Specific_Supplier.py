# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Specific Supplier report         ----------------------------------------------------------------------------------------------------------------
class Specific_Supplier_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Specific_Supplier_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self.get_partner,
            'line2':self.get_order_number,
            'line3':self.get_amount,
        })

    def get_partner(self,data):
        self.cr.execute('SELECT name AS partner_name From res_partner where id=%s'%(data['form']['partner_name'][0]))
        res = self.cr.dictfetchall()
        return res

    def get_amount(self,data):
        self.cr.execute("""SELECT sum(amount_total) AS amount From purchase_order where partner_id= %s and 
        (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s)"""
        ,(data['form']['partner_name'][0],data['form']['Date_from'],data['form']['Date_to']))
        res = self.cr.dictfetchall()
        return res
    def get_order_number(self,data):
        self.cr.execute("""SELECT count(name) AS order_n From purchase_order where partner_id= %s and 
        (to_char(date_order,'YYYY-mm-dd')>=%s and to_char(date_order,'YYYY-mm-dd')<=%s)"""
        ,(data['form']['partner_name'][0],data['form']['Date_from'],data['form']['Date_to']))
        res = self.cr.dictfetchall()
        return res
    def _getdata(self,data):
        #print "------------------------------------------------>",data['form']['partner_name'][0]
        self.cr.execute("""
                 select
                    
                    r.name as partner_name,
                    c.name as order_id,
                    c.date_order as date_order,

                    c.amount_total as total,
                    d.name as dept

                    from purchase_order c
                    
                    left join hr_department d on (c.department_id=d.id)
                    left join res_partner r on (c.partner_id=r.id)
                    left join product_category i on (i.id=c.ir_id)
                where (to_char(c.date_order,'YYYY-mm-dd')>=%s and to_char(c.date_order,'YYYY-mm-dd')<=%s) and c.partner_id= %s
        """,(data['form']['Date_from'],data['form']['Date_to'],data['form']['partner_name'][0])) 
        res = self.cr.dictfetchall()
        return res
report_sxw.report_sxw('report.Specific_Supplier.report', 'purchase.order', 'addons/purchase_report/report/Specific_Supplier.rml' ,parser=Specific_Supplier_report,header=False)
