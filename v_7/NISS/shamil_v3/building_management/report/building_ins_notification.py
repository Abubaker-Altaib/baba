# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields,orm
import pooler
from report import report_sxw
from tools.translate import _

class building_ins_notification(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(building_ins_notification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'line':self._getitem,
            'line2':self._getbuilding,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for record in self.pool.get('building.insurance').browse(self.cr, self.uid, ids, self.context):
            if not record.insurance_lines:
		            raise orm.except_orm(_('Error!'), _('You can not print this notification, Please Insert Building Items First!')) 
        return super(building_ins_notification, self).set_context(objects, data, ids, report_type=report_type) 


    def _getbuilding(self,ins_id):
       
	   self.cr.execute("""
           SELECT Distinct b.building_id as id ,
                           m.name as building_name 

           FROM building_insurance i 
           left join building_insurance_line b on (i.id = b.insurance_id)
	       left join building_building m on (m.id = b.building_id)

		   where i.id = %s 
           ORDER BY b.building_id """%(ins_id))

           res = self.cr.dictfetchall()
           return res

    def _getitem(self,ins_id,building_id):
       
	   self.cr.execute("""
           SELECT i.price as price ,
                  i.name as note ,
                  t.name as item_name ,  
                  i.qty as quantity
            


           FROM building_insurance_line i
		   left join item_item t on (t.id = i.item_id)
		   where i.insurance_id = %s and i.building_id = %s
           ORDER BY i.building_id"""%(ins_id,building_id))

           res = self.cr.dictfetchall()
           return res





        
report_sxw.report_sxw('report.building_ins_notification','building.insurance','addons/building_management/report/building_ins_notification.rml',parser=building_ins_notification, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
