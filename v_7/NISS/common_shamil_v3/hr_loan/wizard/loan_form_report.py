# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from openerp.osv import osv, fields, orm
import datetime

class loans_emp_report(osv.osv_memory):
    _name="loans.emps.report"
    _columns={
        'company_id':fields.many2one( 'res.company', 'Company' ,required=True),
        'department_id':fields.many2one('hr.department', 'Department',domain="[('company_id','=',company_id)]",required=True),
        'employee_ids':fields.many2many( 'hr.employee','emp_loan_rel', 'company_id','emp_id','Employees ', required=True),
        'start_date':fields.date('Start Date' , required=True),
        'loans':fields.many2one('hr.loan','Loan', required=True ),
             }
    _defaults = {
       
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'loans.emps.report', context=c), 
        'employee_ids': False,
	
    }

    def onchange_employee(self, cr, uid, ids, department_id,context={}):
		#employee_type domain
		emp_obj = self.pool.get('hr.employee')
		company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
		contractors = company_obj.loan_contractors
		employee = company_obj.loan_employee
		recruit = company_obj.loan_recruit
		trainee = company_obj.loan_trainee
		employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
                employee_domain['employee_id']+=[('state', '=', 'approved'),('department_id','=',department_id)]
		domain = {'employee_ids':employee_domain['employee_id']}
		return {'domain': domain}

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.loan',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'loan.form.report',
            'datas': datas,
            }

loans_emp_report()

