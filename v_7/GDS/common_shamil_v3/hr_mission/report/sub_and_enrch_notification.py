
from report import report_sxw
from osv import orm
from tools.translate import _

class subsistence_notify(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(subsistence_notify, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        'total':self.total_mission,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in objects:
            if obj.state != "approved":
                raise orm.except_orm(_('Warning!'), _('You cannot print this report for not approved mission!'))
            if obj.mission_id.company_id or not obj.mission_id.currency:
                raise orm.except_orm(_('Warning!'), _('You can not print. This report available only for external missions !')) 
        return super(subsistence_notify, self).set_context(objects, data, ids, report_type=report_type)

    def total_mission(self,miss_id):
        self.cr.execute('''SELECT sum(l.mission_amounts) as total
                            FROM hr_employee_mission m, hr_employee_mission_line l
                            WHERE m.id = %s AND l.emp_mission_id = m.id '''%(miss_id))
        return self.cr.dictfetchall()

report_sxw.report_sxw('report.Subsistence_notifi', 'hr.employee.mission', 'hr_mission/report/sub_and_enrch_notification.rml' ,parser=subsistence_notify ,header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
