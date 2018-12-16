from osv import fields, osv
import time

class payroll_listing_department_months(osv.osv_memory):
    _name = "payroll.listing.department.months"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
       
	    'first_month': fields.selection(_get_months,'First Month', required=True),
            'second_month': fields.selection(_get_months,'Second Month', required=True),
	    'year': fields.integer('year',required=True ),
		'department_ids' : fields.many2many('hr.department.payroll','salary_listing_months_rel', 'dep_listing_id', 'emp_listing_id','Departments', required=True), 
        'payroll_ids': fields.many2many('hr.salary.scale', 'hr_sal_pay_months_rel','listing_id','salary_id','Salary Scale',required=True),
		}
    

    _defaults = {
        'year': int(time.strftime('%Y')),
        'first_month': int(time.strftime('%m')),
        'second_month': int(time.strftime('%m')),

		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        #raise osv.except_osv(('Error'),('The before %s ')% (str(context.get('active_ids', []))))
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.payroll.main.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.department.listing.months',
            'datas': datas,
            }

payroll_listing_department_months()  		 
