# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import re
import pooler
import wizard
from osv import fields, osv
import time
from report import report_sxw
from tools.translate import _

class building_ins_notification(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_ins_notification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line':self._getitem,
            'line2':self._getbuilding,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('building.insurance').browse(self.cr, self.uid, ids, self.context):
            if not obj.insurance_lines:
		            raise osv.except_osv(_('Error!'), _('You can not print this notification, Please Insert Building Items First!')) 
        return super(building_ins_notification, self).set_context(objects, data, ids, report_type=report_type) 


    def _getbuilding(self,num):
       
	   self.cr.execute("""
           SELECT Distinct b.building_id as id ,
                           m.name as building_name 

           FROM building_insurance i 
           left join building_insurance_line b on (i.id = b.insurance_id)
	       left join building_manager m on (m.id = b.building_id)

		   where i.id = %s 
           ORDER BY b.building_id """%(num))

           res = self.cr.dictfetchall()
           return res

    def _getitem(self,num,num2):
       
	   self.cr.execute("""
           SELECT i.price as price ,
                  i.name as note ,
                  t.name as item_name  
            


           FROM building_insurance_line i
		   left join building_item t on (t.id = i.item_id)
		   where i.insurance_id = %s and i.building_id = %s
           ORDER BY i.building_id"""%(num,num2))

           res = self.cr.dictfetchall()
           return res





        
report_sxw.report_sxw('report.building_ins_notification','building.insurance','addons/building_management/report/building_ins_notification.rml',parser=building_ins_notification, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
