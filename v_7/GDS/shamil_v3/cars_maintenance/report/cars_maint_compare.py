#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import pooler
from osv import fields, osv
import time
from report import report_sxw
from openerp.tools.translate import _


class cars_maint_compare(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cars_maint_compare, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('car.maintenance.request').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'done':
		            raise osv.except_osv(_('Error!'), _('You can not print this report, This request not Done yet!')) 
	return super(cars_maint_compare, self).set_context(objects, data, ids, report_type=report_type)



    def _getdata(self,ref):

           self.cr.execute("""
                SELECT 
                                  p.name_template as fault_name ,
				  f.product_qty as qty ,
				  uom.name as product_uom

  
                FROM car_maintenance_request r

		left join car_faults f on (f.fault_id = r.id)
		left join product_product p on (f.product_id = p.id)
		left join product_uom uom on (f.product_uom = uom.id)



                 where r.id = %s and added_by_supplier='False'"""%(ref))


 
           res = self.cr.dictfetchall()
           return res 


report_sxw.report_sxw('report.cars_maint_compare', 'car.maintenance.request', 'addons/cars_maintenance/report/cars_maint_compare.rml' ,parser=cars_maint_compare , header=False)
