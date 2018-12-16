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

#----------------------------------------
#holiday status(inherit)
#----------------------------------------
class hr_holidays_status(osv.osv):

    _inherit = "hr.holidays.status"

    def get_days(self, cr, uid, ids, employee_id, return_false, context=None):
        """
        Method Retrieves number of days, taken days and remain days for specific employee for each holiday.

        @return: Dictionary of values 
        """
        year = time.strftime('%Y')
        date = year + '-01-01'
        # if leave limit is annual and leave save is True add remaining days from past years based on number of save years 
        cr.execute("""SELECT h.id, h.number_of_days_temp, h.holiday_status_id 
                      FROM hr_holidays h left join hr_holidays_status s on s.id=h.holiday_status_id 
                      WHERE h.employee_id = %s AND h.state not in ('draft','cancel','refuse') AND 
                            h.holiday_status_id in %s and ((s.leave_limit='annual' and (h.date_from >= %s or
                            (s.save_leave = True and to_char(h.date_from,'YYYY') >= cast(%s - s.save_years as varchar(5)) ))) or 
                            s.leave_limit='once')""",
            [employee_id, tuple(ids), date, year])
        result = sorted(cr.dictfetchall(), key=lambda x: x['holiday_status_id'])
        grouped_lines = dict((k, [v for v in itr]) for k, itr in groupby(result, itemgetter('holiday_status_id')))
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            leaves_taken = 0
            max_leaves = record.number_of_days
            if record.leave_limit == 'annual' and record.save_leave:
                max_leaves += max_leaves * record.save_years
            if not return_false:
                if record.id in grouped_lines:
                    leaves_taken = sum([item['number_of_days_temp'] for item in grouped_lines[record.id]])
            res[record.id] = {'max_leaves' : max_leaves, 'leaves_taken' : leaves_taken, 'remaining_leaves': max_leaves - leaves_taken}
        return res

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            check_holiday = self.pool.get('hr.holidays').search(cr,uid,[('holiday_status_id','=',rec.id)])
            if check_holiday:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this holiday which is refrence in employees holidays.'))
        return super(hr_holidays_status, self).unlink(cr, uid, ids, context)

    _columns = {
        'set_holiday': fields.boolean('Default Leave', help="If its True then its be default when convert sick leave to holiday"),
        'female_only': fields.boolean('Female Only'),
        'number_of_days': fields.integer('Number of Days', required=True),
        'code': fields.char('Code', size=64),
        'religion': fields.selection([('muslim', 'Muslim'), ('christian', 'Christian'), ('others', 'Others')], 'Religion'),
        'category_ids': fields.many2many('hr.employee.category', 'leave_category_rel', 'leave_id', 'category_id', 'Categories'),
        'save_leave': fields.boolean('Allow Save Leave'),
        'save_years':fields.integer('Save Years', required=True),
        'min_days': fields.float('Minimum no of Days'),
        'annual_programming': fields.boolean('Subservient to Annual Programming'),
        'alternative_emp': fields.boolean('Requires an Alternative to The Employee'),
        'delivery_covenant': fields.boolean('Requires Delivery of Covenant'),
        'leave_certificate': fields.boolean('Requires Leave Certificate'),
        'leave_limit':fields.selection([('once', 'Once'), ('annual', 'Annual'), ], 'Leave Limit', required=True),
        'comments':fields.text("Comments"),
        'settlement': fields.boolean('Service Termination Settlement'),
    }

    _defaults = {
        'leave_limit': 'once',
        'save_years': 1,
        'number_of_days': 1,
        'double_validation': True
    }

    _sql_constraints = [
       ('code_uniqe', 'unique (code)', 'You Can Not Have Two Leave Type With The Same Code!'),
       ('no_of_days_check', 'CHECK (number_of_days > 0)', "The number of days should be greater than Zero!"),
       ('save_years_check', 'CHECK (save_years >= 0)', "The save years should be greater than or equal to Zero!"),
    ]

#----------------------------------------
#holiday(inherit)
#----------------------------------------

