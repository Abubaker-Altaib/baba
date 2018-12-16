from osv import fields, osv
import time

class payroll_listing_department(osv.osv_memory):
    _name = "payroll.listing.department"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
       
	    'month': fields.selection(_get_months,'Month', required=True),
	    'year': fields.integer('year',required=True ),
		'department_ids' : fields.many2many('hr.department.payroll','salary_listing_rel', 'dep_listing_id', 'emp_listing_id','Departments', required=True), 
        'payroll_ids': fields.many2many('hr.salary.scale', 'hr_sal_pay_rel','listing_id','salary_id','Salary Scale',required=True),
        'type': fields.selection([('salary', 'Salary'), ('addendum', 'Addendum')], 'type'),
		'allowance_deduction': fields.many2one('hr.allowance.deduction', 'allowance/deduction'),
        }
    

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),

		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.payroll.main.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.listing.department',
            'datas': datas,
            }

payroll_listing_department()  		 
