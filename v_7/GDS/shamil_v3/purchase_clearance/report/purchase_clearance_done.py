#coding:utf-8
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw

# purchase_clearance_all report         ----------------------------------------------------------------------------------------------------------------
class clearance_report_done(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(clearance_report_done, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })

    def _getdata(self,data):
	   date1= data['form']['Date_from']
	   date2= data['form']['Date_to']
           data_clearance_type = data['form']['clearance_type']
           data_s = data['form']['Shipment']
           data_purpose = data['form']['purpose']
           data_project = data['form']['project_id']
           where_condition = ""
           where_condition += data_clearance_type and " and c.clearance_type='%s'"%data_clearance_type or ""
           where_condition += data_s and " and c.ship_method='%s'"%data_s or ""
           where_condition += data_purpose and (data_purpose == 'pro' and " and c.clearance_purpose='project' " or " and c.clearance_purpose='purchase' ") or ""
           where_condition += data_project and " and c.project_id=%s"%data_project or ""
           self.cr.execute("""
                	select 
				c.name as name ,
				o.name as project_name ,
				po.name as purchase_order ,
				c.delivery_date as deliver_date ,
				c.clearance_type as category ,
				c.bill_of_lading_date as ship_date , 
				c.im_date as im , 
				c.customs_certificate_no as custom ,
				c.date as date , 
				c.document_hand_date as document , 
				c.description as pro_name ,
				c.ministry_date as mini_date ,
				c.clearance_date as clear_date ,
				c.bills_amoun_total as amount ,
				c.bill_of_lading as bill ,
				c.ship_method as ship , 
				c.notes as note
			
                		from purchase_clearance c
					left join hr_department o on (c.project_id=o.id)
					left join purchase_order po on (c.purchase_order_ref = po.id)
				where c.state = 'done' 
				and (to_char(c.date,'YYYY-mm-dd')>=%s and to_char(c.date,'YYYY-mm-dd')<=%s)
       				 """+ where_condition +"order by c.name",(date1,date2)) 
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.clearance_report_done.report', 'purchase.clearance', 'purchase_clearance/report/purchase_clearance_done.rml' ,parser=clearance_report_done,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
