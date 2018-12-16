from osv import fields, osv
import time

class depend_on_job(osv.osv_memory):
    _name = "trainee.depend.on.job"

    _columns = {
         
        'From': fields.date('Start Date', required=True),
        'to': fields.date('End Date', required=True),
	    'job_id' : fields.many2one('hr.job', 'Job', required=True),
   		 }

    def positive_percentage(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
          if p.From > p.to :
               return False
        return True

    _constraints = [
        (positive_percentage, 'The field From Date must be before the To Date!', ['From Date']),
    ]
    
    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'training.approved.by.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'test_free2',
            'datas': datas,
            }
depend_on_job()
