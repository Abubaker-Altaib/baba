# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################import datetime
import datetime
import time
from itertools import groupby
from operator import itemgetter
from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import mx
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta

#----------------------------------------
#holiday status(inherit)
#----------------------------------------
class  hr_holidays_status(osv.Model):
    """Inherits hr.holidays.status and add absence field 
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
        if context:
           curr_id = context.has_key('id') and context['id'] or []
        else:
           curr_id = []
        rec = self.browse(cr,uid,ids[0])

        if rec.permission:
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
        
            if not return_false:
                if record.id in grouped_lines:
                    if not (record.leave_limit == 'annual' and record.save_leave):
                        leaves_taken = sum([item['number_of_days_temp'] for item in grouped_lines[record.id]])
                        remaining_leave = all_leaves - leaves_taken
                        leaves_taken = max_leaves - remaining_leave
                    if remaining_leave > max_leaves:
                       remaining_leave = max_leaves
                       leaves_taken = 0

            print "------------------max_leaves leaves_taken", max_leaves, leaves_taken
            res[record.id] = {'max_leaves' : max_leaves, 'leaves_taken' : leaves_taken, 'remaining_leaves': max_leaves - leaves_taken}
        return res

    _columns = {
        #'scape_days': fields.float('Number Of Days To Create Scape'),
        #'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
        'sick_leave': fields.boolean('Sick Leave'),
        'advance_leave': fields.boolean('Allow Leave IN Advance'),
        'advance_leave_days': fields.integer('Leave IN Advance Days',size=64),
    }
    
    _defaults = {
        'advance_leave': 0,
        #'scape_days': 21,
        'sick_leave': 0,
        #'number_of_days': 3,
        #'absence':0,
        #'permission':0,
    }

    '''def create_sequence(self, cr, uid, vals, context=None):
        """ Create new no_gap entry sequence for every new holiday type
        """
        seq = {
            'name': vals['name'],
            'implementation':'no_gap',
            'padding': 4,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.pool.get('ir.sequence').create(cr, uid, seq)

    def create(self, cr, uid, vals, context=None):
        status_obj = self.pool.get('hr.holidays.status')
        if not 'sequence_id' in vals or not vals['sequence_id'] :
            # if we have the right to create a hr.holidays.status, we should be able to
            # create it's sequence.
            vals.update({'sequence_id': self.create_sequence(cr, SUPERUSER_ID, vals, context)})
        return super(hr_holidays_status, self).create(cr, uid, vals, context)'''

#----------------------------------------
#holiday(inherit)
#----------------------------------------

class hr_holidays(osv.osv):

    _inherit = "hr.holidays"

    
    def _sick_leave(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.sick_leave == True:
                result[holiday.id] = True
            else:
                result[holiday.id] = False
        return result


    def _advance_leave(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.advance_leave == True:
                result[holiday.id] = True
            else:
                result[holiday.id] = False
        return result

    def __compute_remaining(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for holiday in self.browse(cr, uid, ids, context=context):
            context['id'] = holiday.id
            holiday_details = self.pool.get('hr.holidays.status').browse(cr, uid, holiday.holiday_status_id.id, context=context)
            remaining = holiday_details.get_days(holiday.employee_id.id, False)[holiday_details.id]['remaining_leaves']
            remaining = remaining - holiday.number_of_days_temp
            res[holiday.id] = remaining
        return res

    _columns = {
        #'number_hours': fields.float('Numbers Of Hours'),
        'remaining_days': fields.function(__compute_remaining, Type='integer', string='Remaining Days', 
            store={
            'hr.holidays': (lambda self, cr,uid,ids,c: ids, ['state', 'holiday_status_id'], 10),
            }),
        'illness_id': fields.many2one("hr.employee.illness", "Medical Form"),
        'sick_leave': fields.function(_sick_leave, type="boolean", string='Sick Leave'),
        'advance_leave2': fields.function(_advance_leave, type="boolean", string='Advance Leave'),
        'advance_leave': fields.boolean('Leave IN Advance'),

        'type': fields.selection([('remove','Leave Request'),('add','Allocation Request'),('absence','Absence'),('escape','Escape')], 'Request Type', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help="Choose 'Leave Request' if someone wants to take an off-day. \nChoose 'Allocation Request' if you want to increase the number of leaves available for someone", select=True),
        'reference': fields.text('Reference'),
        #'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
        'company_id': fields.many2one('res.company','company'),
        'reference_num': fields.char('Reference Number'),
        'in_absence': fields.boolean('IN Absence'),
        'first_week': fields.boolean('Frist Week'),
        'second_week': fields.boolean('Second Week'),
        'sequence': fields.integer('Sequence'),
        'degree_id':fields.related('employee_id', 'degree_id', string='Degree', type='many2one', relation='hr.salary.degree', readonly=True, store=True),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=False,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'holiday_id': fields.many2one("hr.holidays", "Absence", required=False,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'action_state' : fields.selection([('done','Action Done'),('not_done','Action Not Done')], 'Procedure'),
        'action' : fields.text('Reference') ,
        'place_type' : fields.selection([('inside' , 'Inside') , ('outsite' , 'Outsite')] , string='Location Type') ,
        'holiday_place' : fields.char('Holiday Place') ,
        'source_place' : fields.char('Source') ,
        'road_days' : fields.integer('Road Days') ,
        'return_place' : fields.char('Return Place') ,
        
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False 
        if user.company_id:
            company = user.company_id.id

        return company

    

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
        for holiday in self.browse(cr, uid, ids):
            holiday_ids = self.search(cr, uid, [('date_from', '<=', holiday.date_to), 
                                                ('date_to', '>=', holiday.date_from), 
                                                ('employee_id', '=', holiday.employee_id.id), 
                                                ('id', '<>', holiday.id),('state','!=','refuse')])
            if holiday_ids:
                return False
        return True

    def _cut_postpone_date_check(self, cr, uid, ids):
        for holiday in self.browse(cr, uid, ids):
           if (holiday.postpone  or  holiday.state == 'postpone') and holiday.cut_postpone_date < holiday.date_from:
              raise orm.except_orm(_('Warning!'), _('The start date must be anterior to the Postpone date.'))
           if not holiday.postpone  and  holiday.state in ('cut','approve_cut','done_cut') and holiday.cut_postpone_date > holiday.date_to:
              raise orm.except_orm(_('Warning!'), _('The leave cut date must be anterior to the end date.'))
        return True

    def _check_alternative(self, cr, uid, ids, context=None):
        """
        Constrain method that check if the holiday takes an alternative employee and 
        if so it checks if it has been entered or not.

        @return: Boolean True or False
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.alternative_emp and not holiday.alternative_employee:
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

    _constraints = [
        (_check_date, _('You can not have 2 leaves that overlaps on same day!'), []),
        (_cut_postpone_date_check, '', []),
        (check_holidays, '', []),
        (_check_alternative, _('Error ! You must select alternative employee for this leave.'), []),
        (_check_min, _('Error ! The days you enter is less than minimum no of days.'), []),
    ]

    _defaults = {
        'type': 'remove',
        'company_id' : _default_company,
        'action_state' : 'not_done'
    }


    '''def create(self, cr, uid, vals, context=None):
        """
        Mehtod that creates holiday name by adding the date to it.

        @param vals: Dictionary contains the enterred values
        @return: Super create Mehtod
        """
        holiday_pool = self.pool.get('hr.holidays.status')
        new_name=""
        name = ""
        print "=-----------------context", context
        if 'default_type' in context and context['default_type'] == 'absence':
            status = holiday_pool.browse(cr, uid, vals['holiday_status_id'], context=context)
            name += status.name
            if status.sequence_id:
                #new_name = self.pool.get('ir.sequence').next_by_id(cr, uid, status.sequence_id.id, context)
                new_name = self.pool.get('ir.sequence').browse(cr, uid, status.sequence_id.id, context).number_next_actual
                print "-----------------newmnaaaame", new_name 
                vals['sequence'] = new_name
            else:
                raise orm.except_orm(_('Error'), _('No sequence defined in the Holidays Status !'))
        elif 'default_type' in context and context['default_type'] == 'escape':
            name += u'هروب'
            absence_rec = self.browse(cr, uid , vals['holiday_id'], context)
            vals['sequence'] = new_name = absence_rec.sequence and absence_rec.sequence or vals['sequence']
        else:
            pass
        date = vals.get('date_from') and  vals.get('date_from')
        vals['name'] = name + " " + str(new_name)
        return super(hr_holidays, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        holiday_obj = self.pool.get('hr.holidays.status')
        employee_obj = self.pool.get('hr.employee')
        for holiday in self.browse(cr, uid, ids, context=context):
            name = ""
            new_name = ""
            if holiday.type == 'absence':
                status = holiday_pool.browse(cr, uid, vals['holiday_status_id'], context=context)
                name += status.name
                if status.sequence_id:
                    #new_name = self.pool.get('ir.sequence').next_by_id(cr, uid, status.sequence_id.id, context)
                    new_name = self.pool.get('ir.sequence').browse(cr, uid, status.sequence_id.id, context).number_next_actual
                    print "-----------------newmnaaaame", new_name 
                    vals['sequence'] = new_name
                else:
                    raise orm.except_orm(_('Error'), _('No sequence defined in the Holidays Status !'))
            elif holiday.type == 'escape':
                name += u'هروب'
                absence_rec = self.browse(cr, uid , holiday.holiday_id.id, context)
                vals['sequence'] = new_name = absence_rec.sequence
            else:
            
            date = vals.get('date_from') and  vals.get('date_from') or holiday.date_from or ''
            vals['name'] = name + " " + new_name + " " + date
            holiday_write = super(hr_holidays, self).write(cr, uid, [holiday.id], vals)
            employee_update = employee_obj.write_employee_salary(cr, uid, [holiday.employee_id.id], [])
        return holiday_write'''

    
    '''def onchange_holiday_seq(self, cr, uid, ids, holiday_id, context={}):
        """
            Method that reflect sequence of absence 
            and change with absence changing
        """
        vals = {}
        if holiday_id:
            absence_rec = self.browse(cr, uid , holiday_id, context)
            vals['sequence'] = absence_rec.sequence
        return {'value': vals}'''


    def holidays_validate(self, cr, uid, ids, context=None):
        """
        Mehtod overwrites holidays_validate to create employee illness in case of sick leave .

        @return: boolean
        """
        illness_obj = self.pool.get('hr.employee.illness')
        hol = self.browse(cr, uid, ids, context=context)[0]
        super(hr_holidays, self).holidays_validate(cr, uid, ids, context=context)
        if hol.holiday_status_id.sick_leave:
            create_id = illness_obj.create(cr, uid, {'employee_id': hol.employee_id.id, 'date': hol.date_from,
                                        'end_date': hol.date_to, 'illness': hol.holiday_status_id.name,
                                        'holiday_id':hol.id},)
            self.write(cr,uid,[hol.id],{'illness_id':create_id})
        return True

    def holidays_refuse(self, cr, uid, ids, context=None):
        """
        Method overwrites holidays_refuse and delete related employee illness in case of sick leave.
        
        @return: boolean
        """
        illness_obj = self.pool.get('hr.employee.illness')

        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.holiday_status_id.sick_leave and holiday.illness_id:
                if holiday.illness_id.state != 'draft':
                    raise orm.except_orm(_('Error!'), _('You Can not Refuse Sick Leave Which has Medical Form not in Draft State'))
                else:
                    super(hr_holidays, self).holidays_refuse(cr, uid, ids, context=context)
                    illness_obj.unlink(cr, uid, [holiday.illness_id.id], context)
            else:
                super(hr_holidays, self).holidays_refuse(cr, uid, ids, context=context)
        
        return True



