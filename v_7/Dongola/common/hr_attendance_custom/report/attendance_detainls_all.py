# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from itertools import groupby
from operator import itemgetter
import math


class attendance_details_all(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        self.off_week_days = [4, 5]  # friday and saturday
        self.holiday_dates = {}
        self.unpaind_holiday_dates = {}
        super(attendance_details_all, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines': self.lines,
        })

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def values(self, emp_id, start_date, end_date):
        work_hours = 0

        # to count hours for one day
        if not end_date:
            end_date = start_date

        start_date = self.get_date(start_date)
        end_date = self.get_date(end_date)

        if not emp_id:
            while start_date <= end_date:
                for key in self.cache.keys():
                    if key[1] == str(start_date.weekday()):
                        for record in self.cache[key]:
                            if self.get_date(record['attendance'].date_from) <= start_date:
                                work_hours += record['basic'].working_hours

                start_date += relativedelta(days=1)

        if emp_id:
            while start_date <= end_date:
                flag2 = False
                if emp_id in self.unpaind_holiday_dates.keys():
                    flag2 = start_date.date() in self.unpaind_holiday_dates[
                        emp_id]
                if str(start_date.date()) in self.work_days and not flag2:
                    if (emp_id, str(start_date.weekday())) in self.cache.keys():
                        for record in self.cache[(emp_id, str(start_date.weekday()))]:
                            if self.get_date(record['attendance'].date_from) <= start_date:
                                work_hours += record['basic'].working_hours

                start_date += relativedelta(days=1)

        return work_hours

    def get_caches(self, emp_id, start_date, end_date):
        List = []
        start_date = self.get_date(start_date)
        end_date = self.get_date(end_date)

        while start_date <= end_date:
            if str(start_date.date()) in self.work_days:
                if (emp_id, str(start_date.weekday())) in self.cache.keys():
                    for record in self.cache[(emp_id, str(start_date.weekday()))]:
                        if self.get_date(record['attendance'].date_from) <= start_date:
                            List.append(record)
            start_date += relativedelta(days=1)
        return List

    def get_training(self, start_date, end_date):
        ##############################
        # get events of all employees
        ###########################################
        count = 0
        self.training = {}
        hr_training_approved = self.pool.get('hr.employee.training.approved')

        hr_training_approved_ids_first = hr_training_approved.search(self.cr, self.uid,
                                                                     [('state', '=',
                                                                       'approved')],
                                                                     context=self.context)

        hr_training_approved_ids_second = hr_training_approved.search(self.cr, self.uid,
                                                                      [('state', '=',
                                                                        'approved')],
                                                                      context=self.context)

        List_ids = list(set(hr_training_approved_ids_first) |
                        set(hr_training_approved_ids_second))

        basic = hr_training_approved.browse(
            self.cr, self.uid, List_ids, context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        for training in basic:
            event_start = datetime.strptime(training.start_date, "%Y-%m-%d")
            event_end = datetime.strptime(training.end_date, "%Y-%m-%d")
            while event_start >= start_date and event_start <= end_date and event_start <= event_end:
                count += 1
                event_start += relativedelta(days=1)
            for emp in training.line_ids:
                self.training[emp.employee_id.id] = self.training.get(
                    emp.employee_id.id, 0)
                hours = (training.end_time - training.start_time) * emp.days
                self.training[emp.employee_id.id] += int(hours)

    def get_missions(self, start_date, end_date):
        ##############################
        # get events of all employees
        ###########################################
        count = 0
        #self.training = {}
        employee_mission = self.pool.get('hr.employee.mission')

        employee_mission_ids_first = employee_mission.search(self.cr, self.uid,
                                                             [('state', '=',
                                                               'approved')],
                                                             context=self.context)

        employee_mission_ids_second = employee_mission.search(self.cr, self.uid,
                                                              [('state', '=',
                                                                'approved')],
                                                              context=self.context)

        List_ids = list(set(employee_mission_ids_first) |
                        set(employee_mission_ids_second))

        basic = employee_mission.browse(
            self.cr, self.uid, List_ids, context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        for training in basic:
            event_start = datetime.strptime(training.start_date, "%Y-%m-%d")
            event_end = datetime.strptime(training.end_date, "%Y-%m-%d")
            while event_start <= event_end:
                if event_start >= start_date and event_start <= end_date:
                    count += 1
                event_start += relativedelta(days=1)
            for emp in training.mission_line:
                self.training[emp.employee_id.id] = self.training.get(
                    emp.employee_id.id, 0)
                hours = emp.days * 8
                self.training[emp.employee_id.id] += int(hours)

    def get_working_hours(self):
        ##############################
        # get the working hours for all selected employees
        ###########################################

        self.cache = {}
        resource_calendar = self.pool.get('resource.calendar')

        resource_calendar_ids = resource_calendar.search(self.cr, self.uid, [],
                                                         context=self.context)

        for basic in resource_calendar.browse(self.cr, self.uid, resource_calendar_ids, context=self.context):
            for i in basic.employees_ids:
                for attendance in basic.attendance_ids:
                    self.cache[i.id, str(attendance.dayofweek)] = self.cache.get(
                        (i.id, attendance.dayofweek), [])
                    self.cache[i.id, str(attendance.dayofweek)] .append(
                        {'basic': basic, 'attendance': attendance})

    def get_off_days(self, start_date, end_date):
        ##############################
        # get the off_days in selected range
        ###########################################

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.off_days = []
        self.work_days = []
        while start_date <= end_date:
            if start_date.weekday() in self.off_week_days:
                self.off_days.append(start_date.strftime(
                    tools.DEFAULT_SERVER_DATE_FORMAT))
            else:
                self.work_days.append(start_date.strftime(
                    tools.DEFAULT_SERVER_DATE_FORMAT))
            start_date += relativedelta(days=1)

    def get_attendance(self, start_date, end_date):
        ##############################
        # get the attendance of all selected employees
        ###########################################
        hr_employee = self.pool.get('hr.employee')
        names = hr_employee.read(self.cr, self.uid, self.employees_ids, [
                                 'name_related'], context=self.context)
        self.names = {x['id']: x['name_related'] for x in names}
        hr_attendance = self.pool.get('hr.attendance')
        start_date = start_date + " 00:00:00"
        end_date = end_date + " 23:59:59"
        hr_attendance_ids = hr_attendance.search(self.cr, self.uid,
                                                 [('emp_id', 'in', self.employees_ids), ('name',
                                                                                         '>=', start_date), ('name', '<=', end_date)],
                                                 context=self.context)

        basic = hr_attendance.browse(
            self.cr, self.uid, hr_attendance_ids, context=self.context)

        groups_time = groupby(basic, key=lambda x: (
            x.emp_id.id, datetime.strptime(x.name, "%Y-%m-%d %H:%M:%S").date()))

        self.employees_attendance_time = {}

        groups_time_dict = {}
        for k, itr in groups_time:
            itr = [x for x in itr]
            groups_time_dict[k] = groups_time_dict.get(k, [])
            groups_time_dict[k] += itr
        for k in groups_time_dict:
            sign_in = sign_out = 0
            #itr = [x for x in itr]
            itr = groups_time_dict[k]
            date_time = str(k[1]) + " 00:00:00"
            date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

            sign_in_filter = filter(lambda x: x.action == 'sign_in', itr)
            if sign_in_filter:
                sign_in = min(sign_in_filter, key=lambda x: datetime.strptime(
                    x.name, "%Y-%m-%d %H:%M:%S"))

            sign_out_filter = filter(lambda x: x.action == 'sign_out', itr)
            if sign_out_filter:
                sign_out = max(sign_out_filter, key=lambda x: datetime.strptime(
                    x.name, "%Y-%m-%d %H:%M:%S"))

            work = 0.0
            over_time = 0.0
            late_in = 0.0
            early_out = 0.0
            early_in = 0.0
            short = 0.0

            if sign_in and sign_out:
                work = datetime.strptime(
                    sign_out.name, "%Y-%m-%d %H:%M:%S") - datetime.strptime(sign_in.name, "%Y-%m-%d %H:%M:%S")

                sign_in_time = datetime.strptime(
                    sign_in.name, "%Y-%m-%d %H:%M:%S")
                sign_out_time = datetime.strptime(
                    sign_out.name, "%Y-%m-%d %H:%M:%S")

                hours = work.seconds / 3600.0
                work = hours
                work_hours = 0
                calendar = self.cache[k[0], str(date_time.weekday())]
                calendar = filter(lambda x: self.get_date(
                    x['attendance'].date_from) <= date_time, calendar)
                calendar = calendar and [
                    max(calendar, key=lambda x: self.get_date(x['attendance'].date_from))] or []
                for ca in calendar:
                    work_hours += ca['basic'].working_hours

                if calendar:

                    last_hour = max(calendar, key=lambda x: x[
                                    'attendance'].hour_to)
                    hour_to = int(last_hour['attendance'].hour_to)
                    min_to = last_hour['attendance'].hour_to - hour_to
                    hour_to *= 60.0
                    min_to = 100 * int(min_to) / 60
                    min_to += hour_to


                    over_out = (sign_out_time.hour * 60.0) + sign_out_time.minute - min_to
                    
                    over_out /= 60.0
                    first_hour = min(calendar, key=lambda x: x[
                        'attendance'].hour_from)

                    hour_from = int(first_hour['attendance'].hour_from)
                    min_from = first_hour['attendance'].hour_from - hour_from
                    hour_from *= 60.0
                    min_from = 100 * int(min_from) / 60
                    min_from += hour_from

                    over_in = (sign_in_time.hour * 60.0) + sign_in_time.minute - min_from

                    
                    if over_out > 0:
                        over_time = over_out

                    if over_out < 0:
                        early_out = math.fabs(over_out)
                    
                    if over_in > 30:
                        over_in /= 60.0
                        late_in = over_in
                    
                    if over_in < 0:
                        early_in = math.fabs(over_in)

                    short = work_hours - work
                    if short < 0:
                        short = 0

            if sign_in != 0:
                # to get time fragment
                sign_in = str(sign_in.name).split(' ')[1]

            if sign_out != 0:
                # to get time fragment
                sign_out = str(sign_out.name).split(' ')[1]

            self.employees_attendance_time[k] = {
                'name': self.names[k[0]],
                'date': k[1],
                'sign_in': sign_in or "-",
                'sign_out': sign_out or "-",
                'work': round(work, 2) or "-",
                'over_time': round(over_time, 2) or "-",
                'late_in': round(late_in, 2) or "-",
                'early_out': round(early_out, 2) or "-",
                'early_in': round(early_in, 2) or "-",
                'short': round(short, 2) or "-",
            }

    def abacense_days(self, emp_id, start_date, end_date):
        count = 0
        count_h = 0
        for day in self.work_days:
            flag = False
            flag2 = False
            if emp_id in self.holiday_dates.keys():
                flag = self.get_date(day).date() in self.holiday_dates[emp_id]

            if emp_id in self.unpaind_holiday_dates.keys():
                flag2 = self.get_date(
                    day).date() in self.unpaind_holiday_dates[emp_id]

            if (emp_id, day, 'sign_in') not in self.employees_attendance and (emp_id, day, 'sign_out') not in self.employees_attendance and not flag and not flag2:
                count += 1
                count_h += self.values(emp_id, day, False)

        return int(count), int(count_h)

    def late_days(self, emp_id):
        count = 0
        count_h = 0.0

        for day in self.work_days:
            if (emp_id, day, 'sign_in') in self.employees_attendance and\
               (emp_id, day, 'sign_out')in self.employees_attendance:
                sign_in = min(filter(lambda x: x[0] == emp_id and x[2] == 'sign_in' and x[
                              3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                sign_out = max(filter(lambda x: x[0] == emp_id and x[2] == 'sign_out' and x[
                               3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                hours = (sign_out[1] - sign_in[1]).seconds / 3600.0
                work_hours = 0
                calendar = self.cache[emp_id, str(sign_out[1].weekday())]
                calendar = filter(lambda x: self.get_date(
                    x['attendance'].date_from) <= sign_out[1], calendar)
                for ca in calendar:
                    work_hours += ca['basic'].working_hours

                # change it to float
                work_hours *= 1.0

                if hours < work_hours:
                    count += 1
                    count_h += (work_hours - hours)

        return int(count), round(count_h, 2)

    def early_out(self, emp_id):
        count = 0
        for day in self.work_days:
            if (emp_id, day, 'sign_in') in self.employees_attendance and\
               (emp_id, day, 'sign_out')in self.employees_attendance:
                sign_out = max(filter(lambda x: x[0] == emp_id and x[2] == 'sign_out' and x[
                               3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                if sign_out:
                    calendar = self.cache[emp_id, str(sign_out[1].weekday())]
                    calendar = filter(lambda x: self.get_date(
                        x['attendance'].date_from) <= sign_out[1], calendar)
                    if calendar:
                        last_hour = max(calendar, key=lambda x: x[
                                        'attendance'].hour_to)
                        if float(str(sign_out[1].hour) + '.' + str(sign_out[1].minute)) < last_hour['attendance'].hour_to:
                            count += 1

        return int(count)

    def forget_finger_print(self, emp_id):
        count = 0
        count_h = 0
        for day in self.work_days:
            if (emp_id, day, 'sign_in') in self.employees_attendance or\
               (emp_id, day, 'sign_out')in self.employees_attendance:
                sign_in_sign_out = filter(lambda x: x[0] == emp_id and x[1] == day and (
                    x[2] == 'sign_in' or x[2] == 'sign_out'), self.employees_attendance.keys())
                if len(sign_in_sign_out) == 1:
                    count += 1
        return int(count)

    def forget_finger_print_hours(self, emp_id, forget_finger_print, start_date, end_date):
        count = 0
        basics = [x['basic']
                  for x in self.get_caches(emp_id, start_date, end_date)]
        basics = list(set(basics))
        for cache in basics:
            factor = cache.factor
            min_hours = cache.min_hours
            max_hours = cache.max_hours
            if forget_finger_print <= factor:
                count += forget_finger_print * min_hours
            else:
                first = forget_finger_print - factor
                first *= max_hours
                second = factor * min_hours
                count += first + second

        return int(count)

    def extra_work_day(self, emp_id):
        count = 0
        for day in self.work_days:
            if (emp_id, day, 'sign_in') in self.employees_attendance and\
               (emp_id, day, 'sign_out')in self.employees_attendance:
                sign_in = min(filter(lambda x: x[0] == emp_id and x[2] == 'sign_in' and x[
                              3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                sign_out = max(filter(lambda x: x[0] == emp_id and x[2] == 'sign_out' and x[
                               3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                hours = (sign_out[1] - sign_in[1]).seconds / 3600

                if sign_in and sign_out:
                    work_hours = 0
                    calendar = self.cache[emp_id, str(sign_out[1].weekday())]
                    calendar = filter(lambda x: self.get_date(
                        x['attendance'].date_from) <= sign_out[1], calendar)
                    for ca in calendar:
                        if sign_out >= ca['attendance'].date_from:
                            work_hours += ca['basic'].working_hours

                    if hours > work_hours:
                        count += (hours - work_hours)
        return int(count)

    def extra_off_day(self, emp_id):
        count = 0
        for day in self.off_days:
            if (emp_id, day, 'sign_in') in self.employees_attendance and\
               (emp_id, day, 'sign_out')in self.employees_attendance:
                sign_in = min(filter(lambda x: x[0] == emp_id and x[2] == 'sign_in' and x[
                              3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                sign_out = max(filter(lambda x: x[0] == emp_id and x[2] == 'sign_out' and x[
                               3] == day, self.employees_attendance_time.keys()), key=lambda x: x[1])
                hours = (sign_out[1] - sign_in[1]).seconds / 3600
                if sign_in and sign_out:
                    work_hours = 0

                    calendar = (emp_id, str(sign_out[1].weekday())) in self.cache and self.cache[
                        emp_id, str(sign_out[1].weekday())] or []
                    calendar = filter(lambda x: self.get_date(
                        x['attendance'].date_from) <= sign_out[1], calendar)
                    for ca in calendar:
                        if sign_out >= ca['attendance'].date_from:
                            work_hours += ca['basic'].working_hours

                    if hours > work_hours:
                        count += (hours - work_hours)
        return int(count)

    def period_work_hours(self, emp_id, start_date, end_date):
        work_hours = 0
        work_hours = self.values(emp_id, start_date, end_date)
        count = 0
        for crurent in self.off_days:
            flag2 = False
            if emp_id in self.unpaind_holiday_dates.keys():
                flag2 = self.get_date(crurent).date(
                ) in self.unpaind_holiday_dates[emp_id]
            if not flag2:
                count += 1

        return int(work_hours) + (count * 8)

    def get_holidays(self, start_date, end_date, emp_id):
        ##############################
        # get holidays of an employee
        ###########################################
        count = 0
        hr_holidays = self.pool.get('hr.holidays')
        end_date = end_date + " 23:59:59"

        hr_holidays_ids_first = hr_holidays.search(self.cr, self.uid,
                                                   [('employee_id', '=', emp_id),
                                                    ('state', '=', 'validate')],
                                                   context=self.context)

        hr_holidays_ids_second = hr_holidays.search(self.cr, self.uid,
                                                    [('employee_id', '=', emp_id),
                                                     ('state', '=', 'validate')],
                                                    context=self.context)

        List_ids = list(set(hr_holidays_ids_first) |
                        set(hr_holidays_ids_second))

        basic = hr_holidays.browse(
            self.cr, self.uid, List_ids, context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

        for holiday in basic:
            holiday_status_type = holiday.holiday_status_id.payroll_type

            holiday_start = datetime.strptime(
                holiday.date_from, "%Y-%m-%d %H:%M:%S")
            holiday_end = datetime.strptime(
                holiday.date_to, "%Y-%m-%d %H:%M:%S")

            while holiday_start <= holiday_end:
                if holiday_start >= start_date and holiday_start <= end_date:
                    if holiday_status_type == 'unpaied':
                        self.unpaind_holiday_dates[holiday.employee_id.id] = self.unpaind_holiday_dates.get(
                            holiday.employee_id.id, [])
                        self.unpaind_holiday_dates[
                            holiday.employee_id.id].append(holiday_start.date())
                    else:
                        self.holiday_dates[holiday.employee_id.id] = self.holiday_dates.get(
                            holiday.employee_id.id, [])
                        self.holiday_dates[holiday.employee_id.id].append(
                            holiday_start.date())
                        count += 1
                holiday_start += relativedelta(days=1)

        return count

    def get_events(self, emp_id, start_date, end_date):
        ##############################
        # get events of all employees
        ###########################################
        count = 0
        hr_public_events = self.pool.get('hr.public.events')

        hr_public_events_ids_first = hr_public_events.search(self.cr, self.uid,
                                                             [('start_date',
                                                               '>=', start_date)],
                                                             context=self.context)

        hr_public_events_ids_second = hr_public_events.search(self.cr, self.uid,
                                                              [('end_date',
                                                                '<=', end_date)],
                                                              context=self.context)

        List_ids = list(set(hr_public_events_ids_first) |
                        set(hr_public_events_ids_second))

        basic = hr_public_events.browse(
            self.cr, self.uid, List_ids, context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        for event in basic:
            if not event.dayofweek:
                event_start = datetime.strptime(event.start_date, "%Y-%m-%d")
                event_end = datetime.strptime(event.end_date, "%Y-%m-%d")
                while event_start >= start_date and event_start <= end_date and event_start <= event_end:
                    count += self.values(emp_id,
                                         str(event_start.date()), False)
                    event_start += relativedelta(days=1)

        return count

    def lines(self, data):
        lines = []
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        department_ids = data['form']['department_ids']
        # new_emp_ids = data['form']['emp_ids']
        employees_obj = self.pool.get('hr.employee')
        if department_ids:
            all_deps = []
            for dep_id in department_ids:
                all_deps.append(dep_id)
                new_deps_ids = self.pool.get('hr.department').search(
                    self.cr, self.uid, [('id', 'child_of', dep_id)], context=self.context)
                all_deps += new_deps_ids
            all_deps = list(set(all_deps))
            department_ids = all_deps
        if not department_ids:
            department_ids = self.pool.get('hr.department').search(
                self.cr, self.uid, [], context=self.context)
        self.employees_ids = employees_obj.search(self.cr, self.uid, [(
            'department_id', 'in', department_ids), ('state', '=', 'approved')])

        # if there is no employee
        if not self.employees_ids:
            return []

        # get off working days records in self.cache = {} object
        self.get_working_hours()

        # get off days records in self.off_days object
        self.get_off_days(start_date, end_date)

        # get attendance records in self.employees_attendance object
        self.get_attendance(start_date, end_date)

        # get training records in self.training object
        #self.get_training(start_date, end_date)

        #self.get_missions(start_date, end_date)
        start_date = self.get_date(start_date)
        end_date = self.get_date(end_date)
        # get days where employee not signed in
        while start_date <= end_date:
            for emp in self.employees_ids:
                if (emp, start_date.date()) not in self.employees_attendance_time.keys():
                    self.employees_attendance_time[(emp, start_date.date())] = {
                        'name': self.names[emp],
                        'date': start_date.date(),
                        'sign_in': "-",
                        'sign_out': "-",
                        'work': "-",
                        'over_time': "-",
                        'late_in': "-",
                        'early_out': "-",
                        'early_in': "-",
                        'short': "-",
                    }
            start_date += relativedelta(days=1)

        for rec in self.employees_attendance_time.keys():
            lines.append(self.employees_attendance_time[rec])

        lines = sorted(lines, key=lambda k: (k['date'], k['name']))

        if lines:
            new_lines = []
            new_lines.append(['name',
                              'date',
                              'sign_in',
                              'sign_out',
                              'work',
                              'over_time',
                              'late_in',
                              'early_out',
                              'early_in',
                              'short'])

            for line in lines:
                if line['sign_in'] != '-' and line['sign_out'] != '-' and line['late_in'] == '-' and line['early_out'] == '-':
                    continue
                new_line = []
                new_line.append(line['name'])
                new_line.append(line['date'])
                new_line.append(line['sign_in'])
                new_line.append(line['sign_out'])
                new_line.append(line['work'])
                new_line.append(line['over_time'])
                new_line.append(line['late_in'])
                new_line.append(line['early_out'])
                new_line.append(line['early_in'])
                new_line.append(line['short'])

                new_lines.append(new_line)

            lines = new_lines

            row = lines
            new_list = []
            header = row[0]
            flag = False
            i = 0

            for item in row:
                new_list.append(item)
                if i == 18 and not flag:
                    new_list.append(header)
                    flag = True
                    i = 0
                if i == 22 and flag:
                    new_list.append(header)
                    i = 0
                i += 1
            lines = new_list

        return lines


report_sxw.report_sxw('report.attendance_details_all.report', 'hr.attendance.percentage',
                      'addons/hr_attendance_custom/report/attendance_details.mako', parser=attendance_details_all)
