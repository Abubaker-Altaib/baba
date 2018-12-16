from osv import fields, osv
from openerp import netsvc

class wizard_create_employee(osv.osv_memory):
    
    _name = "wizard.create.employee"
    
    _columns = {
        'create_type':fields.selection([('new','New Employee record'),('same','Same Employee record')],'Creation type',required=True),
        }

    def create_employee(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        active_id = context.get('active_id',False)
        #employee = employee_obj.browse(cr, uid, active_id, context=context):
        default = {'employee_type':'employee','state':'draft'}
        if self.browse(cr,uid,ids[0],context=context).create_type == 'new':
            employee_obj.copy(cr, uid, active_id, default, context=context)
        else:
            employee_obj.write(cr, uid, [active_id],default, context=context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_delete(uid, 'hr.employee', active_id, cr)
            wf_service.trg_create(uid, 'hr.employee', active_id, cr)
