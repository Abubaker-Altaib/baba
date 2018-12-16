import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class service_state_takeout(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(service_state_takeout, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'job_groups_len': self._get_job_groups_len,
            'job_groups': self._get_job_groups,
            'job_groups_len_by_one': self._get_job_groups_len_by_one,
            'job_groups_data_by_one': self._get_job_groups_data_by_one,
        })

    def _get_job_groups_len(self, data):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        degree_id = int(data['form']['degree_id'][0])
        jobs_ids = data['form']['jobs_ids']
        move_deg_obj = self.pool.get('hr.movements.degree')

        move_deg_ids = move_deg_obj.search(self.cr, self.uid, [(
            'reference', '=', degree_id), ('approve_date', '>=', start_date), ('approve_date', '<=', end_date), ])
        
        move_deg = move_deg_obj.browse(self.cr, self.uid, move_deg_ids)
        
        if jobs_ids:
            move_deg = filter(lambda x:x.employee_id.parent_job_id.id in jobs_ids, move_deg)

        self.all_data = move_deg
        return len(move_deg)

    def _get_job_groups(self):
        return set([x.employee_id.parent_job_id for x in self.all_data])
    
    def _get_job_groups_len_by_one(self, group_id):
        data = filter(lambda x:x.employee_id.parent_job_id.id == group_id, self.all_data)
        return len(data)
    
    def _get_job_groups_data_by_one(self, group_id):
        data = filter(lambda x:x.employee_id.parent_job_id.id == group_id, self.all_data)
        return data

report_sxw.report_sxw('report.service_state_takeout.report', 'hr.employee',
                      'addons/hr_custom_military/report/service_state_takeout_report.rml', parser=service_state_takeout, header='internal landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
