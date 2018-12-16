
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class attendance_approved_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(attendance_approved_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines':self.lines,
        })
    def lines(self,data):
        attendance_obj = self.pool.get('suggested.attendance')
        attendance_lines_obj = self.pool.get('suggested.attendance.line')
        lines = attendance_obj.read(self.cr, self.uid, [ self.context['active_id'] ],[], self.context)
        lines_ids = lines and 'lines_ids' in lines[0] and lines[0]['lines_ids'] or []
        start_date = lines and 'start_date' in lines[0] and lines[0]['start_date'] or 0
        attendace_lines = attendance_lines_obj.read(self.cr, self.uid, lines_ids,[], self.context)
        if attendace_lines:
            new_lines = []
            new_lines.append([u'ملاحظات',u'نسبة العمل',
            u'عدد الساعات المستحقة',u'الساعات المسترجعة حسب توجيهات مدراء الادارات',u'ساعات التدريب والماموريات',
            u'عدد ساعات التأخير',u'عدد ساعات نسيان البصمة',
            u'عدد ساعات الغياب',u' عدد الساعات في الشهر من'+str(start_date),
            u'الساعات أﻹضافية ايام العطلة',u'الساعات أﻹضافية ايام العمل',
            u'عدد أيام نسيان البصمة',u'عدد أيام الخروج المبكر',
            u'عدد أيام التأخير',u'عدد أيام اجازة',
            u'عدد أيام غياب',u'اﻹدارة',u'اﻹسم'])
            counter = 1
            for line in attendace_lines:
                new_line = []
                new_line.append('')
                new_line.append(line['added_percent'])
                new_line.append(line['earned'])
                new_line.append(line['added'])
                new_line.append(line['training'])
                new_line.append(line['late_hours'])
                new_line.append(line['forget_finger_print_hours'])
                new_line.append(line['abacense_hours'])
                new_line.append(line['period_work_hours'])
                new_line.append(line['extra_off_day'])
                new_line.append(line['extra_work_day'])
                new_line.append(line['forget_finger_print'])
                new_line.append(line['early_out'])
                new_line.append(line['late_days'])
                new_line.append(line['get_holidays'])
                new_line.append(line['abacense_days'])
                new_line.append(line['department'])
                new_line.append(line['name'])
                new_line.append(counter)
                new_lines.append(new_line)
                counter+=1
            attendace_lines = new_lines
        return attendace_lines
        


report_sxw.report_sxw('report.attendance_approved_report.report','suggested.attendance','addons/attendance_ntc/report/attendance_approved_report.mako',parser=attendance_approved_report,header=False)
