# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################import datetime
from openerp import addons
import logging
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools
import mx
import datetime
import time
from itertools import groupby
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.osv.orm import except_orm
from urlparse import urljoin
from urllib import urlencode
from admin_affairs.model.email_serivce import send_mail



class  hr_holidays_status(osv.osv):
    """
    Inherit hr.holidays.status and add new fields to the configuration
    of the holiday in order to be used in the buying or end of service process. 
    """
    _inherit = "hr.holidays.status"


    def get_days(self, cr, uid, ids, employee_id, return_false, context=None):
        """
        Method Retrieves number of days, taken days and remain days for specific employee for each holiday.
        @return: Dictionary of values
        """
        holidays_obj = self.pool.get('hr.holidays')
        year = time.strftime('%Y')
        date = year + '-'+time.strftime('%m')+'-'+time.strftime('%d')+ " 23:59:59"
        month = time.strftime('%m')
        curr_id = context.has_key('id') and context['id'] or []
        rec = self.browse(cr,uid,ids[0])

        if rec.sick_day or rec.permission:
            if curr_id:
                cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id, 
                    to_char(h.date_from,'YYYY') as year, h.remaining_days, EXTRACT(MONTH FROM h.date_from) 
                              FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id   
                              WHERE h.employee_id = %s AND h.state not in ('draft','cancel','refuse') AND 
                                    h.holiday_status_id in %s and h.id != %s and s.leave_limit='annual' and 
                                    EXTRACT(MONTH FROM h.date_from) = %s and to_char(h.date_from,'YYYY') = cast(%s as varchar(5))
                                    ORDER BY h.date_from, h.id """,
                    [employee_id, tuple(ids),curr_id, month,year])
            else:
                cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id, 
                    to_char(h.date_from,'YYYY') as year, h.remaining_days 
                              FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id   
                              WHERE h.employee_id = %s AND h.state not in ('draft','cancel','refuse') AND 
                                    h.holiday_status_id in %s and s.leave_limit='annual' and 
                                    EXTRACT(MONTH FROM h.date_from) = %s and to_char(h.date_from,'YYYY') = cast(%s as varchar(5))
                                    ORDER BY h.date_from, h.id """,
                    [employee_id, tuple(ids), month,year])

        # if leave limit is annual and leave save is True add remaining days from past years based on number of save years 
        else:
            '''cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id 
                          FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id 
                          WHERE h.employee_id = %s AND h.state not in ('draft','cancel','refuse') AND 
                                h.holiday_status_id in %s and ((s.leave_limit='annual' and (h.date_from <= %s and 
                                (s.save_leave = False and to_char(h.date_from,'YYYY') = cast(%s as varchar(5))) or
                                (s.save_leave = True and to_char(h.date_from,'YYYY') >= cast(%s - s.save_years as varchar(5)) ))) or 
                                s.leave_limit='once')""",
                [employee_id, tuple(ids), date,year, year])'''

            if curr_id:
                cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id, 
                    to_char(h.date_from,'YYYY') as year, h.remaining_days 
                              FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id   
                              WHERE h.employee_id = %s AND h.state in ('validate','done_cut') AND 
                                    h.holiday_status_id in %s and h.id != %s and ((s.leave_limit='annual' and (h.date_from <= %s and 
                                    (s.save_leave = False and to_char(h.date_from,'YYYY') = cast(%s as varchar(5))) or 
                                    s.save_leave = True )) or 
                                    s.leave_limit='once')
                                    ORDER BY h.date_from, h.id """,
                    [employee_id, tuple(ids),curr_id, date,year])
            else:
                cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id, 
                    to_char(h.date_from,'YYYY') as year, h.remaining_days 
                              FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id   
                              WHERE h.employee_id = %s AND h.state in ('validate','done_cut') AND 
                                    h.holiday_status_id in %s and ((s.leave_limit='annual' and (h.date_from <= %s and 
                                    (s.save_leave = False and to_char(h.date_from,'YYYY') = cast(%s as varchar(5))) or 
                                    s.save_leave = True )) or 
                                    s.leave_limit='once')
                                    ORDER BY h.date_from, h.id """,
                    [employee_id, tuple(ids), date,year])
        result = sorted(cr.dictfetchall(), key=lambda x: x['holiday_status_id'])
        grouped_lines = dict((k, [v for v in itr]) for k, itr in groupby(result, itemgetter('holiday_status_id')))
        res = {}
        last_taken_leaves = 0
        for record in self.browse(cr, uid, ids, context=context):
            leaves_taken = 0
            remaining_leave = 0
            max_leaves = record.number_of_days
            max_leaves2 = record.number_of_days
            all_leaves = record.number_of_days
            sum_old_taken = 0
            
            if record.linked_with_unpaid_leaves:
                cr.execute("""SELECT h.number_of_days_temp
                    FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id 
                    WHERE h.employee_id = %s AND h.state = 'validate' AND 
                        h.holiday_status_id != %s and h.date_from <= %s """,
                [employee_id, record.id, date])

                sum_old_taken = sum( [ x.get('number_of_days_temp') for x in cr.dictfetchall() ] )


                day_wheight = 365/max_leaves

                sum_old_taken = int(sum_old_taken/day_wheight)   
            if record.leave_limit == 'annual' and record.save_leave:
                save_years=record.save_years
                if employee_id:
                    emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
                    start_date=emp.re_employment_date or emp.employment_date or time.strftime('%Y-%m-%d')
                    employment_year= datetime.datetime.strptime(start_date, '%Y-%m-%d').year
                    employment_years=int(year) - int(employment_year)
                    if employment_years < save_years:
                        save_years=employment_years
                max_leaves += max_leaves * save_years 
                all_leaves += employment_years * record.number_of_days

                if record.id in grouped_lines:
                    grouped_lines_remaining = dict((k, [v for v in itr]) for k, itr in groupby(grouped_lines[record.id], itemgetter('year')))
                    year_list = range(int(year),int(year)-save_years-1, -1)
                    year_dic = grouped_lines_remaining.has_key(year) and grouped_lines_remaining[year] or []
                    if year_dic:
                            remaining_leave = year_dic[len(year_dic)-1]['remaining_days']
                            leaves_taken = max_leaves - remaining_leave
                    else:
                        if len(year_list) > 1:
                            for x in year_list[1:]:
                                year_dic1 = grouped_lines_remaining.has_key(str(x)) and grouped_lines_remaining[str(x)] or []
                                max_leaves2 = record.number_of_days
                                save_years2= record.save_years
                                index = year_list.index(x)
                                employment_year2=x - int(employment_year)
                                if employment_year2 < save_years2:
                                    save_years2=employment_year2
                                max_leaves2 += max_leaves2 * save_years2
                                if year_dic1:
                                    #remain = year_dic1[len(year_dic1)-1]['remaining_days'] and year_dic1[len(year_dic1)-1]['remaining_days'] or max_leaves2
                                    remain = year_dic1[len(year_dic1)-1].has_key('remaining_days') and year_dic1[len(year_dic1)-1]['remaining_days']
                                    remaining_leave = remain + record.number_of_days*index
                                    leaves_taken = max_leaves - remaining_leave

                                
                                break

                    if remaining_leave > max_leaves:
                        remaining_leave = max_leaves
                        leaves_taken = 0            
                else:
                    remaining_leave = max_leaves
                    leaves_taken = 0

            remaining_sum=0
            remain=0
            last_degre = 0
            Leaves=[]
            if record.check_remain or record.save_remain:
                    cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id ,h.remaining_leaves, s.number_of_days
                        FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id 
                        WHERE h.employee_id = %s AND h.state = 'validate' AND s.leave_limit='annual' AND
                            h.holiday_status_id != %s and h.date_from <= %s """,
                    [employee_id, record.id, date])
                    result_old = sorted(cr.dictfetchall(), key=lambda x: x['holiday_status_id'])
                    grouped_lines_unpaid_annual = dict((k, [v for v in itr]) for k, itr in groupby(result_old, itemgetter('holiday_status_id')))
                    for rec in grouped_lines_unpaid_annual:
                        Leaves.append(rec)

                    emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
                    if emp.degree_id.sequence:
                        last_degre = emp.degree_id.sequence + 1
                    last_degree_id = self.pool.get('hr.salary.degree').search(cr, uid, [('sequence','=',last_degre)])
                    if last_degree_id:
                        hol_leave = self.pool.get('hr.holidays.status').browse(cr, uid, Leaves)
                        for leav in hol_leave:
                            Leaves=[]
                            for categ in leav.category_ids:
                                for Categories in emp.category_ids:
                                    if categ.id  == Categories.id and categ.id not in Leaves :
                                        Leaves.append(leav.id)
                        for rec in grouped_lines_unpaid_annual:
                            length_key = len(grouped_lines_unpaid_annual[rec])
                            if rec in Leaves:
                                    last_leave = self.pool.get('hr.holidays.status').browse(cr, uid, rec) 
                                    #remain = last_leave.number_of_days + (last_leave.number_of_days * last_leave.save_years)
                                    for item in grouped_lines_unpaid_annual[rec]:
                                        last_taken_leaves += item['number_of_days_temp']
                                        if item['number_of_days'] > last_taken_leaves:
                                            remain =   item['number_of_days'] - last_taken_leaves 
                                        else:
                                            remain =   last_taken_leaves  - item['number_of_days']
                                
                        max_leaves += remain
        
            if not return_false:
                if record.id in grouped_lines:
                    if not (record.leave_limit == 'annual' and record.save_leave):
                        leaves_taken = sum([item['number_of_days_temp'] for item in grouped_lines[record.id]])
                        remaining_leave = all_leaves - leaves_taken
                        leaves_taken = max_leaves - remaining_leave
                    if remaining_leave > max_leaves:
                       remaining_leave = max_leaves
                       leaves_taken = 0

            
            res[record.id] = {'max_leaves' : max_leaves, 'leaves_taken' : leaves_taken, 'remaining_leaves': max_leaves - leaves_taken - sum_old_taken}
        return res


    _columns = {
         'advance_leave': fields.boolean('Allow Leave IN Advance'),
         'sick_leave': fields.boolean('Sick Leave'),
         'advance_leave_days': fields.integer('Leave IN Advance Days',size=64),
         'sick_day': fields.boolean('Sick Day'),
         'allow_cut': fields.boolean('Allow Leave Cut'), 
                }
    
    _defaults = {
            'advance_leave': False,
            'sick_leave': False,
            'sick_day': False,
            'allow_cut': False,
              }

#----------------------------------------
#holiday(inherit)
#----------------------------------------
class  hr_holidays(osv.osv):
     _inherit = "hr.holidays"
     _order = "date_from desc"

     """inherit hr.holiday and add new fields associated to the buying  pocess
     """
     _track = {
        'state': {
            'hr_ntc_custom.mt_holidays_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_holidays.mt_holidays_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'validate',
            'hr_holidays.mt_holidays_refused': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'refuse',
            'hr_holidays.mt_holidays_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_ntc_custom.mt_holidays_unit_manag': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'unit_manag',
            'hr_ntc_custom.mt_holidays_dep_manag': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'dep_manag',
            'hr_ntc_custom.mt_holidays_general_dep': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'general_dep',
            'hr_ntc_custom.mt_holidays_hr_finance1': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_finance1',
            'hr_ntc_custom.mt_holidays_hr_finance2': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_finance2',
            'hr_ntc_custom.mt_holidays_cut': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cut',
            'hr_ntc_custom.mt_holidays_approve_cut': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approve_cut',
            'hr_ntc_custom.mt_holidays_general_dep_cut': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'general_dep_cut',
            'hr_ntc_custom.mt_holidays_hr_finance1_cut': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_finance1_cut',
            'hr_ntc_custom.mt_holidays_hr_finance2_cut': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_finance2_cut',
            'hr_ntc_custom.mt_holidays_done_cut': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done_cut',
            
        },
    }

     def __compute_remaining(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for holiday in self.browse(cr, uid, ids, context=context):
            context['id'] = holiday.id
            holiday_details = self.pool.get('hr.holidays.status').browse(cr, uid, holiday.holiday_status_id.id, context=context)
            remaining = holiday_details.get_days(holiday.employee_id.id, False)[holiday_details.id]['remaining_leaves']
            remaining = remaining - holiday.number_of_days_temp
            res[holiday.id] = remaining
        return res

     def _allow_cut(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.allow_cut == True:
                result[holiday.id] = True
            else:
                result[holiday.id] = False
        return result

     def _default_allow_cut(self, cr, uid, context=None):
        """ 
            To check if Leave type allow Cutand then return boolean field
        """
        result = False
        status_obj = self.pool.get('hr.holidays.status')
        if context.has_key('holiday_status_id'):
            if status_obj.browse(cr,uid,context['holiday_status_id']).allow_cut:
                result = True
        
        return result

     _columns = {
        'advance_leave': fields.boolean('Leave IN Advance'),
        'advance_leave2': fields.boolean('Leave IN Advance22'),
	    'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), 
            ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('unit_manag', 'Waiting Department Manager Approve'),
            ('dep_manag', 'Waiting General Department Manager Approve'),
            ('general_dep','Waiting HR and Financial Manager Approve'),
            ('hr_finance1', 'Waiting General Manager Approve'),
            ('review', 'Waiting Reviewer'),
            ('hr_finance2', 'Waiting HR Implementation'),
            #('general_manag', 'Waiting HR Implementation'),
            ('validate','Approve Done'), 
            ('cut', 'Waiting Cut Approval From Department Manager'), 
            ('approve_cut', 'Waiting Cut Approval From General Department Manager'),
            ('general_dep_cut','Waiting Cut Approval From HR and Financial Manager'),
            ('hr_finance1_cut', 'Waiting Cut Approval From General Manager'),
            ('hr_finance2_cut', 'Waiting Cut Implementation From HR'),
            #('general_manag_cut', 'Waiting Cut Implementation From HR'), 
            ('done_cut', 'Done Cut'),('postpone', 'Postpone'), 
            ('confirm_buying', 'To Leave Buying'), ('holiday_buying','Leave Buying'),('holiday_end_service','End of Service Allowance'), 
            ('paid','Paid')], 'State', readonly=True),
        'remaining_days': fields.function(__compute_remaining, Type='integer', string='Remaining Days', 
            store={
            'hr.holidays': (lambda self, cr,uid,ids,c: ids, ['state', 'holiday_status_id'], 10),
            }),
        'active' : fields.boolean('Active'),
        'email': fields.char('Email', size=240),
        'manager_user_id': fields.many2one('res.users', "Manager user"),
        'url':fields.char('URL',size=156, readonly=True,),
        'reject_reason': fields.text('Reject Reasons'),
        'allow_cut': fields.function(_allow_cut,type="boolean", string='Allow Cut'),
                }

     _defaults = {
            'remaining_days': 0,
            'active' : 1,
            'allow_cut' : _default_allow_cut,
              } 


     def holidays_refuse(self, cr, uid, ids, context=None):
        """
            Overwrite refuse funtion to check reasons for reject
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            if not holiday.reject_reason:
                raise osv.except_osv(_('Warning!'),_('Please enter reject reasons'))
        return super(hr_holidays, self).holidays_refuse(cr, uid, ids, context=context)


     def check_unpaid(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            if h.holiday_status_id.payroll_type == 'unpaied':
                  return True
            else:
                  return False

     def check_sick_leave(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            if h.holiday_status_id.sick_leave or  h.holiday_status_id.sick_day:
                  return True
            else:
                  return False

     def check_unit(self, cr, uid, ids, context=None):
            for h in self.browse(cr, uid, ids, context=context):
                dep = h.employee_id.department_id
                res = []
                if dep.parent_id:
                    cr.execute('SELECT hr_department_cat.category_type as type ' \
                        'FROM hr_department_cat ' \
                        'LEFT JOIN hr_department on (hr_department.cat_id=hr_department_cat.id)' \
                        'WHERE hr_department.id = %s', (dep.parent_id.id,))
                    res = cr.dictfetchall()
                if h.employee_id.department_id.cat_id.category_type == 'unit' or (res and res[0]['type'] == 'unit' and h.state != 'confirm') :
                    return True
                else:
                    return False
     def not_manger(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            check_unit_manager = self.check_unit_manager(cr, uid, ids, context)
            check_dep_manager = self.check_dep_manager(cr, uid, ids, context)
            check_general_dep_manager = self.check_general_dep_manager(cr, uid, ids, context)
            check_general_manager = self.check_general_manager(cr, uid, ids, context)

            if not check_unit_manager and not check_dep_manager and not check_general_dep_manager and not check_general_manager:
                return True
            else:
                return False

     def check_unit_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag = self.pool.get('res.users').has_group(cr, user_id, 'base.group_unit_manager')
            flag1 = self.pool.get('res.users').has_group(cr, user_id, 'base.group_department_manager')
            flag2 = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_general_department_manager')
            if flag and not flag1 and not flag2:
                  return True
            else:
                  return False

     def check_dep_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag1 = self.pool.get('res.users').has_group(cr, user_id, 'base.group_department_manager')
            flag2 = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_general_department_manager')
            flag3 = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_account_general_manager')
            if flag1 and not flag2 and not flag3:
                  return True
            else:
                  return False

     def check_general_dep_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_general_department_manager')
            flag1 = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_account_general_manager')
            if flag and not flag1:
                  return True
            else:
                  return False

     def check_general_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_account_general_manager')
            if flag:
                  return True
            else:
                  return False

     def dep_manager_user(self, cr, uid,ids, vals, context=None):
        cr.execute('SELECT res_users.id as user_id, res_users.login as login, hr_department.manager_id as manager_id, res_partner.email as email ' \
            'FROM public.res_users, public.hr_employee, public.resource_resource, public.hr_department, public.res_partner ' \
            'WHERE hr_department.manager_id = hr_employee.id '\
            'AND hr_employee.resource_id = resource_resource.id '\
            'AND resource_resource.user_id = res_users.id '\
            'AND res_users.partner_id = res_partner.id '\
            'AND hr_department.id = %s', (vals['department_id'][0],))
        res = cr.dictfetchall()
        if res and res[0].has_key('manager_id') and res[0]['manager_id']:
            cr.execute("update hr_holidays set manager_id=%s, email=%s where id=%s" , ( res[0]['manager_id'],res[0]['email'],ids[0]))
        
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]

        query = {'db': cr.dbname}
        fragment = {
            'login': res[0]['login'],
            'model': 'hr.holidays',
            'id': ids[0],
        }
        try:
            self.pool.get('hr.holidays').check_access_rule(cr, res[0]['user_id'], ids, 'read', context=context)
            url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
            cr.execute("update hr_holidays set url=%s where id=%s" , (url, ids[0]))
        except except_orm, e:
            cr.execute("update hr_holidays set url=NULL where id=%s" %(ids[0]))

        #cr.execute("update hr_attendance_record set manager_user_id=%s where id=%s" , (result['manager_user_id'],  rec.id))

        return res
     
     def manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id
            check_dep_manager = self.check_dep_manager(cr, uid, ids, context)
            check_general_dep_manager = self.check_general_dep_manager(cr, uid, ids, context)
            check_general_manager = self.check_general_manager(cr, uid, ids, context)

            if h.state == 'confirm':
                if dep_cat.category_type == 'section' or dep_cat.category_type == 'department' or dep_cat.category_type == 'general_dep' or dep_cat.category_type == 'unit':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                    if dep_cat.category_type == 'section' and mang_user_id and mang_user_id[0]['user_id'] != h.employee_id.user_id.id:
                        #if h.employee_id.department_id.manager_id.user_id.id == uid:
                        if not mang_user_id:
                            mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                        if mang_user_id and mang_user_id[0]['user_id'] == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                    elif dep_cat.category_type == 'section' and mang_user_id and mang_user_id[0]['user_id'] == h.employee_id.user_id.id:
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                        if mang_user_id and mang_user_id[0]['user_id'] == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                    else:
                        if not mang_user_id:
                            mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                        if mang_user_id and mang_user_id[0]['user_id'] == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))

            if h.state == 'unit_manag' or h.state == 'cut':
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                    if not mang_user_id:
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.parent_id.id,h.employee_id.department_id.parent_id.parent_id)})
                    if mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                        return False

                if dep_cat.category_type == 'department' or dep_cat.category_type == 'general_dep' or dep_cat.category_type == 'unit':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                    if not mang_user_id:
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                    if mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                        return False 

            if h.state == 'dep_manag' or h.state == 'approve_cut':
                parent_dep = h.employee_id.department_id.parent_id
                if dep_cat.category_type == 'section':
                    mang_user_id = parent_dep and parent_dep.parent_id and self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.parent_id.id,parent_dep.parent_id)}) or {}
                    if parent_dep and parent_dep.parent_id and mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

                if dep_cat.category_type == 'department':
                    mang_user_id = parent_dep and self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.id,parent_dep)}) or {}
                    if parent_dep and mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

                if dep_cat.category_type == 'general_dep':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)}) 
                    if mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

            if h.state == 'validate':
                
                if not check_dep_manager and not check_general_dep_manager and not check_general_manager:
                    if dep_cat.category_type == 'section' or dep_cat.category_type == 'department' or dep_cat.category_type == 'general_dep' or dep_cat.category_type == 'unit':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)}) or {}
                        if dep_cat.category_type == 'section' and mang_user_id and mang_user_id[0]['user_id'] != h.employee_id.user_id.id:
                            if not mang_user_id:
                                mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                            if mang_user_id and mang_user_id[0]['user_id'] == uid:
                                return True
                            else:
                                raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                        elif dep_cat.category_type == 'section' and mang_user_id and mang_user_id[0]['user_id'] == h.employee_id.user_id.id:
                            mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                            if mang_user_id and mang_user_id[0]['user_id'] == uid:
                                return True
                            else:
                                raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                        else:
                            if not mang_user_id:
                                mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                            if mang_user_id and mang_user_id[0]['user_id'] == uid:
                                return True
                            else:
                                raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))

                if check_dep_manager and not check_general_dep_manager and not check_general_manager:
                    if dep_cat.category_type == 'department':
                        mang_user_id = parent_dep and self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.id,parent_dep)}) or {}
                        if parent_dep and mang_user_id and mang_user_id[0]['user_id'] == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                            return False
                    if dep_cat.category_type == 'general_dep':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)}) or {}
                        if mang_user_id and mang_user_id[0]['user_id'] == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                            return False

                if check_general_dep_manager and not check_general_manager:
                    if self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_account_general_manager'):
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee manager'))
                        return False

                if check_general_manager:
                    if self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_general_hr_manager'):
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not HR employee'))
                        return False


        return True

     def create(self, cr, uid, vals, context=None):
        """
        Mehtod that creates holiday name by adding the date to it.

        @param vals: Dictionary contains the enterred values
        @return: Super create Mehtod
        """
        holiday_pool = self.pool.get('hr.holidays.status')
        status_rec = holiday_pool.browse(cr, uid, vals['holiday_status_id'], context=context)
        if status_rec.sick_leave:
            flag5 = self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_user')
            if not flag5:
                raise osv.except_osv(_('Warning!'),_('Any holiday request related to the Sick Leave can only be through HR'))
        return super(hr_holidays, self).create(cr, uid, vals, context=context)

     def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        user_group_obj = self.pool.get('res.groups.users.rel')
        flag = self.pool.get('res.users').has_group(cr, uid, 'base.group_unit_manager')
        flag1 = self.pool.get('res.users').has_group(cr, uid, 'base.group_department_manager')
        flag2 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_general_department_manager')
        flag3 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_general_hr_manager')
        flag4 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_account_general_manager')
        flag5 = self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_user')
        rec = self.browse(cr, uid, ids[0], context=context)
        cat = rec.employee_id.department_id.cat_id.category_type
        if not rec.holiday_status_id.sick_leave:
            if rec.state != 'draft' and rec.employee_id.user_id.id == uid and not flag and not flag1 and not flag2 and not flag3 and not flag5 and not flag4:
                 raise osv.except_osv(_('Warning!'),_('You can not write in this document'))
            if rec.state not in ('draft','confirm','validate') and flag and not flag1 and not flag2 and not flag3 and not flag5 and not flag4:
                 raise osv.except_osv(_('Warning!'),_('You can not write in this document'))
            if rec.state not in ('draft','confirm','unit_manag','validate','cut') and flag1 and cat and not flag2 and not flag3 and not flag5 and not flag4:
                 raise osv.except_osv(_('Warning!'),_('You can not write in this document'))
            if rec.state not in ('draft','confirm','unit_manag','dep_manag','validate','cut','approve_cut') and flag2 and not flag3 and not flag5 and not flag4:
                 raise osv.except_osv(_('Warning!'),_('You can not write in this document'))
            '''if rec.state not in ('draft','confirm','unit_manag','dep_manag','validate','cut','approve_cut','general_dep','general_dep_cut') and flag3 and not flag5 and not flag4:
                 raise osv.except_osv(_('Warning!'),_('You can not write in this document'))
            if rec.state in ('validate','hr_finance2','done_cut','hr_finance2_cut') and flag4 and not flag5:
                 raise osv.except_osv(_('Warning!'),_('You can not write in this document'))'''
        else:
            if not flag5:
                raise osv.except_osv(_('Warning!'),_('Any update related to the Sick Leave can only be through HR'))
        
        if vals.has_key('state'):
            super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
            result = self.check_manager_email(cr,uid,ids,context)
            return True
        else: 
            return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)

     def check_manager_email(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        user_group_obj = self.pool.get('res.groups.users.rel')
        mail_template_id = data_obj.get_object_reference(cr, uid,'hr_ntc_custom', 'email_hr_holidays')

        
        context = context or {}
        context['action'] = 'hr_holidays_custom.menu_permission'

        force_send = True
        group = False
        for h in self.browse(cr, uid, ids, context=context):
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id
            check_dep_manager = self.check_dep_manager(cr, uid, ids, context)
            check_general_dep_manager = self.check_general_dep_manager(cr, uid, ids, context)
            check_general_manager = self.check_general_manager(cr, uid, ids, context)
            
            if h.state == 'confirm':
                if not check_dep_manager and not check_general_dep_manager and not check_general_manager:
                    if dep_cat.category_type == 'section' or dep_cat.category_type == 'department' or dep_cat.category_type == 'general_dep' or dep_cat.category_type == 'unit':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                        if dep_cat.category_type == 'section' and mang_user_id and mang_user_id[0]['user_id']  != h.employee_id.user_id.id:
                            if h.holiday_status_id.permission:
                                send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                        u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                            else:
                                template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                            return True
                            
                        elif dep_cat.category_type == 'section' and mang_user_id and mang_user_id[0]['user_id']  == h.employee_id.user_id.id:
                            mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                            if h.holiday_status_id.permission:
                                send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                        u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                            else:
                                template_obj.send_mail(cr, uid, mail_template_id[1], h.id ,force_send, context=context)
                            return True
                            
                        else:
                            if h.employee_id.department_id.manager_id:
                                if h.holiday_status_id.permission:
                                    send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                                    u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                                else:
                                    template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send, context=context)
                                return True

                if check_dep_manager and not check_general_dep_manager and not check_general_manager:
                    if dep_cat.category_type == 'department':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.id,parent_dep)})
                        if parent_dep and mang_user_id and mang_user_id[0]['manager_id']:
                            if h.holiday_status_id.permission:
                                send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                                u'هناك سجل طلب إذن في انتظار تصدسق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                            else:
                                template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send, context=context)
                            return True
                        
                    if dep_cat.category_type == 'general_dep':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                        if mang_user_id and mang_user_id[0]['manager_id']:
                            if h.holiday_status_id.permission:
                                send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                                u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                            else:
                                template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send, context=context)
                            return True

                if check_general_dep_manager and not check_general_manager:
                    if dep_cat.category_type == 'department':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.id,parent_dep)})
                        if mang_user_id and mang_user_id[0]['manager_id']:
                            if h.holiday_status_id.permission:
                                send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                                u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                            else:
                                template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send, context=context)
                            return True

                    if dep_cat.category_type == 'general_dep':
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                        if mang_user_id and mang_user_id[0]['manager_id']:
                            if h.holiday_status_id.permission:
                                send_mail(self, cr, uid, ids[0],group ,u'تصديق إذن'.encode('utf-8'), 
                                u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                            else:
                                template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send,  context=context)
                            return True
                    
                if check_general_manager:
                    if h.holiday_status_id.permission:
                        send_mail(self, cr, uid, ids[0], 'base.group_hr_user',u'تصديق إذن'.encode('utf-8'), 
                                            u'هناك سجل طلب إذن في انتظار تصديق المدير المباشر'.encode('utf-8'), context=context)
                    else:
                        group_id = data_obj.get_object_reference(cr, uid,'base', 'group_hr_user')
                        cr.execute('SELECT g.uid as user_id ' \
                                'FROM public.res_groups_users_rel g ' \
                                'WHERE g.gid = %s', (group_id[1],) )
                        user_group_ids = cr.dictfetchall()
                        user_ids = [x['user_id'] for x in user_group_ids]
                        if user_ids:
                            user_ids.append(0)
                            cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                                'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                                'WHERE hr_employee.resource_id = resource_resource.id '\
                                'AND resource_resource.user_id = res_users.id '\
                                'AND res_users.partner_id = res_partner.id '\
                                'AND res_users.id in %s', (tuple(user_ids),) )
                            res = cr.dictfetchall()
                            for r in res:
                                cr.execute("update hr_holidays set manager_id=%s, email=%s where id=%s" , ( r['emp_id'], r['email'], h.id))

                                base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
                                base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]

                                query = {'db': cr.dbname}
                                fragment = {
                                    'login': r['login'],
                                    'model': 'hr.holidays',
                                    'id': ids[0],
                                }
                                try:
                                    self.pool.get('hr.holidays').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                    url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                    cr.execute("update hr_holidays set url=%s where id=%s" , (url, ids[0]))
                                except except_orm, e:
                                    cr.execute("update hr_holidays set url=NULL where id=%s" %(ids[0]))

                                template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                            return True
                    

            if h.state == 'unit_manag' or h.state == 'cut':
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.parent_id.id,h.employee_id.department_id.parent_id)})
                    if mang_user_id and mang_user_id[0]['manager_id']:
                        template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send,  context=context)
                        return True

                if dep_cat.category_type == 'department' or dep_cat.category_type == 'general_dep' or dep_cat.category_type == 'unit':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                    if mang_user_id and mang_user_id[0]['manager_id']:
                        template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send, context=context)
                        return True

            if h.state == 'dep_manag' or h.state == 'approve_cut':
                parent_dep = h.employee_id.department_id.parent_id
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.parent_id.id,parent_dep.parent_id)})
                    if mang_user_id and mang_user_id[0]['manager_id'] :
                        template_obj.send_mail(cr, uid, mail_template_id[1],h.id, force_send, context=context)
                        return True

                if dep_cat.category_type == 'department':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(parent_dep.id,parent_dep)})
                    if mang_user_id and mang_user_id[0]['manager_id']:
                        template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True

                if dep_cat.category_type == 'general_dep':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':(h.employee_id.department_id.id,h.employee_id.department_id)})
                    if mang_user_id and mang_user_id[0]['manager_id']:
                        template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True


            if h.state == 'general_dep' or h.state == 'general_dep_cut' :
                group_id = data_obj.get_object_reference(cr, uid,'base_custom', 'group_general_hr_manager')
                cr.execute('SELECT g.uid as user_id ' \
                            'FROM public.res_groups_users_rel g ' \
                            'WHERE g.gid = %s', (group_id[1],) )
                user_group_ids = cr.dictfetchall()
                user_ids = [x['user_id'] for x in user_group_ids]
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            cr.execute("update hr_holidays set manager_id=%s, email=%s where id=%s" , ( r['emp_id'], r['email'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
                            base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.holidays',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.holidays').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_holidays set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_holidays set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True
            
            if h.state == 'hr_finance1' or h.state == 'hr_finance1_cut' :
                group_id = data_obj.get_object_reference(cr, uid,'base_custom', 'group_account_general_manager')
                cr.execute('SELECT g.uid as user_id ' \
                            'FROM public.res_groups_users_rel g ' \
                            'WHERE g.gid = %s', (group_id[1],) )
                user_group_ids = cr.dictfetchall()
                user_ids = [x['user_id'] for x in user_group_ids]
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            cr.execute("update hr_holidays set manager_id=%s, email=%s where id=%s" , ( r['emp_id'], r['email'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
                            base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.holidays',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.holidays').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_holidays set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_holidays set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True

            if h.state == 'hr_finance2' or h.state == 'hr_finance2_cut' :
                if h.holiday_status_id.permission:
                    send_mail(self, cr, uid, ids[0], 'base.group_hr_user',u'تصديق إذن'.encode('utf-8'), 
                                            u'هناك سجل طلب إذن في انتظار تنفيذ الموارد البشرية'.encode('utf-8'), context=context)
                else:
                    group_id = data_obj.get_object_reference(cr, uid,'base', 'group_hr_user')
                    cr.execute('SELECT g.uid as user_id ' \
                                'FROM public.res_groups_users_rel g ' \
                                'WHERE g.gid = %s', (group_id[1],) )
                    user_group_ids = cr.dictfetchall()
                    user_ids = [x['user_id'] for x in user_group_ids]
                    if user_ids:
                            user_ids.append(0)
                            cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                                'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                                'WHERE hr_employee.resource_id = resource_resource.id '\
                                'AND resource_resource.user_id = res_users.id '\
                                'AND res_users.partner_id = res_partner.id '\
                                'AND res_users.id in %s', (tuple(user_ids),) )
                            res = cr.dictfetchall()
                            for r in res:
                                cr.execute("update hr_holidays set manager_id=%s, email=%s where id=%s" , ( r['emp_id'], r['email'], h.id))
                                
                                base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
                                base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]

                                query = {'db': cr.dbname}
                                fragment = {
                                    'login': r['login'],
                                    'model': 'hr.holidays',
                                    'id': ids[0],
                                }
                                try:
                                    self.pool.get('hr.holidays').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                    url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                    cr.execute("update hr_holidays set url=%s where id=%s" , (url, ids[0]))
                                except except_orm, e:
                                    cr.execute("update hr_holidays set url=NULL where id=%s" %(ids[0]))

                                template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                            return True 
            
            if h.state == 'review' :
                group_id = data_obj.get_object_reference(cr, uid,'purchase_ntc', 'group_internal_auditor')
                cr.execute('SELECT g.uid as user_id ' \
                            'FROM public.res_groups_users_rel g ' \
                            'WHERE g.gid = %s', (group_id[1],) )
                user_group_ids = cr.dictfetchall()
                user_ids = [x['user_id'] for x in user_group_ids]
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            cr.execute("update hr_holidays set manager_id=%s, email=%s where id=%s" , ( r['emp_id'], r['email'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
                            base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.holidays',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.holidays').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_holidays set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_holidays set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True       


        return True

     def cut(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'cut'.

        @return: Boolean True
        """            
        for h in self.browse(cr, uid, ids, context=context):
            if not h.cut_postpone_date:
                raise osv.except_osv(_('Warning!'), _('You Must Enter Leave Cut Date.'))
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id
            check_dep_manager = self.check_dep_manager(cr, uid, ids, context)
            check_general_dep_manager = self.check_general_dep_manager(cr, uid, ids, context)
            check_general_manager = self.check_general_manager(cr, uid, ids, context)

            if not check_dep_manager and not check_general_dep_manager and not check_general_manager:
                return self.write(cr, uid, ids, {'state':'cut'}, context=context)
            if check_dep_manager and not check_general_dep_manager and not check_general_manager:
                return self.write(cr, uid, ids, {'state':'approve_cut'}, context=context)
            if check_general_dep_manager and not check_general_manager:
                return self.write(cr, uid, ids, {'state':'hr_finance1_cut'}, context=context)
            if check_general_manager:
                #return self.write(cr, uid, ids, {'state':'hr_finance2_cut'}, context=context)
                return self.write(cr, uid, ids, {'state':'general_dep_cut'}, context=context)
        return False
     

     def onchange_holiday(self, cr, uid, ids, holiday_id, employee_id, date_from=None, context=None):
        """
        Retrieve number of remaining days for employee in specific holiday as holiday number of days.

        @param holiday_id: Id of holiday
        @param emp_id: Id of employee
        @return: Dictionary of values 
        """
        advance_leave2 = False
        if not holiday_id or not employee_id :
            return {'value':{'number_of_days_temp': 0, 'advance_leave2':advance_leave2, 'remaining_days': 0, 
                                'allow_cut':False}}
         
        context={'employee_id':employee_id}
        holiday = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_id, context=context)
        
        allow_cut = False
        remaining_leaves = holiday.get_days(context.get('employee_id'), False)[holiday.id]['remaining_leaves']
        if holiday.advance_leave and remaining_leaves <= 0 and abs(remaining_leaves) <= holiday.advance_leave_days:
            advance_leave2 = True 
        if holiday.allow_cut:
            allow_cut = True
        return {'value':{'number_of_days_temp': remaining_leaves, 'advance_leave2': advance_leave2, 
                            'remaining_days': remaining_leaves, 'allow_cut': allow_cut}}

     def check_holidays(self, cr, uid, ids, context=None):
        """
        Constrain method that check the number of the requested holiday days is 
        greater than remaining days.
        @return: Boolean True or False
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            holiday_ids = self.search(cr, uid, [('employee_id', '=', holiday.employee_id.id),
                                    ('holiday_status_id', '=', holiday.holiday_status_id.id), 
                                    ('state', 'not in', ('draft', 'cancel','refuse'))], context=context)
            if holiday.holiday_status_id.leave_limit == 'once' and len(holiday_ids) > holiday.holiday_status_id.number_of_days:
                raise orm.except_orm(_('Warning!'), _('Leave Limit is Once and Already Taken'))
            if holiday.holiday_status_id.leave_limit == 'annual':
                context={'employee_id':holiday.employee_id.id}
                context['id'] = holiday.id
                holiday_details = self.pool.get('hr.holidays.status').browse(cr, uid, holiday.holiday_status_id.id, context=context)
                #remaining = holiday_details.remaining_leaves holiday.employee_id.id
                remaining = holiday_details.get_days(holiday.employee_id.id, False)[holiday_details.id]['remaining_leaves']
                advance_days = holiday_details.advance_leave_days
                check = advance_days - abs(remaining) - holiday.number_of_days_temp
                check2 = abs(remaining) - holiday.number_of_days_temp
                if (not holiday.holiday_status_id.limit and not holiday.advance_leave) and check2 < 0 :
                    raise orm.except_orm(_('Warning!'), _('You cannot validate leaves for employee %s: too few remaining days (%s).') % (holiday.employee_id.name, remaining))
                if (not holiday.holiday_status_id.limit) and holiday.advance_leave and remaining < advance_days and check < 0 :
                    raise orm.except_orm(_('Warning!'), _('You cannot validate in advance leaves for employee %s: too few remaining days (%s).') % (holiday.employee_id.name, advance_days-abs(remaining)))
                 
        return True

     def _check_date(self, cr, uid, ids):
        """
        Constrain method that check  if 2 leaves that overlaps on same day
        @return: Boolean True or False
        """  
        for holiday in self.browse(cr, uid, ids):
            holiday_ids = self.search(cr, uid, [('date_from', '<=', holiday.date_to), 
                                     ('date_to', '>=', holiday.date_from), ('employee_id', '=', holiday.employee_id.id),
                                     ('id', '!=', holiday.id),('state','!=','refuse')])
            if holiday_ids:
                return False
        return True

     def _cut_postpone_date_check(self, cr, uid, ids):
        """
        Constrain method that check  if The start date anterior to the Postpone date
        @return: Boolean True or False
        """                
        for holiday in self.browse(cr, uid, ids):
            if (holiday.postpone  or  holiday.state == 'postpone') and holiday.cut_postpone_date < holiday.date_from:
                raise orm.except_orm(_('Warning!'), _('The start date must be anterior to the Postpone date.'))
            if not holiday.postpone  and  holiday.state in ('draft','cut','approve_cut','done_cut') and holiday.cut_postpone_date > holiday.date_to:
                raise orm.except_orm(_('Warning!'), _('The leave cut date must be anterior to the end date.'))
        return True

     def _check_alternative(self, cr, uid, ids, context=None):
        """
        Constrain method that check if the holiday takes an alternative employee and 
        if so it checks if it has been entered or not.

        @return: Boolean True or False
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.alternative_emp:
                if not holiday.holiday_status_id.sick_leave:
                    check_unit_manager = self.check_unit_manager(cr, uid, ids, context)
                    check_dep_manager = self.check_dep_manager(cr, uid, ids, context)
                    check_general_dep_manager = self.check_general_dep_manager(cr, uid, ids, context)
                    check_general_manager = self.check_general_manager(cr, uid, ids, context)
                    check_unit = self.check_unit(cr, uid, ids, context)
                    check_unpaid = self.check_unpaid(cr, uid, ids, context)

                    cat_id = holiday.employee_id.department_id.cat_id.category_type
                    flag = holiday.state == 'unit_manag' and cat_id == 'section' and not check_unit_manager
                    flag1 = holiday.state == 'dep_manag' and cat_id == 'section' and  check_unit_manager and not check_unit
                    flag2 = holiday.state == 'general_dep' and cat_id == 'unit' and not check_unpaid and not check_general_dep_manager
                    flag3 = holiday.state == 'hr_finance1' and cat_id == 'unit' and check_unpaid and not check_general_dep_manager
                    flag4 = holiday.state == 'general_dep' and cat_id == 'department' and not check_unpaid and check_dep_manager
                    flag5 = holiday.state == 'hr_finance1' and cat_id == 'department' and check_unpaid and check_dep_manager
                    flag6 = holiday.state == 'hr_finance1' and check_general_dep_manager
                    flag7 = holiday.state == 'hr_finance2' and check_general_manager
                    if holiday.state not in ['draft','confirm']:
                        if flag or flag1 or flag2 or flag3 or flag4 or flag5 or flag6 or flag7:
                            if not holiday.alternative_employee or (holiday.alternative_employee and holiday.alternative_employee.id == holiday.employee_id.id):
                                return False
                else:
                    if not holiday.alternative_employee or (holiday.alternative_employee and holiday.alternative_employee.id == holiday.employee_id.id):
                        return False
                    
        return True
     def _check_min(self, cr, uid, ids, context=None):
        """
        Constrain method that check if the holiday days is meeting the minimum 
        no of days or not.

        @return: Boolean True or False
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.min_days and holiday.holiday_status_id.min_days > holiday.number_of_days_temp:
                return False
        return True
        
     def _check_hours(self, cr, uid, ids, context=None):
        """
        Constraint method that check if the holiday hours is in the range or not.

        @return: Boolean True or False
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.number_hour < holiday.number_hours:
                raise osv.except_osv(_('Error!'), _('The number of hours is greater than the number of actual hours.'))
        return True

     def onchange_date_from(self, cr, uid, ids, date_from, date_to, days_no, field, context=None):
        """
        Retrieves number of remaining days for employee in specific holiday as holiday number of days and end date.

        @param date_to: End date
        @param date_from: Start date
        @param days_no: Number of days
        @param field: Changed field
        @return: Dictionary of values 
        """
        # Use days_no is not None instead of days_no != False because Zero is False but not None
        if date_from and (' ' not in date_from):
            date_from = date_from + ' ' + '00:00:00'

        if date_to and (' ' not in date_to):
            date_to = date_to + ' ' + '00:00:00'
        vals = {}
        dt_from = date_from and datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT)
        dt_to = date_to and datetime.datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)
        if field == 'date_from':
            if dt_from and days_no is not None:
                vals.update({'date_to':str(dt_from + datetime.timedelta(days_no - 1))})
            elif dt_from and dt_to:
                vals.update({'number_of_days_temp':round(self._get_number_of_days(date_from, date_to) + 1)})
        if field == 'date_to':
            if dt_from and dt_to:
                vals.update({'number_of_days_temp':round(self._get_number_of_days(date_from, date_to) + 1)})
            elif days_no is not None and dt_to:
                vals.update({'date_from':str(dt_to - datetime.timedelta(days_no - 1))})
        if field == 'days':
            if dt_from and days_no is not None:
                vals.update({'date_to':str(dt_from + datetime.timedelta(days_no - 1))})
            elif days_no is not None and dt_to:
                vals.update({'date_from':str(dt_to - datetime.timedelta(days_no - 1))})
        return {'value':vals}

     def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days and number of hours.
        """
        res = super(hr_holidays, self).onchange_date_to(cr, uid, ids, date_to, date_from)
        if date_from and date_to:
            date_from = mx.DateTime.Parser.DateTimeFromString(date_from )
            date_to = mx.DateTime.Parser.DateTimeFromString(date_to )
            hours = (date_to - date_from).hours
            res['value'].update({'number_hours': hours})
        return res

     def onchange_number_hours(self, cr, uid, ids, date_from, number_hours ):
        """
        Update the date_to.
        """
        vals = {}
        if date_from and number_hours:
            date_from = mx.DateTime.Parser.DateTimeFromString(date_from)
            date_to = date_from + datetime.timedelta(hours= number_hours)
            #date_to = mx.DateTime.Parser.DateTimeFromString(date_to )
            #hours = (date_to - date_from).hours
            date_to =  date_to.strftime("%Y-%m-%d %H:%M:%S")
            vals.update({'date_to': date_to})
        return {'value':vals}

     _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', []),
        (_cut_postpone_date_check, '', []),
        (check_holidays, '', []),
        (_check_alternative, 'Error ! You must select alternative employee for this leave.', []),
        (_check_min, 'Error ! The days you enter is less than minimum no of days.', []),
        (_check_hours, '', []),
     ]

     def holidays_confirm(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        '''for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id and record.employee_id.parent_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)'''
        return self.write(cr, uid, ids, {'state': 'confirm'})
