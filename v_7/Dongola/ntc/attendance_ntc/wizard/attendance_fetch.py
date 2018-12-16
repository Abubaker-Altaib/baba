# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date,datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _

from dateutil.relativedelta import relativedelta
from openerp import tools
from itertools import groupby
from operator import itemgetter


class attendance_percentage(osv.osv_memory):
    _name = "hr.attendance.fetch.wizard"

    _description = "Attendance Fetch Wizard"

    _columns = {
        'start_date':fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'department_ids':fields.many2many('hr.department',string='Departments'),
    }

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of start_date if greater than end_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            start_date = self.get_date(act.start_date)
            end_date = self.get_date(act.end_date)
            attendance_obj = self.pool.get('suggested.attendance')
            attendance_ids = attendance_obj.search(cr, uid, [],context=context)
            dates = attendance_obj.read(cr, uid, attendance_ids, ['start_date','end_date'], context=context)

            dates = [{'start_date':self.get_date(x['start_date']),'end_date':self.get_date(x['end_date'])} for x in dates]
            for date in dates:
                case0 = date['start_date'] >= start_date and date['end_date'] <= end_date

                case1 = date['start_date'] <= start_date and date['end_date'] >= end_date

                case2 = date['start_date'] <= start_date and start_date <= date['end_date'] 

                case3 = start_date <= date['start_date'] and date['start_date'] <= end_date
                
                if case0 or case1 or case2 or case3:
                    raise osv.except_osv(_('Error'), _("THIS RANGE OF DATE HAVE BEEN FETCHED BEFORE"))

            if ((start_date > end_date) and end_date):
                raise osv.except_osv(_('ValidateError'), _("Start Date Must Be Less Than End Date"))
        return True
    
    _constraints = [
        (_check_date, _(''), ['start_date','end_date']),
    ]

    def fetch(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['emp_ids'] = []
        datas = {'form':data}
        self.cr =cr
        self.uid=uid
        self.context = context
        self.off_week_days = [4,5]#friday and saturday
        self.holiday_dates = {}
	self.unpaind_holiday_dates ={}
        self.lines(datas)
    

    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")

    def values(self,emp_id,start_date,end_date):
        work_hours = 0

        #to count hours for one day
        if not end_date:
            end_date = start_date

        start_date = self.get_date(start_date)
        end_date = self.get_date(end_date)

        if not emp_id:
            while start_date <= end_date:
                for key in self.cache.keys():
                    if key[1] == str(start_date.weekday() ) :
                        calendar = filter(lambda x : self.get_date(x['attendance'].date_from) <= start_date,self.cache[key])
                        calendar =calendar and [max( calendar, key = lambda x: self.get_date(x['attendance'].date_from) )] or []
                        for record in calendar:
                            if self.get_date( record['attendance'].date_from ) <= start_date:
                                work_hours += record['basic'].working_hours

                start_date += relativedelta(days=1)



        if emp_id:
            while start_date <= end_date:
                flag2 = False
                if emp_id in self.unpaind_holiday_dates.keys() :
                    flag2 = start_date.date() in self.unpaind_holiday_dates[emp_id]
                if str( start_date.date() ) in self.work_days and not flag2:
                    if (emp_id,str(start_date.weekday() ) ) in self.cache.keys():
                        calendar = filter(lambda x : self.get_date(x['attendance'].date_from) <= start_date,self.cache[(emp_id,str(start_date.weekday() ) )])
                        calendar =calendar and [max( calendar, key = lambda x: self.get_date(x['attendance'].date_from) )] or []
                        for record in calendar:
                            if self.get_date( record['attendance'].date_from ) <= start_date:
                                work_hours += record['basic'].working_hours
                    
                start_date += relativedelta(days=1)
        
        return work_hours

    def get_caches(self,emp_id,start_date,end_date):
        List = []
        start_date = self.get_date(start_date)
        end_date = self.get_date(end_date)

        while start_date <= end_date:
            if str( start_date.date() ) in self.work_days:
                if (emp_id,str(start_date.weekday()) ) in self.cache.keys():
                    for record in self.cache[(emp_id,str(start_date.weekday()) )]:
                        if self.get_date( record['attendance'].date_from ) <= start_date:
                            List.append(record)
            start_date += relativedelta(days=1)
        return List


    def get_training(self, start_date, end_date ):
        ##############################
        #get events of all employees
        ###########################################
        count = 0
        self.training = {}
        hr_training_approved = self.pool.get('hr.employee.training.approved')

        hr_training_approved_ids_first = hr_training_approved.search(self.cr,self.uid, 
            [('state','=','approved')],
             context=self.context)

        hr_training_approved_ids_second= hr_training_approved.search(self.cr,self.uid, 
            [('state','=','approved')],
             context=self.context)

        List_ids = list(set(hr_training_approved_ids_first) | set(hr_training_approved_ids_second))

        basic = hr_training_approved.browse(self.cr,self.uid,List_ids,context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date   = datetime.strptime(end_date  , "%Y-%m-%d")

        for training in basic:
            event_start = datetime.strptime(training.start_date, "%Y-%m-%d")
            event_end = datetime.strptime(training.end_date, "%Y-%m-%d")
            while event_start >= start_date and event_start <= end_date and event_start <= event_end :
                count += 1 
                event_start += relativedelta(days=1)
            for emp in training.line_ids:
                self.training[emp.employee_id.id] = self.training.get(emp.employee_id.id,0)
                hours = (training.end_time - training.start_time) * emp.days
                self.training[emp.employee_id.id] += int(hours)



    def get_missions(self, start_date, end_date ):
        ##############################
        #get events of all employees
        ###########################################
        count = 0
        #self.training = {}
        employee_mission = self.pool.get('hr.employee.mission')

        employee_mission_ids_first = employee_mission.search(self.cr,self.uid, 
            [('state','in', ('approved', 'hr_approved', 'reviewed', 'done') )],
             context=self.context)

        employee_mission_ids_second= employee_mission.search(self.cr,self.uid, 
            [('state','in', ('approved', 'hr_approved', 'reviewed', 'done') )],
             context=self.context)

        List_ids = list(set(employee_mission_ids_first) | set(employee_mission_ids_second))

        basic = employee_mission.browse(self.cr,self.uid,List_ids,context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date   = datetime.strptime(end_date  , "%Y-%m-%d")
        self.missions_dates = {}
        for training in basic:
            count = 0
            event_start = datetime.strptime(training.start_date, "%Y-%m-%d")
            event_end = datetime.strptime(training.end_date, "%Y-%m-%d")
            dates_list = []
            while event_start <= event_end :
                if event_start >= start_date and event_start <= end_date:
                    dates_list.append(event_start.date())
                    count += 1 
                event_start += relativedelta(days=1)
            for emp in training.mission_line:
                self.training[emp.employee_id.id] = self.training.get(emp.employee_id.id,0)
                hours = emp.days * 8
                if count < emp.days:
                    hours = count * 8
                self.training[emp.employee_id.id] += int(hours)

                self.missions_dates[emp.employee_id.id] = self.missions_dates.get(emp.employee_id.id,[])

                self.missions_dates[emp.employee_id.id] += dates_list
                    





    def get_working_hours(self):
        ##############################
        #get the working hours for all selected employees
        ###########################################

        self.cache = {}
        resource_calendar = self.pool.get('resource.calendar')

        resource_calendar_ids = resource_calendar.search(self.cr,self.uid,[],
             context=self.context)

        for basic in resource_calendar.browse(self.cr,self.uid,resource_calendar_ids,context=self.context):
            for i in basic.employees_ids:
                for attendance in basic.attendance_ids: 
                    self.cache[i.id,str(attendance.dayofweek)] = self.cache.get((i.id,attendance.dayofweek),[])
                    self.cache[i.id,str(attendance.dayofweek)] .append({'basic':basic,'attendance':attendance})


        

    def get_off_days(self, start_date, end_date):
        ##############################
        #get the off_days in selected range
        ###########################################

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.off_days = []
        self.work_days = []
        while start_date <= end_date:
            if start_date.weekday() in self.off_week_days:
                self.off_days.append(start_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
            else:
                self.work_days.append(start_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
            start_date += relativedelta(days=1)



    def get_attendance(self, start_date, end_date):
        ##############################
        #get the attendance of all selected employees
        ###########################################
        hr_attendance = self.pool.get('hr.attendance')
        emp_codes = self.pool.get('hr.employee').read(self.cr, self.uid, self.employees_ids,['emp_code', 'id'],context=self.context)
        emp_codes = {int(x['emp_code']): int(x['id'])for x in emp_codes }
        hr_attendance_ids = hr_attendance.search(self.cr,self.uid, 
            [ ('employee_id', 'in', emp_codes.keys()) ],
             context=self.context)
                
        basic = hr_attendance.browse(self.cr,self.uid,hr_attendance_ids,context=self.context)

        groups = groupby(basic,key=lambda x: (emp_codes[x.employee_id], str(x.day),x.action ))
        
        self.employees_attendance = {}
        for k,itr in groups:
            self.employees_attendance[k] = self.employees_attendance.get(k,[])
            for i in itr:
                self.employees_attendance[k].append(i)


        groups_time = groupby(basic,key=lambda x: (emp_codes[x.employee_id], datetime.strptime(x.name, "%Y-%m-%d %H:%M:%S"),x.action ))
        
        self.employees_attendance_time = {}
        for k,itr in groups_time:
            #to use the date in search
            k  += (k[1].date().strftime(tools.DEFAULT_SERVER_DATE_FORMAT),)
            self.employees_attendance_time[k] = self.employees_attendance_time.get(k,[])
            for i in itr:
                self.employees_attendance_time[k].append(i)


    def abacense_days(self,emp_id,start_date, end_date):
        count = 0
        count_h = 0
        for day in self.work_days:
            flag = False
            flag2 = False
            flag3 = False
            if emp_id in self.holiday_dates.keys() :
                flag = self.get_date(day).date() in self.holiday_dates[emp_id]
            
            if emp_id in self.unpaind_holiday_dates.keys() :
                flag2 = self.get_date(day).date() in self.unpaind_holiday_dates[emp_id]

            if emp_id in self.missions_dates.keys() :
                flag3 = self.get_date(day).date() in self.missions_dates[emp_id]

            if (emp_id,day,'sign_in') not in self.employees_attendance and (emp_id,day,'sign_out') not in self.employees_attendance and not flag and not flag2 and not flag3:
                count+=1
                count_h += self.values(emp_id,day, False)


        return int(count),int(count_h)


    def late_days(self,emp_id):
        count = 0
        count_h = 0.0

        for day in self.work_days:
            if (emp_id,day,'sign_in') in self.employees_attendance and\
               (emp_id,day,'sign_out')in self.employees_attendance:
                sign_in = min( filter(lambda x:x[0] == emp_id and x[2] == 'sign_in'  and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                sign_out =max( filter(lambda x:x[0] == emp_id and x[2] == 'sign_out' and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                hours = (sign_out[1] - sign_in[1] ).seconds / 3600.0
                work_hours = 0
                calendar = self.cache[emp_id,str( sign_out[1].weekday() )]
                calendar = filter(lambda x : self.get_date(x['attendance'].date_from) <= sign_out[1],calendar)

                calendar = calendar and [max( calendar, key = lambda x: self.get_date(x['attendance'].date_from) )] or []
                
                for ca in calendar:
                    work_hours+=ca['basic'].working_hours
                
                #change it to float
                work_hours *= 1.0

                if hours < work_hours:
                    count+=1
                    count_h+= (work_hours - hours)

        return int(count),round(count_h,2)

    def early_out(self,emp_id):
        count = 0
        for day in self.work_days:
            if (emp_id,day,'sign_in') in self.employees_attendance and\
               (emp_id,day,'sign_out')in self.employees_attendance:
                sign_out =max( filter(lambda x:x[0] == emp_id and x[2] == 'sign_out' and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                if sign_out:
                    calendar = self.cache[emp_id,str( sign_out[1].weekday() )]
                    calendar = filter(lambda x : self.get_date(x['attendance'].date_from) <= sign_out[1], calendar)
                    calendar =calendar and [max( calendar, key = lambda x: self.get_date(x['attendance'].date_from) )] or []

                    if calendar:
                        last_hour = max(calendar, key = lambda x: x['attendance'].hour_to )
                        if float( str( sign_out[1].hour )+'.'+str( sign_out[1].minute ) ) < last_hour['attendance'].hour_to:
                            count+=1

        return int(count)

    def forget_finger_print(self,emp_id):
        count = 0
        count_h = 0
        for day in self.work_days:
            if (emp_id,day,'sign_in') in self.employees_attendance or\
               (emp_id,day,'sign_out')in self.employees_attendance:
                sign_in_sign_out =filter(lambda x:x[0] == emp_id and x[1] == day and (x[2] == 'sign_in' or x[2] == 'sign_out') ,self.employees_attendance.keys())
                if len(sign_in_sign_out) == 1:
                    count+=1
        return int(count)

    def forget_finger_print_hours(self,emp_id,forget_finger_print,start_date,end_date):
        count = 0
        basics = [x['basic'] for x in self.get_caches(emp_id,start_date,end_date)]
        basics=list(set(basics))
        basics = [basics[0]]
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

    def extra_work_day(self,emp_id):
        count = 0
        for day in self.work_days:
            if (emp_id,day,'sign_in') in self.employees_attendance and\
               (emp_id,day,'sign_out')in self.employees_attendance:
                sign_in = min( filter(lambda x:x[0] == emp_id and x[2] == 'sign_in'  and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                sign_out =max( filter(lambda x:x[0] == emp_id and x[2] == 'sign_out' and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                hours = (sign_out[1] - sign_in[1] ).seconds / 3600
                
                if sign_in and sign_out:
                    work_hours = 0
                    calendar = self.cache[emp_id,str( sign_out[1].weekday() )]
                    calendar = filter(lambda x : self.get_date(x['attendance'].date_from) <= sign_out[1], calendar)

                    calendar =calendar and [max( calendar, key = lambda x: self.get_date(x['attendance'].date_from) )] or []

                    for ca in calendar:
                        if sign_out >= ca['attendance'].date_from:
                            work_hours+=ca['basic'].working_hours

                    if hours > work_hours:
                        count+=(hours - work_hours)
        return int(count)

    def extra_off_day(self,emp_id):
        count = 0
        for day in self.off_days:
            if (emp_id,day,'sign_in') in self.employees_attendance and\
               (emp_id,day,'sign_out')in self.employees_attendance:
                sign_in = min( filter(lambda x:x[0] == emp_id and x[2] == 'sign_in'  and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                sign_out =max( filter(lambda x:x[0] == emp_id and x[2] == 'sign_out' and x[3] == day,self.employees_attendance_time.keys()), key = lambda x: x[1] )
                hours = (sign_out[1] - sign_in[1] ).seconds / 3600
                if sign_in and sign_out:
                    work_hours = 0

                    calendar = ( emp_id,str( sign_out[1].weekday() ) ) in self.cache and self.cache[emp_id,str( sign_out[1].weekday() )] or []
                    calendar = filter(lambda x : self.get_date(x['attendance'].date_from) <= sign_out[1], calendar)

                    calendar =calendar and [max( calendar, key = lambda x: self.get_date(x['attendance'].date_from) )] or []

                    for ca in calendar:
                        if sign_out >= ca['attendance'].date_from:
                            work_hours+=ca['basic'].working_hours

                    if hours > work_hours:
                        count+=(hours - work_hours)
        return int(count)

    def period_work_hours(self,emp_id,start_date,end_date):
        work_hours = 0
        work_hours = self.values(emp_id,start_date,end_date)
        count = 0
        for crurent in self.off_days:
            flag2 = False
            if emp_id in self.unpaind_holiday_dates.keys() :
                flag2 = self.get_date(crurent).date() in self.unpaind_holiday_dates[emp_id]
            
            flag1 = False
            if emp_id in self.missions_dates.keys() :
                flag1 = self.get_date(crurent).date() in self.missions_dates[emp_id]

            if not (flag1 or flag2):
                count += 1
        
        return int(work_hours) + (count*8)


    def get_holidays(self, start_date, end_date, emp_id ):
        ##############################
        #get holidays of an employee
        ###########################################
        count = 0
        hr_holidays = self.pool.get('hr.holidays')
        start_date = start_date+" 00:00:00"
        end_date = end_date+" 23:59:59"

        permissions_ids = self.pool.get('hr.holidays.status').search(self.cr, self.uid, [('permission','=',True)])

        hr_holidays_ids_first = hr_holidays.search(self.cr,self.uid, 
            [('employee_id','=',emp_id), ('state','in',('validate', 'done_cut') ),('holiday_status_id','not in',permissions_ids )],
             context=self.context)

        hr_holidays_ids_second= hr_holidays.search(self.cr,self.uid, 
            [('employee_id','=',emp_id), ('state','in',('validate', 'done_cut') ),('holiday_status_id','not in',permissions_ids )],
             context=self.context)

        List_ids = list(set(hr_holidays_ids_first) | set(hr_holidays_ids_second))

        
        basic = hr_holidays.browse(self.cr,self.uid,List_ids,context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").date()
        end_date   = datetime.strptime(end_date  , "%Y-%m-%d %H:%M:%S").date()

        for holiday in basic:
            holiday_status_type =  holiday.holiday_status_id.payroll_type

            holiday_start = datetime.strptime(holiday.date_from, "%Y-%m-%d %H:%M:%S").date()
            holiday_end = datetime.strptime(holiday.date_to, "%Y-%m-%d %H:%M:%S").date()

            while holiday_start <= holiday_end:
                if holiday_start >= start_date and holiday_start <= end_date:
                    if holiday_status_type == 'unpaied':
                        self.unpaind_holiday_dates[holiday.employee_id.id] = self.unpaind_holiday_dates.get(holiday.employee_id.id,[])
                        self.unpaind_holiday_dates[holiday.employee_id.id].append(holiday_start)
                    else:
                        self.holiday_dates[holiday.employee_id.id] = self.holiday_dates.get(holiday.employee_id.id,[])
                        self.holiday_dates[holiday.employee_id.id].append(holiday_start)
                        count+=1
                holiday_start += relativedelta(days=1)

        return count


    def get_events(self, emp_id, start_date, end_date ):
        ##############################
        #get events of all employees
        ###########################################
        count = 0
        hr_public_events = self.pool.get('hr.public.events')

        hr_public_events_ids_first = hr_public_events.search(self.cr,self.uid, 
            [('start_date','>=', start_date)],
             context=self.context)

        hr_public_events_ids_second= hr_public_events.search(self.cr,self.uid, 
            [('end_date' ,'<=', end_date)],
             context=self.context)

        List_ids = list(set(hr_public_events_ids_first) | set(hr_public_events_ids_second))

        basic = hr_public_events.browse(self.cr,self.uid,List_ids,context=self.context)

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date   = datetime.strptime(end_date  , "%Y-%m-%d")

        for event in basic:
            if not event.dayofweek:
                event_start = datetime.strptime(event.start_date, "%Y-%m-%d")
                event_end = datetime.strptime(event.end_date, "%Y-%m-%d")
                while event_start >= start_date and event_start <= end_date and event_start <= event_end :
                    count+=self.values(emp_id,str(event_start.date()),False)
                    event_start += relativedelta(days=1)

        return count

        





    def lines(self,data):
        lines = []
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        department_ids = data['form']['department_ids']
        new_emp_ids = data['form']['emp_ids']
        employees_obj = self.pool.get('hr.employee')
        if not department_ids:
            department_ids = self.pool.get('hr.department').search(self.cr, self.uid, [], context=self.context)
        self.employees_ids = employees_obj.search(self.cr, self.uid, [('department_id','in',department_ids), ('state','=','approved')])
        if new_emp_ids:
            self.employees_ids = new_emp_ids
        #if there is no employee
        if not self.employees_ids:
            return []

        #get off working days records in self.cache = {} object
        self.get_working_hours()

        #get off days records in self.off_days object
        self.get_off_days(start_date, end_date)
        
        #get attendance records in self.employees_attendance object
        self.get_attendance(start_date, end_date)

        #get training records in self.training object
        self.get_training(start_date, end_date)

        self.get_missions(start_date, end_date)

        for emp in employees_obj.browse(self.cr,self.uid,self.employees_ids,self.context):
            emp_list = {'emp_id':emp.id, 'name':emp.name,'department':emp.department_id.name}
            emp_list['get_holidays'] = self.get_holidays(start_date, end_date, emp.id)
            emp_list['abacense_days'],emp_list['abacense_hours'] = self.abacense_days(emp.id,start_date,end_date)
            emp_list['late_days'],emp_list['late_hours'] = self.late_days(emp.id)
            emp_list['early_out'] = self.early_out(emp.id)
            emp_list['forget_finger_print'] = self.forget_finger_print(emp.id)
            emp_list['extra_work_day'] = self.extra_work_day(emp.id)
            emp_list['extra_off_day'] = self.extra_off_day(emp.id)
            emp_list['period_work_hours'] = self.period_work_hours(emp.id,start_date,end_date)
            emp_list['forget_finger_print_hours'] = self.forget_finger_print_hours(emp.id,emp_list['forget_finger_print'],start_date,end_date)
            
            #emp_list['get_events'] = self.get_events(emp.id, start_date, end_date) 
            emp_list['training'] = (emp.id in self.training) and self.training[emp.id] or 0


            emp_list['earned'] = emp_list['period_work_hours'] - emp_list['abacense_hours']
            emp_list['earned'] = emp_list['earned'] - emp_list['forget_finger_print_hours']
            emp_list['earned'] = emp_list['earned'] - emp_list['late_hours']
            emp_list['earned'] = emp_list['earned'] #+ emp_list['training']# + emp_list['get_events']
            emp_list['percent']= 0 
            try:
                emp_list['percent']= emp_list['earned']/emp_list['period_work_hours'] * 100
                emp_list['percent'] = round(emp_list['percent'],2)
                emp_list['added_percent'] = emp_list['percent']
            except Exception, e:
                print ""
                
            
            if emp_list['period_work_hours'] != 0:
                lines.append(emp_list)
        if lines:
            if len(new_emp_ids) != 1:
                suggested_attendance_obj = self.pool.get('suggested.attendance')
                suggested_attendance_line_obj = self.pool.get('suggested.attendance.line')
                self.context = self.context and self.context or {}
                self.context['wizard'] = True
                attendance_id = suggested_attendance_obj.create(self.cr, self.uid, {'lines_ids':[(0,0,x)for x in lines],
                'start_date':self.get_date(start_date),
                'end_date':self.get_date(end_date)}, context=self.context)
                
        
        if lines:
            new_lines = []
            new_lines.append([u'ملاحظات',u'نسبة العمل',
            u'عدد الساعات المستحقة',u'ساعات التدريب والماموريات',
            u'عدد ساعات التأخير',u'عدد ساعات نسيان البصمة',
            u'عدد ساعات الغياب',u' عدد الساعات في الشهر من'+str(data['form']['start_date']),
            u'الساعات أﻹضافية ايام العطلة',u'الساعات أﻹضافية ايام العمل',
            u'عدد أيام نسيان البصمة',u'عدد أيام الخروج المبكر',
            u'عدد أيام التأخير',u'عدد أيام اجازة',
            u'عدد أيام غياب',u'اﻹدارة',u'اﻹسم'])
            counter = 1
            for line in lines:
                new_line = []
                new_line.append('')
                new_line.append(line['percent'])
                new_line.append(line['earned'])
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
            lines = new_lines

            row = lines
            new_list = []
            header = row[0]
            flag = False
            i = 0

            for item in row:
                new_list.append(item)
                if i == 11 and not flag:
                    new_list.append(header)
                    flag = True
                    i = 0
                if i == 14 and flag:
                    new_list.append(header)
                    i = 0
                i += 1
            lines = new_list
            
        return lines