class hr_holidays(osv.osv):

    _inherit = "hr.holidays"

    def _compute(self, cr, uid, ids, arg, fields, context=None):
        """
        Mehtod returns the state as percentage to be used in the progress bar.

        @return: Dictionary of values 
        """
        res = {}
        progress = 0.0
        if not ids:
            return res
        for hol in self.browse(cr, uid, ids):
            if hol.state == 'confirm':
                progress = 25.0
            if hol.state == 'validate1':
                progress = 75.0
            if hol.state == 'validate':
                progress = 100.0
            if hol.state == 'done_cut':
                progress = 100.0
            if hol.state == 'refuse':
                progress = 0.0
            if hol.state == 'draft':
                progress = 0.0
            res[hol.id] = progress
        return res

    def holidays_validate(self, cr, uid, ids, context=None):
        """
        Mehtod overwrites holidays_validate and updates the remaining days of the employee's holiday.

        @return: the super of the method hr_holidays
        """
        hol = self.browse(cr, uid, ids, context=context)[0]
        status = self.pool.get('hr.holidays.status').browse(cr, uid, hol.holiday_status_id.id, context={'employee_id':hol.employee_id.id})
        self.write(cr, uid, ids, {'remaining_leaves':status.remaining_leaves})
        return super(hr_holidays, self).holidays_validate(cr, uid, ids, context=context)

    def check_holidays(self, cr, uid, ids, context=None):
        """
        Constrain method that check the number of the requested holiday days is 
        greater than remaining days.

        @return: Boolean True or False
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            holiday_ids = self.search(cr, uid, [('employee_id', '=', holiday.employee_id.id), ('holiday_status_id', '=', holiday.holiday_status_id.id), ('state', 'not in', ('draft', 'cancel','refuse'))], context=context)
            if holiday.holiday_status_id.leave_limit == 'once' and len(holiday_ids) > 1:
                raise orm.except_orm(_('Warning!'), _('Leave Limit is Once and Already Taken'))
            holiday_details = self.pool.get('hr.holidays.status').get_days(cr, uid, [holiday.holiday_status_id.id], holiday.employee_id.id, False, context=context)
            remaining = holiday_details.get(holiday.holiday_status_id.id, {}).get('remaining_leaves', 0)
            if holiday.holiday_status_id.leave_limit== 'annual' and remaining < 0:
                raise orm.except_orm(_('Warning!'), _('You cannot validate leaves for employee %s: too few remaining days (%s).') % (holiday.employee_id.name, remaining))
        return True

    def _check_date(self, cr, uid, ids):
        for holiday in self.browse(cr, uid, ids):
            holiday_ids = self.search(cr, uid, [('date_from', '<=', holiday.date_to), ('date_to', '>=', holiday.date_from), ('employee_id', '=', holiday.employee_id.id), ('id', '<>', holiday.id),('state','!=','refuse')])
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


    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft':[('readonly', False)], 'confirm':[('readonly', False)]}),
        'name': fields.char('Description', readonly=True , size=64),
        'emp_code': fields.related('employee_id', 'emp_code', type='char', relation='hr.employee', string='Employee Code', store=True , readonly=True),
        'alternative_employee': fields.many2one('hr.employee', "Alternative Employee"),
        'progress': fields.function(_compute, type='float', method=True, string='Progress'),
        'create_date': fields.datetime('Create Date', readonly=True),
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
            ('validate1', 'Second Approval'), ('validate', 'Approved'), ('cut', 'Cut Leave'), ('approve_cut', 'Approve Cut'), ('done_cut', 'Done Cut'),('postpone', 'Postpone')], 'State', readonly=True),
        'cut_postpone_date': fields.datetime('Cut/Postpone Date' , states={'draft':[('invisible', True)], 'confirm':[('invisible', True)], 'validate1':[('invisible', True)]}),
        'remaining_leaves': fields.float('Remaining Leaves'),
        'postpone' :fields.boolean('Postpone', readonly=True),
        'notes': fields.text('Reasons', states={'refuse':[('readonly',True)]}),
    }

    _defaults = {
        'employee_id': False, #To call onchange_employee
        'date_from': fields.datetime.now,
        'name': '/'
    }


    _sql_constraints = [
        ('date_check3', 'CHECK ((postpone = true AND date_from < cut_postpone_date) or postpone = False )', "The start date must be anterior to the Postpone date."),
        ('cut_postpone_date_check', "CHECK (postpone != true AND cut_postpone_date <= date_to AND state != 'postpone')", "The leave cut date must be anterior to the end date."),
        ('absence_date_check', 'unique (employee_id,holiday_status_id,date_to,date_from)', "you can not enterd absence date for employee which entered before."),
    ]
    
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
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from','date_to']),
        (_cut_postpone_date_check, 'The start date must be anterior to the Postpone date.', ['cut_postpone_date']),
        (check_holidays, _('holiday days must be greater than remaining days!'), ['number_of_days_temp']),
        (_check_alternative, 'Error ! You must select alternative employee for this leave.', ['alternative_employee']),
        (_check_min, 'Error ! The days you enter is less than minimum no of days.', ['number_of_days_temp']),
    ]

    def onchange_holiday(self, cr, uid, ids, holiday_id, employee_id, date_from, context=None):
        """
        Retrieve number of remaining days for employee in specific holiday as holiday number of days.

        @param holiday_id: Id of holiday
        @param emp_id: Id of employee
        @return: Dictionary of values 
        """
        if not holiday_id:
            return {'value':{'number_of_days_temp': 0}}
        holiday = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_id, context=context)
        domain = [('id', 'not in', ids),
                  ('employee_id', '=', employee_id),
                  ('holiday_status_id', '=', holiday_id),
                  ('state', 'not in', ('draft', 'cancel','refuse'))]
        total_days = holiday.number_of_days
        if holiday.save_leave and holiday.leave_limit == 'annual':
            total_days += total_days * holiday.save_years
            if date_from:
                year = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S').year - holiday.save_years
                domain += [('date_from', '>=', datetime.date(year, 1, 1).strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        holiday_ids = self.search(cr, uid, domain, context=context)
        if holiday.leave_limit == 'once' and holiday_ids:
            raise orm.except_orm(_('Warning!'), _('This employee already took %s holiday before, holiday with once leave limit should take only once!.') % (holiday.name,))
        taken_days = sum([holidays.number_of_days_temp for holidays in self.browse(cr, uid, holiday_ids, context=context)])
        return {'value':{'number_of_days_temp': total_days - taken_days}}

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

    def create(self, cr, uid, vals, context=None):
        """
        Mehtod that creates holiday name by adding the date to it.

        @param vals: Dictionary contains the enterred values
        @return: Super create Mehtod
        """
        holiday_pool = self.pool.get('hr.holidays.status')
        vals['name'] = holiday_pool.browse(cr, uid, vals['holiday_status_id'], context=context).name + " " + (vals['date_from'] or '')
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
            name = vals.get('holiday_status_id') and holiday_obj.browse(cr, uid, vals['holiday_status_id'], context=context).name or \
                        holiday.holiday_status_id.name
            date = vals.get('date_from') and  vals.get('date_from') or holiday.date_from or ''
            vals['name'] = name + " " + date
            holiday_write = super(hr_holidays, self).write(cr, uid, [holiday.id], vals)
            employee_update = employee_obj.write_employee_salary(cr, uid, [holiday.employee_id.id], [])
        return holiday_write

    def write_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
       """Scheduler to check end date of holidays periodically 
       @return True
       """
       date = time.strftime('%Y-%m-%d')
       cr.execute("select date from hr_employee_salary_addendum where date=(select max(date) from hr_employee_salary_addendum where type = 'salary') and type ='salary'")
       prev_salary_date = cr.fetchone()
       domain=[]
       if prev_salary_date:
          domain += ['|','|', ('date_to','<=',date),('date_to','>=',date),('date_to','>',prev_salary_date[0])]
          domain += ['|','|',('date_from','>=',prev_salary_date[0]), ('date_from','<=',prev_salary_date[0]),('date_from','<=',date)]
          domain+= [('state','in',('validate','done_cut'))]
       else:
          domain+= [('date_to','>=',date)]
       emp_holidays_ids= self.search(cr,uid,domain)
       self.write(cr, uid, emp_holidays_ids, {})
       return True

    def onchange_employee(self, cr, uid, ids, emp_id, context=None):
        """
        Retrieve available holidays for specific employee based on his 
        information(degree,religion,marital status and category).

        @param emp_id: Id of employee
        @return: Dictionary of values 
        """
        domain = {}
        emp_obj = self.pool.get('hr.employee')
        if emp_id:
            emp = emp_obj.browse(cr, uid, emp_id, context=context)
            categories = emp.category_ids
            domain = {'holiday_status_id':[
               '&', '&', '|', ('degree_ids', '=', False), ('degree_ids', 'in', (emp.degree_id.id)),
               '|', ('category_ids', '=', False), ('category_ids', 'in', [categ.id for categ in categories]),
               '|' , ('religion', '=', False), ('religion', '=', (emp.religion))]}
            domain['holiday_status_id'].append(('absence', '!=', True))
            if emp.gender != 'female':
                domain['holiday_status_id'].append(('female_only', '=', False))
        else:
            domain = {'holiday_status_id':[('name', '=', '')]}
        #employee_type domain
        company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        contractors = company_obj.holiday_contractors
        employee = company_obj.holiday_employee
        recruit = company_obj.holiday_recruit
        trainee = company_obj.holiday_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        employee_domain['employee_id'].append(('state', '=','approved'))
        domain = {
            'holiday_status_id': domain['holiday_status_id'],
            'employee_id': employee_domain['employee_id'],
        }
        return {'value': {'holiday_status_id':False} , 'domain': domain}

    def cut(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'cut'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'cut'}, context=context)

    def approve_cut(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'approve_cut'.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'approve_cut'}, context=context)

    def done_cut(self, cr, uid, ids, context=None):
        """
        Workflow function that changes the state to 'done_cut' 
        and check if the cut date has been enterred then alters the holiday's date
        if not raises an exception and updates holiday's days and dates.
        
        @return: Boolean True
        """
        for holiday in self.browse(cr, uid, ids, context=context):
            if not holiday.cut_postpone_date:
                raise osv.except_osv(_('Warning!'), _('You Must Enter Leave Cut Date.'))
        res = self.onchange_date_from(cr, uid, ids, holiday.date_from, holiday.cut_postpone_date, False, 'date_to', context=context)
        return self.write(cr, uid, ids, {'state':'done_cut', 'date_to':holiday.cut_postpone_date,
                                         'number_of_days_temp':res['value']['number_of_days_temp']}, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.holidays', id, cr)
            wf_service.trg_create(uid, 'hr.holidays', id, cr)
        return True

    def approve_postpone(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'refuse' and postpone the holiday.

        @return: Boolean True        
        """
        self.write(cr, uid, ids, {'postpone': True,'state':'refuse'}, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        holiday = self.browse(cr, uid, id, context=context)
        if holiday.holiday_status_id.absence:
           raise osv.except_osv(_('Warning!'), _("You Cannot Duplicate Employee's Absence !"))
        else:
           raise osv.except_osv(_('Warning!'), _("You Cannot Duplicate Employee's Holiday !"))        
        return super(hr_holidays, self).copy(cr, uid, id, default=default, context=context)


#----------------------------------------
#public events
#----------------------------------------
class hr_public_events(osv.osv):

    _name = "hr.public.events"

    _description = "public events"

    def _get_number_of_days(self, cr, uid, ids, arg, fields, context=None):
        """
        Returns a float equals to the timedelta between two dates given as string.

        @param arg: other arguments
        @param fields: functional field to be updated
        @return: dictionary of values to be updated
        """
        res = {}
        for event in self.browse(cr, uid, ids, context=context):
            res[event.id] = 1
            if event.start_date and event.end_date:
                from_dt = datetime.datetime.strptime(event.start_date, DEFAULT_SERVER_DATE_FORMAT)
                to_dt = datetime.datetime.strptime(event.end_date, DEFAULT_SERVER_DATE_FORMAT)
                timedelta = to_dt - from_dt
                res[event.id] += timedelta.days + float(timedelta.seconds) / 86400
        return res

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'number_of_days': fields.function(_get_number_of_days, type='integer', method=True, string='Number of Days'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'dayofweek': fields.selection([(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], 'Day of Week'),
        'comment':fields.text("Comments"),
        'active': fields.boolean('Active'),
    }

    def check_number_of_days(self, cr, uid, ids, context=None):
        """
        Constrain method that checks if the event days greater the zero.

        @return: Boolean True or False
        """
        for event in self.browse(cr, uid, ids, context=context):
            if event.number_of_days < 1:
                return False
        return True

    _defaults = {
        'active':lambda *a:1,
    }

    _constraints = [
        (check_number_of_days, _('The number of event days should be greater than Zero!'), ['number_of_days']),
    ]

    def onchange_dayofweek(self, cr, uid, ids, dayofweek, context=None):
        """
        Retrieve available holidays for specific employee based on his information(degree,religion,marital status and category).

        @param dayofweek: Id of employee
        @return: Dictionary of values or An empty one
        """
        if dayofweek != False:
            self.write(cr, uid, ids, {'start_date': False, 'end_date': False, 'number_of_days': 1}, context=context)
            return  {'value':{'start_date': False, 'end_date': False, 'number_of_days': 1}}
        return {}

    def unlink(self, cr, uid, ids, context={}):
        raise osv.except_osv(_('ERROR'), _('you can not delete this record , instead make it inactive '))
        return True

    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'You Can Not Have Two public event With The Same name!'),
              ]

