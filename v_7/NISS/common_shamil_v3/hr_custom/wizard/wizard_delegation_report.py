
from osv import fields, osv
import time

class wizard_delegation(osv.osv_memory):
    _name = "delegation.report"

    _columns = {

	    'category_id': fields.many2many('hr.delegation.category','cat_dep_rel','category_dept','categorys_id', 'Category name',required=True ),

   		 }
   

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr2.basic.emp.delegation',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'delegation.report',
            'datas': datas,
            }

wizard_delegation()
   

