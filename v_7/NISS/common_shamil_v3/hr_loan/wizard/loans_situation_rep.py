
from openerp.osv import fields, osv
import time

class loans_situation_rep(osv.osv_memory):
    _name = "loans.situation.rep"

    _columns = {
 
	         'company_id': fields.many2one('res.company', 'Company Name',required=True ),
	         'loan_id': fields.many2one('hr.loan','Loan Name',required=True ),
		 'emp_id': fields.many2many('hr.employee','loan_employee_relation','employee_id','loan_id', 'Employee(s)'),

   		 }
   
  
    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.loan.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'loans.situation.rep',
            'datas': datas,
            }

loans_situation_rep()