class hr_employee_delegation(osv.osv):

    """
    Inherets hr.employee.delegation and adds function to check employee holidays befor delegating him
    """

    _inherit = "hr.employee.delegation"

    def check_holidays(self, cr, uid, ids, context=None):
        """
        Checks if the employee has a holiday during the delegation period or not.

        @return: Boolean True or False
        """
        message = ''
        emp_holiday_obj = self.pool.get('hr.holidays')
        for r in self.browse(cr, uid, ids):
            holiday = emp_holiday_obj.search(cr, uid, [('date_to', '>=', r.start_date), ('date_from', '<=', r.end_date), ('employee_id', '=', r.employee_id.id), ('state', '=', 'validate')])
            if holiday:
                message = _('This employee in a holiday')
            if message:
                if not r.message:
                    cr.execute('update hr_employee_delegation set message=%s where id=%s', (message, r.id))
                return False
        return True

#----------------------------------------
#Hr dismissal (inherit)
#----------------------------------------
class hr_dismissal(osv.osv):

    """
    Inherets hr.dismissal and adds boolean field to set whether to close the holiday out with service termination or not
    """

    _inherit = "hr.dismissal"
    _columns = {

           'holiday_settlement' :fields.boolean('Holiday Settlement'),

               }

#----------------------------------------
#employment termination (inherit)
#----------------------------------------

