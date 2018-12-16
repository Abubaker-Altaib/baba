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
class clearance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(clearance_report, self).__init__(cr, uid, name, context)
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
				p.name as purchase_order ,
				c.delivery_date as deliver_date ,
				c.clearance_type as category ,
				c.document_hand_date as document , 
				c.ministry_date as mini_date ,
				c.clearance_date as clear_date ,
				c.bills_amoun_total as amount ,
				c.bill_of_lading as bill ,
				c.ship_method as ship , 
				c.state,
				 CASE c.state 
                    			 WHEN 'draft' THEN 'مبدئي '
                    			 WHEN 'confirmed'  THEN 'فى انتظار تصديق مدير الموارد البشرية والمالية والامداد'
                    			 WHEN 'gm'  THEN 'فى انتظار مدير ادارة الامداد'
                    			 WHEN 'supply'  THEN 'فى انتظار مدير قسم التخليص'
                    			 WHEN 'clear_dept'  THEN 'فى انتظار ضابط التخليص'
                    			 WHEN 'clear_officer'  THEN 'فى محطة التخليص'
                    			 WHEN 'clear_stage'  THEN 'فى انتظار التسعير'
                    			 WHEN 'accounting_price'  THEN 'فى انتظار الارسال الى قسم الحسابات'
                    			 WHEN 'cancel' THEN 'ملغي'
           		        END "state2" ,
				c.notes as note
			
                		from purchase_clearance c
					left join hr_department o on (c.project_id=o.id)
					left join purchase_order p on (c.purchase_order_ref = p.id)
				where c.state NOT IN ('done') 
				and (to_char(c.date,'YYYY-mm-dd')>=%s and to_char(c.date,'YYYY-mm-dd')<=%s)
       				 """+ where_condition +"order by c.name",(date1,date2)) 
  
           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.clearance_report.report', 'purchase.clearance', 'purchase_clearance/report/purchase_clearance_All.rml' ,parser=clearance_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
