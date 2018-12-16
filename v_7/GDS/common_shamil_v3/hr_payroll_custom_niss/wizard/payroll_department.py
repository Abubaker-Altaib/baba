from osv import fields, osv
import time

class payroll_department(osv.osv_memory):
    _name = "payroll.department"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
        'month': fields.selection(_get_months,'Month', required=True),
	    'year': fields.integer('year',required=True ),
		'department_ids' : fields.many2many('hr.department.payroll','salary_list_rel', 'dep_id', 'emp_id','Departments', required=True), 


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
            'report_name': 'payroll_department',
            'datas': datas,
            }

payroll_department()  		 