#----------------------------------------
#hr_holidays_absence
#----------------------------------------

class hr_holidays_absence(osv.osv):

    _name = "hr.holidays.absence"
    
    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'days_number': fields.integer('Days Number'),
        'employee_id': fields.many2one('hr.employee','Employee'),
        #'number_hours': fields.float('Numbers Of Hours'),
        'type': fields.selection([('absence','Absence'),('escape','Escape')], 'Request Type', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help="Choose 'Leave Request' if someone wants to take an off-day. \nChoose 'Allocation Request' if you want to increase the number of leaves available for someone", select=True),
        'reference': fields.text('Reference'),
        #'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
        'company_id': fields.many2one('res.company','company'),
        'reference_num': fields.char('Reference Number'),
        'in_absence': fields.boolean('IN Absence'),
        'first_week': fields.boolean('Frist Week'),
        'second_week': fields.boolean('Second Week'),
        'sequence': fields.integer('Sequence'),
        'degree_id': fields.many2one('hr.salary.degree', 'Degree'),
        #'degree_id':fields.related('employee_id', 'degree_id', string='Degree', type='many2one', relation='hr.salary.degree', readonly=True, store=True),
        'action_state' : fields.selection([('done','Action Done'),('not_done','Action Not Done')], 'Procedure'),
        'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('cancel','Canceled'),('done','Ended Escape')],'State'),
        'action' : fields.text('Reference') ,
        'absence': fields.many2one('hr.holidays.absence', 'Absence'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'deduction_id': fields.many2one('hr.allowance.deduction', 'Deduction'),
        'allow_deduct_except': fields.many2one('hr.allowance.deduction.exception', 'Deduction Exception'),
        'employee_suspend_archive_id': fields.many2one('hr2.basic.salary.suspend.archive', 'Suspend Archive'),
        'payroll_deduct': fields.float('Deduction Amount From Payroll'),
    }

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method to update sequence.

        @param vals: Values that have been entered
        @return: super create method
        """
        if 'type' in vals and vals['type'] == 'absence':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays.absence')
            vals.update({'sequence': int(sequence) })
        if 'employee_id' in vals:
            onchange_value = self.onchange_employee(cr, uid, [], vals['employee_id'],context)['value']
            vals.update({'degree_id': onchange_value['degree_id'] })
            vals.update({'department_id': onchange_value['department_id'] })
        return super(hr_holidays_absence, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Method thats overwrite the writr method to update degree and department.

        @param vals: Values that have been entered
        @return: super write method
        """
        #rec = self.browse(cr, uid, ids[0], context)
        for rec in self.browse(cr, uid, ids, context):
            if 'employee_id' in vals:
                onchange_value = self.onchange_employee(cr, uid, ids, vals['employee_id'],context)['value']
                vals.update({'degree_id': onchange_value['degree_id'] })
                vals.update({'department_id': onchange_value['department_id'] })
            if 'absence' in vals and rec.type == 'escape':
                absence_ids = self.search(cr, uid, [('absence','=',rec.id),('type','=','absence'),
                    ('state','!=','draft')], context)
                if absence_ids:
                    absence_rec = self.browse(cr, uid, absence_ids[0], context)
                    raise orm.except_orm(_('Error!'), _('You Can not Change Value Of Absence Field Of This Record,It has been created from Absence Record With Sequence:%s ')%(absence_rec.sequence))
                vals['sequence'] = self.browse(cr,uid, vals['absence'], context).sequence
        return super(hr_holidays_absence, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """
        Method thats overwrite the unlink method to make check.

        @param ids: Record ids
        @return: super unlink method
        """
        payroll_arch_obj = self.pool.get('hr.payroll.main.archive')
        allownce_arch_obj = self.pool.get('hr.allowance.deduction.archive')
        allow_exception_obj = self.pool.get('hr.allowance.deduction.exception')
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise orm.except_orm(_('Error!'), _('You Can not Delete Record not in Draft State'))
            elif rec.type == 'absence':
                if rec.absence and rec.absence.state != 'draft':
                    raise orm.except_orm(_('Error!'), _('You Can not Delete This Record,It has Escape Record not in Draft State'))
                if rec.allow_deduct_except:
                        to_dt = mx.DateTime.Parser.DateTimeFromString(rec.allow_deduct_except.end_date)
                        arch_ids = payroll_arch_obj.search(cr, uid, [('employee_id','=',rec.employee_id.id)
                            ('month','=',to_dt.month),('year','=',to_dt.year),('in_salary_sheet','=',True)])
                        if arch_ids:
                            allownce_arch_ids = allownce_arch_obj.search(cr ,uid, [('main_arch_id','in',arch_ids),
                                ('allow_deduct_id','=',rec.allow_deduct_except.allow_deduct_id.id)])
                            if not allownce_arch_ids:
                                allow_exception_obj.unlink(cr, uid, [rec.allow_deduct_except.id], context)
            elif rec.type == 'escape':
                if 'delete_from_absence' in context and context['delete_from_absence'] == True:
                    pass
                else:   
                    absence_ids = self.search(cr, uid, [('absence','=',rec.absence.id),('type','=','absence'),('state','!=','draft')], context)
                    if absence_ids:
                        absence_rec = self.browse(cr, uid, absence_ids[0], context)
                        raise orm.except_orm(_('Error!'), _('You Can not Delete This Record,It has been created from Absence Record With Sequence:%s ')%(absence_rec.sequence))
            else:
                pass    

        return super(hr_holidays_absence, self).unlink(cr, uid, ids, context=context)

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
        vals = {}
        dt_from = date_from and mx.DateTime.Parser.DateTimeFromString(date_from)
        dt_to = date_to and mx.DateTime.Parser.DateTimeFromString(date_to)
        if field == 'date_from':
            if dt_from and days_no != 0:
                vals.update({'date_to':str(dt_from + datetime.timedelta(days_no - 1))})
            elif dt_from and dt_to:
                vals.update({'days_number':round(self._get_number_of_days(date_from, date_to) + 1)})
        if field == 'date_to':
            if dt_from and dt_to:
                vals.update({'days_number':round(self._get_number_of_days(date_from, date_to) + 1)})
            elif days_no != 0 and dt_to:
                vals.update({'date_from':str(dt_to - datetime.timedelta(days_no - 1))})
        if field == 'days':
            if dt_from and days_no != 0:
                vals.update({'date_to':str(dt_from + datetime.timedelta(days_no - 1))})
            elif days_no != 0 and dt_to:
                vals.update({'date_from':str(dt_to - datetime.timedelta(days_no - 1))})
        return {'value':vals}


    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        from_dt = mx.DateTime.Parser.DateTimeFromString(date_from)
        to_dt = mx.DateTime.Parser.DateTimeFromString(date_to)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days
        return diff_day

    def create_escape(self, cr, uid, ids, context={}):
        """
        Method that create escape from absence
        """
        rec = self.browse(cr, uid, ids[0], context)
        #for rec in self.browse(cr, uid, ids):
        number_of_absence_escape_days = rec.employee_id.company_id.number_of_absence_escape_days
        days_number = rec.days_number
        date_to = rec.date_to
        if not rec.date_to:
            date_to = time.strftime('%Y-%m-%d')
            days_number = self._get_number_of_days(rec.date_from, date_to)
        if days_number >= number_of_absence_escape_days:
            vals = {
                'employee_id': rec.employee_id.id,
                'degree_id': rec.degree_id.id,
                'absence': rec.id,
                'company_id': rec.company_id.id,
                'sequence': rec.sequence,
                'date_from': rec.date_from,
                'date_to': date_to,
                'days_number': rec.days_number,
                'type': 'escape'

            }
            create_id = self.create(cr, uid, vals, context)
            self.write(cr, uid, [rec.id], {'absence': create_id}, context)

        return True

    def create_allowance_exception(self, cr, uid, ids, context={}):
        """
        Method that create allowance_deduction exception from absence
        """
        allow_exception_obj = self.pool.get('hr.allowance.deduction.exception')
        payroll_arch_obj = self.pool.get('hr.payroll.main.archive')
        rec = self.browse(cr, uid, ids[0], context)
        
        create_id = False
        number_of_absence_payroll_days = rec.employee_id.company_id.number_of_absence_payroll_days
        days_number = rec.days_number
        date_to = rec.date_to
        date = time.strftime('%Y-%m-%d')
        month = int(time.strftime('%m'))
        year = int(time.strftime('%Y'))
        
        if not rec.date_to:
            date_to = time.strftime('%Y-%m-%d')
            days_number = self._get_number_of_days(rec.date_from, date_to)
        if days_number >= number_of_absence_payroll_days:
            allow_dict = self.pool.get('payroll').allowances_deductions_calculation(cr,uid,date_to,rec.employee_id,{},[rec.deduction_id.id], False,[rec.deduction_id.id])
            print "------------------allow_dict", allow_dict
            amount = allow_dict['total_deduct'] * days_number
            arch_ids = payroll_arch_obj.search(cr, uid, [('employee_id','=',rec.employee_id.id),
                ('month','=',month),('year','=',year),('in_salary_sheet','=',True)])
            if not arch_ids:
                datetime_date_to = datetime.datetime(year,month,1) + relativedelta(months=1,days=-1)
            else:
                datetime_date_to = datetime.datetime(year,month,1) + relativedelta(months=2,days=-1)
            date_to = datetime.date(datetime_date_to.year,datetime_date_to.month,datetime_date_to.day).strftime('%Y-%m-%d')
                
            if not rec.allow_deduct_except:
                vals = {
                    'employee_id': rec.employee_id.id,
                    'types': 'deduct',
                    'absence': rec.id,
                    'company_id': rec.company_id.id,
                    'action': 'special',
                    'start_date': rec.date_from,
                    'end_date': date_to,
                    'allow_deduct_id': rec.deduction_id.id,
                    'amount': amount,

                }
                create_id = allow_exception_obj.create(cr, uid, vals, context)
                self.write(cr, uid, [rec.id], {'allow_deduct_except': create_id}, context)
            '''else:
                allow_exception_obj.write(cr, uid, [rec.allow_deduct_except.id], {'amount': amount}, context)'''

        return create_id

    def create_salary_suspend(self, cr, uid, ids, context={}):
        """
        Method that create salary suspend record from absence
        """
        suspend_obj = self.pool.get('emp.suspend')
        emp_obj = self.pool.get('hr.employee')
        suspend_archive_obj = self.pool.get('hr2.basic.salary.suspend.archive')
        rec = self.browse(cr, uid, ids[0], context)
        create_id = False
        date = time.strftime('%Y-%m-%d')
        ttype = 'resume' in context and 'resume' or 'suspend'
        sal_susp = ttype == 'suspend' and True or False 
        if not rec.employee_suspend_archive_id or ttype == 'resume':
            vals = {
                'employee_id': rec.employee_id.id,
                'suspend_type': ttype,
                'suspend_date':rec.date_to,
                #'company_id': rec.company_id.id,
                'comments': _('Escape'),
                'date': date,
            }
            create_id = suspend_archive_obj.create(cr, uid, vals, context)
            emp_obj.write(cr, uid, [rec.employee_id.id], {'salary_suspend':sal_susp}, context=context)
            self.write(cr, uid, [rec.id], {'employee_suspend_archive_id': create_id}, context)

        return create_id

    
    def confirm(self, cr, uid, ids, context={}):
        """
        Method that change state to confirmed
        """
        employee_termination_obj = self.pool.get('hr.employment.termination')
        for rec in self.browse(cr, uid, ids):
            print "--------------confirmrec",rec
            if not rec.date_to:
                raise orm.except_orm(_('Error!'), _('Please Enter Date To'))
            elif rec.type == 'absence':
                if not rec.absence:
                    self.create_escape(cr, uid, [rec.id], context)
                #if not rec.allow_deduct_except:
                    #raise orm.except_orm(_('Error!'), _('Please Enter Date To5'))
                #    self.create_allowance_exception(cr, uid, [rec.id], context)
            else:
                #raise orm.except_orm(_('Error!'), _('Please Enter Date To5'))
                if rec.type == 'escape':
                   reason_id=self.pool.get('hr.dismissal').search(cr, uid,[('escape','=',True)],limit=1,context=context)
                   if not reason_id:
                      raise orm.except_orm(_('Error!'), _('Please Create Escape End Reason'))
                   termination_id = employee_termination_obj.create(cr, uid, { 'employee_id': rec.employee_id.id,
                                                                        'dismissal_date': rec.date_to,
                                                                        'dismissal_type': reason_id[0],
                                                                        'state' : 'confirmed'})
                   self.pool.get('hr.employee').write(cr, uid, [rec.employee_id.id], {'end_date':  rec.date_to})
                   employee_termination_obj.do_terminate(cr, uid,[termination_id],context=context)
                if not rec.employee_suspend_archive_id:
                    self.create_salary_suspend(cr, uid, ids, context)
        return self.write(cr, uid, ids, {'state':'confirmed'}, context)

    def set_to_draft(self, cr, uid, ids, context={}):
        """
        Method that change state to draft
        """
        
        return self.write(cr, uid, ids, {'state':'draft'}, context)


    def end_escape(self, cr, uid, ids, context={}):
        """
        Method that change state to done
        """
        suspend_archive_obj = self.pool.get('hr2.basic.salary.suspend.archive')
        for rec in self.browse(cr, uid, ids):
            vals = {'state':'done'}
            if rec.type == 'escape':
                context['resume'] = True
                self.create_salary_suspend(cr, uid, ids, context)
                vals['employee_suspend_archive_id'] = False
        return self.write(cr, uid, ids, vals, context)

    def cancel(self, cr, uid, ids, context={}):
        """
        Method that change state to cancel
        """
        suspend_archive_obj = self.pool.get('hr2.basic.salary.suspend.archive')
        payroll_arch_obj = self.pool.get('hr.payroll.main.archive')
        allownce_arch_obj = self.pool.get('hr.allowance.deduction.archive')
        allow_exception_obj = self.pool.get('hr.allowance.deduction.exception')
        for rec in self.browse(cr, uid, ids):
            vals = {'state':'cancel'}
            if rec.type == 'absence':
                if rec.absence and rec.absence.state != 'draft':
                    raise orm.except_orm(_('Error!'), _('You Can not Refuse Absence Which has Escape not in Draft State'))
                    #self.create_escape(cr, uid, [rec.id], context)
                if rec.absence and rec.absence.state == 'draft':
                    context['delete_from_absence'] = True
                    self.unlink(cr, uid, [rec.absence.id], context)
                
                if rec.allow_deduct_except:
                    to_dt = mx.DateTime.Parser.DateTimeFromString(rec.allow_deduct_except.end_date)
                    arch_ids = payroll_arch_obj.search(cr, uid, [('employee_id','=',rec.employee_id.id),
                        ('month','=',to_dt.month),('year','=',to_dt.year),('in_salary_sheet','=',True)])
                    if arch_ids:
                        allownce_arch_ids = allownce_arch_obj.search(cr ,uid, [('main_arch_id','in',arch_ids),
                            ('allow_deduct_id','=',rec.allow_deduct_except.allow_deduct_id.id)])
                        if not allownce_arch_ids:
                            allow_exception_obj.unlink(cr, uid, [rec.allow_deduct_except.id], context)
                    else:
                        allow_exception_obj.unlink(cr, uid, [rec.allow_deduct_except.id], context)
                    #self.create_allowance_exception(cr, uid, [rec.id], context)
            else:
                if rec.employee_suspend_archive_id:
                    suspend_archive_obj.unlink(cr, uid, [rec.employee_suspend_archive_id.id], context)
                    context['resume'] = True
                    self.create_salary_suspend(cr, uid, ids, context)
                    vals['employee_suspend_archive_id'] = False
        return self.write(cr, uid, ids, vals, context)    

    def _default_company(self, cr, uid, context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company

    def onchange_employee(self, cr, uid, ids, employee_id, context={}):
        vals = {'degree_id': False, 'department_id': False}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr ,uid ,employee_id)
            degree = employee.degree_id.id
            department = employee.department_id.id 
            vals = {'degree_id': degree, 'department_id': department}
        return {'value': vals}


    def name_get(self, cr, uid, ids, context=None):
        key = 'Absence'
        if context and 'lang' in context:
            key = context['default_type'] == 'escape' and 'Escape' or key
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src','=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s %s(%s - %s)" % (item.employee_id.name, key , item.date_from, item.date_to or ' ')) for item in self.browse(cr, uid, ids, context=context)] or []


    def write_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        """Scheduler to check end date of holidays periodically 
        @return True
        """
        date = time.strftime('%Y-%m-%d')
        idss = self.search(cr, uid, [('date_to','=',False),('state','=','draft')], context=context)
        for rec in self.browse(cr, uid, idss):
            if rec.type == 'absence':
                self.create_escape(cr, uid, [rec.id], context)
                self.create_allowance_exception(cr, uid, [rec.id], context)
            else:
                self.create_salary_suspend(cr, uid, ids, context)
        
        return True

    def _check_date(self, cr, uid, ids):
        print "----------------------ids", ids
        for rec in self.browse(cr, uid, ids):
            print "rec.id------", rec.id
            holiday_ids = self.search(cr, uid, [('date_from', '<=', rec.date_to), 
                                                ('date_to', '>=', rec.date_from), 
                                                ('employee_id', '=', rec.employee_id.id), 
                                                ('id', '!=', rec.id),('state','!=','cancel'),
                                                ('type','=',rec.type)])
            print "----------holiday_ids",holiday_ids
            if holiday_ids:
                raise orm.except_orm(_('Validate Error!'), _('You can not have 2 absences that overlaps on same day!'))
                return False
        return True

    def _check_date_to(self, cr, uid, ids):
        for rec in self.browse(cr, uid, ids):
            if rec.date_to < rec.date_from:
                raise orm.except_orm(_('Validate Error!'), _('Date To Must Be After Date From'))
                return False
        return True

    _constraints = [
        (_check_date, (''), []),
        (_check_date_to, (''), []),
    ]
    
    _defaults = {
        'company_id': _default_company,
        'state': 'draft',
        'action_state' : 'not_done'
    }


#----------------------------------------
#hr_allowance_deduction(inherit)
#----------------------------------------

class hr_allowance_deduction(osv.osv):

    _inherit = "hr.allowance.deduction"
    
    _columns = {
        'absence_deduction': fields.boolean('Absence Deduction'),
    }

    _defaults = {
        'absence_deduction': 0,
    }


