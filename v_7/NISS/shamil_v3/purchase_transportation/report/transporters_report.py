# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class transporters_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(transporters_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line3':self.get_amount,
        })

    def get_amount(self,data):
        if data['form']['state']:
            if data['form']['partner_name']:
                self.cr.execute("""SELECT sum(amount_total) AS amount From transportation_quotes tq
                left join transportation_order tr on (tr.id = tq.transportation_id)
                where tq.supplier_id= %s and 
                (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and (tq.state = 'done')
                and (tr.state = 'done')"""
                ,(data['form']['partner_name'][0],data['form']['Date_from'],data['form']['Date_to']))
            else :
                self.cr.execute("""SELECT sum(amount_total) AS amount From transportation_quotes tq
                left join transportation_order tr on (tr.id = tq.transportation_id)
                where
                (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and (tq.state = 'done')
                and (tr.state = 'done')"""
                ,(data['form']['Date_from'],data['form']['Date_to']))
        else:
            if data['form']['partner_name']:
                self.cr.execute("""SELECT sum(amount_total) AS amount From transportation_quotes tq
                left join transportation_order tr on (tr.id = tq.transportation_id)
                where tq.supplier_id= %s and 
                (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and (tq.state = 'done')"""
                ,(data['form']['partner_name'][0],data['form']['Date_from'],data['form']['Date_to']))
            else :
                self.cr.execute("""SELECT sum(amount_total) AS amount From transportation_quotes tq
                left join transportation_order tr on (tr.id = tq.transportation_id)
                where
                (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and (tq.state = 'done')"""
                ,(data['form']['Date_from'],data['form']['Date_to']))
        res = self.cr.dictfetchall()
        
        return res

    def _getdata(self,data):
        if data['form']['state']:
            if data['form']['partner_name']:
                self.cr.execute("""select tr.source_location source ,
                                       tr.destination_location dest,
                                       tq.amount_total total,
                                       pr.name partner,
                                       tr.transportation_date date,
                                 CASE tr.state WHEN 'done' THEN 'تم'
                                              WHEN 'pur_manager' THEN 'انتظار تاكيد قسم الترحيل'
                                              WHEN 'quotation' THEN 'انشاء الفواتير'
                                              WHEN 'cancel' THEN 'ملغي'
                                              WHEN 'draft' THEN 'طلب مبدئي'
                                              WHEN 'send' THEN 'تم ارسال المواد'
                                              WHEN 'receive' THEN 'تم استلام المواد'
                                              WHEN 'confirmed' THEN 'انتظار تصديق مدير الامداد'
                                              WHEN 'supply' THEN 'انتظار تصديق قسم المشتريات'
                                END "state" ,
                                       tr.name tran
                                from transportation_order tr 
                                   left join transportation_quotes tq on (tr.id = tq.transportation_id and tq.state='done')
                                   left join res_partner pr on (tq.supplier_id = pr.id)
                                where (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and tq.supplier_id= %s and tr.state = 'done' 
                                """,(data['form']['Date_from'],data['form']['Date_to'],data['form']['partner_name'][0])) 
            else:
                self.cr.execute("""select tr.source_location source ,
                                       tr.destination_location dest,
                                       tq.amount_total total,
                                       pr.name partner,
                                       tr.transportation_date date,
                                       tr.name tran,
                                    CASE tr.state WHEN 'done' THEN 'تم'
                                              WHEN 'pur_manager' THEN 'انتظار تاكيد قسم الترحيل'
                                              WHEN 'quotation' THEN 'انشاء الفواتير'
                                              WHEN 'cancel' THEN 'ملغي'
                                              WHEN 'draft' THEN 'طلب مبدئي'
                                              WHEN 'send' THEN 'تم ارسال المواد'
                                              WHEN 'receive' THEN 'تم استلام المواد'
                                              WHEN 'confirmed' THEN 'انتظار تصديق مدير الامداد'
                                              WHEN 'supply' THEN 'انتظار تصديق قسم المشتريات'
                                END "state"
                                from transportation_order tr 
                                   left join transportation_quotes tq on (tr.id = tq.transportation_id and tq.state='done')
                                   left join res_partner pr on (tq.supplier_id = pr.id)
                                where (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and tr.state = 'done'
                                """,(data['form']['Date_from'],data['form']['Date_to'])) 
        else :
            if data['form']['partner_name']:
                self.cr.execute("""select tr.source_location source ,
                                       tr.destination_location dest,
                                       tq.amount_total total,
                                       pr.name partner,
                                       tr.transportation_date date,
                                       tr.name tran,
                                    CASE tr.state WHEN 'done' THEN 'تم'
                                              WHEN 'pur_manager' THEN 'انتظار تاكيد قسم الترحيل'
                                              WHEN 'quotation' THEN 'انشاء الفواتير'
                                              WHEN 'cancel' THEN 'ملغي'
                                              WHEN 'draft' THEN 'طلب مبدئي'
                                              WHEN 'send' THEN 'تم ارسال المواد'
                                              WHEN 'receive' THEN 'تم استلام المواد'
                                              WHEN 'confirmed' THEN 'انتظار تصديق مدير الامداد'
                                              WHEN 'supply' THEN 'انتظار تصديق قسم المشتريات'
                                END "state"
                                from transportation_order tr 
                                   left join transportation_quotes tq on (tr.id = tq.transportation_id and tq.state='done')
                                   left join res_partner pr on (tq.supplier_id = pr.id)
                                where (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) and tq.supplier_id= %s 
                                """,(data['form']['Date_from'],data['form']['Date_to'],data['form']['partner_name'][0])) 
            else:
                self.cr.execute("""select tr.source_location source ,
                                       tr.destination_location dest,
                                       tq.amount_total total,
                                       pr.name partner,
                                       tr.transportation_date date,
                                       tr.name tran,
                                    CASE tr.state WHEN 'done' THEN 'تم'
                                              WHEN 'pur_manager' THEN 'انتظار تاكيد قسم الترحيل'
                                              WHEN 'quotation' THEN 'انشاء الفواتير'
                                              WHEN 'cancel' THEN 'ملغي'
                                              WHEN 'draft' THEN 'طلب مبدئي'
                                              WHEN 'send' THEN 'تم ارسال المواد'
                                              WHEN 'receive' THEN 'تم استلام المواد'
                                              WHEN 'confirmed' THEN 'انتظار تصديق مدير الامداد'
                                              WHEN 'supply' THEN 'انتظار تصديق قسم المشتريات'
                                END "state"
                                from transportation_order tr 
                                   left join transportation_quotes tq on (tr.id = tq.transportation_id and tq.state='done')
                                   left join res_partner pr on (tq.supplier_id = pr.id)
                                where (to_char(tr.transportation_date,'YYYY-mm-dd')>=%s and to_char(tr.transportation_date,'YYYY-mm-dd')<=%s) 
                                """,(data['form']['Date_from'],data['form']['Date_to'])) 
            
        res = self.cr.dictfetchall()
        print"res ",res
        return res
report_sxw.report_sxw('report.transporters_report', 'transportation.order', 'purchase_transportation/report/transporters_report.rml' ,parser=transporters_report )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
