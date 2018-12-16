
import mx
from report import report_sxw
from osv import osv
from tools.translate import _

class car_renting_notifi(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(car_renting_notifi, self).__init__(cr, uid, name, context)
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('hr.employee.mission').browse(self.cr, self.uid, ids, self.context):
            if not obj.mission_id.company_id and obj.transport != '5' :
                raise osv.except_osv(_('Error!'), _('You can not print. This report available only for internal missions  or missions that need to rent a car !'))
        return super(car_renting_notifi, self).set_context(objects, data, ids, report_type=report_type)

report_sxw.report_sxw('report.car_renting_notifi', 'hr.employee.mission', 'hr_mission/report/car_renting_notification.rml' , parser=car_renting_notifi , header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