class hr_employment_termination(osv.Model):

    """Inherits hr.employment.termination and overwrite calculates method to buy employee's remain hoidays.
    """

    _inherit = "hr.employment.termination"

    def calculation(self, cr, uid, ids, transfer , context=None):

        """Method that overwrite calculates method to buy employee's remain hoidays.
           @return: list
        """
        holiday = self.pool.get('hr.holidays')
        payroll = self.pool.get('payroll')
        holiday_status = self.pool.get('hr.holidays.status')
        termination_lines = self.pool.get('hr.employment.termination.lines')
        holiday = self.pool.get('hr.holidays')
        termination_ids=[]
        transfer = transfer==True and transfer or False
        termination_ids = super(hr_employment_termination, self).calculation(cr, uid, ids, transfer=False,context=context)
        for rec in self.browse(cr, uid, ids, context=context):  
            if rec.dismissal_type.holiday_settlement==True:
                holi_status_ids = holiday_status.search(cr, uid, [('settlement','=',True),('active','=',True),('buy_leave','=',True)])
                if  holi_status_ids:
                    for status in holiday_status.browse(cr, uid, holi_status_ids, context=context) :
                        days = holiday_status.get_days(cr, uid, [status.id], rec.employee_id.id, False, context=context).values()
                        allow_dict = payroll.allowances_deductions_calculation(cr,uid,rec.dismissal_date,rec.employee_id,{'no_sp_rec':True}, [status.buy_allowance_id.id], False,[])
                        amount = allow_dict['total_allow'] * days[0]['remaining_leaves']
                        termination_id = termination_lines.create(cr, uid, {  'account_id': status.buy_allowance_id.account_id.id,
                                                                             'termination_id': rec.id,
                                                                             'type': 'holiday',
                                                                             'amount': amount,
                                                                             'name': status.buy_allowance_id.name})
                        termination_ids.append(termination_id)
                        if transfer:
                             cr_holi_id = holiday.create(cr, uid,{ 'holiday_status_id' : status.id, 
                                                                   'date_from' : time.strftime('%Y-%m-%d'),
                                                                   'employee_id' : rec.employee_id.id,
                                                                   'amount' : amount,
                                                                   'state' : 'holiday_buying',
                                                                   'acc_number' : rec.acc_number,
                                                                   'buying_days' : days[0]['remaining_leaves'],
                                                                   'number_of_days_temp' : days[0]['remaining_leaves'],
                                                                   })
                             #print"=lllll rec.acc_number",rec.acc_number,rec.employee_id
                             wf_service = netsvc.LocalService("workflow")
                             wf_service.trg_validate(uid,'hr.holidays',cr_holi_id, 'paid', cr)
                             self.pool.get('hr.holidays').write(cr, uid, [cr_holi_id], {'state': 'paid'}, context=context)
        return  termination_ids

#----------------------------------------
class hr_employment_termination_lines(osv.Model):

    """
    Inherets hr.employment.termination.lines and add a new value to the selection field type.
    """

    _inherit = "hr.employment.termination.lines"

    _columns = {

         'type':fields.selection([('trm_allowance', 'Termination Allowance'), ('special', 'Special'), ('holiday', 'Holiday')], 'Type'),

            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

