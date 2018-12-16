# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import re
import pooler
from report import report_sxw
#import wizard
from openerp.osv import fields, osv
from openerp.tools.translate import _

class foreigners_procedures(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(foreigners_procedures, self).__init__(cr, uid, name, context)
        self.localcontext.update({
#           'foreigners':self.foreigners,              
        })
        self.context = context

    """def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('foreigners.procedures.request').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'done':
		            raise osv.except_osv(_('Error!'), _('You can not print this notification, the procedure request not approved yet!')) 

        return super(foreigners_procedures, self).set_context(objects, data, ids, report_type=report_type) 

    def foreigners(self,request_id): 
        self.cr.execute(''' 
SELECT 
   foreigner_name as name , passport_number as passport_no
FROM 
  public_relation_foreigners
WHERE 
    id in(select foreigner_id from foreigners_request_rel where request_id= %s)
''',(request_id,))
       
        res=self.cr.dictfetchall()
        counter=0
        res_data={}
        top_result=[]
        while counter < len(res):
           res_data = { 'no': counter+1,
                        'name':res[counter]['name'],
                        'passport_no': res[counter]['passport_no'],

                       }
           top_result.append(res_data)
           counter+=1
        return top_result"""
                
        
 
report_sxw.report_sxw('report.foreigners.procedures', 'foreigners.procedures.request', 'addons/public_relation/report/foreigners_procedures.rml' ,parser=foreigners_procedures ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
