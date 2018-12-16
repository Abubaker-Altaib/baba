import time
from report import report_sxw
from osv import osv
import pooler


class dependence_letter_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(dependence_letter_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
         
         
         'function' : self.get_data,
         
         })
    
    
    
    def get_data(self,data):
           
           request_clearance_ids = data['form']['request_clearance_ids']
           

           if len(request_clearance_ids) == 1:
                condition = " and cl.id in (%s)"%request_clearance_ids[0]

                if data['form']['document_type'] == 'bill_of_lading':
                   bill_lading_num = { 'count' : 'one_bill_of_lading' }
                elif data['form']['document_type'] == 'invoice':
                   bill_lading_num = { 'count' : 'one_invoice' }
                elif data['form']['document_type'] == 'certf_customs':
                   bill_lading_num = { 'count' : 'one_certf_customs' }
                else :
                   bill_lading_num = { 'count' : 'one_abdication_certificate' }


           else: 
                request_clearance_ids = tuple(request_clearance_ids)
                condition = " and cl.id in %s"%str(request_clearance_ids) 

                if data['form']['document_type'] == 'bill_of_lading':
                   bill_lading_num = { 'count' : 'multi_bill_of_lading' }
                elif data['form']['document_type'] == 'invoice':
                   bill_lading_num = { 'count' : 'multi_invoice' }
                elif data['form']['document_type'] == 'certf_customs':
                   bill_lading_num = { 'count' : 'multi_certf_customs' }
                else :
                   bill_lading_num = { 'count' : 'multi_abdication_certificate' }

           self.cr.execute( """
                                    select                        
                                                    distinct cl.bill_of_lading as bill_of_lading  ,
                                                    cl.bill_of_lading_date as date ,
                                                    cl.message_content as message_content
                                                    From purchase_clearance cl
                                                    

                                                    
                                                where cl.state not in ('cancel','done') """ + condition  + """order by cl.bill_of_lading_date""")
             
           res={}
           res['result'] = self.cr.dictfetchall()
           res['count'] =bill_lading_num.get('count')

           return res

report_sxw.report_sxw('report.dependence_letter_report', 'purchase.clearance', 'purchase_clearance_niss/report/dependence_letter_report.rml', parser=dependence_letter_report,header=False)
