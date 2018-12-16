# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import datetime
from openerp.osv import osv , fields
from tools.translate import _
import openerp.addons.decimal_precision as dp
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


#----------------------------------------
#mission category
#----------------------------------------

tansport_type = [
    ('1', 'Internal transport'),
    ('2', 'Train'),
    ('3', 'Plane'),
    ('4', 'Bus'),
    ('5', 'Taxi'),
    ('6', 'Other'),
]

mission_state = [
    ('draft', 'Draft'),
    ('completed','Completed'),
    ('confirmed', 'Confirmed'),
    ('validated','Validated'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class mission_category(osv.osv):
    
    _name = "hr.mission.category"

    _description = "Mission Category"

    _columns = {
        'name': fields.char("Mission Category", size=200 , required=True),
        'code': fields.char('Code', size=64),
        'allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance'),
        'mission_account_id':fields.property('account.account', type='many2one', relation='account.account',
                                             string="Mission Account", method=True, view_load=True,
                                             domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
        'fees_account_id': fields.property('account.account', type='many2one', relation='account.account',
                                          string="Fees Account", method=True, view_load=True,
                                        domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
        'fees_currency_id':fields.many2one('res.currency', 'Fees Currency'),        
		'journal_id':  fields.property('account.journal', type='many2one', relation='account.journal',
                                       string="Journal", method=True, view_load=True,
                                       domain="[('type','=','purchase'),('special','=',False)]"),
        'account_analytic_id': fields.property('account.analytic.account', type='many2one',relation='account.analytic.account',
                                                domain="[('type','=','normal')]", string="Analytic Account", method=True, view_load=True),
        'destination':fields.char("Destination name",size=200),
        'company_id' : fields.many2one('res.company', 'Company'),
#         'currency':fields.many2one('res.currency', 'Currency'),
        'parent_id': fields.many2one('hr.mission.category', 'Mission Parent', domain="[('type','=','view')]"),
        'type': fields.selection([('view', 'view'), ('normal', 'Normal')], 'Type'),
        'limit':fields.integer('Limit'),
        'limit_exceed':fields.boolean('Allow Limit Exceeding'),
        'validate':fields.boolean('Double Validation'),
    }

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'you can not create same name !')
    ]

    _defaults = {
        'type' : 'normal',
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        This method prevent to delete record if it has parent
        return super & raise exception
        """
        mission_id = self.search(cr, uid, [('parent_id', 'in', ids)], context=context)
        if mission_id:
            raise osv.except_osv(_('Warning!'),_('You cannot delete this mission category because it is parent to another mission category'))
        return super(mission_category, self).unlink(cr, uid, ids, context)

    def copy(self, cr, uid, id, default=None, context=None):
        """
        This method prevent to duplicate record if it has parent
        return super & raise exception
        """
        default = {} if default is None else default.copy()
        mission = self.browse(cr, uid, id, context=context)
        default.update({'name':mission.name+"(copy)"})
        return super(mission_category, self).copy(cr, uid, id, default, context=context)
#----------------------------------------
# employee missions
#----------------------------------------
class employee_mission(osv.osv):

    _name = "hr.employee.mission"

    _description = "Employee Mission"

#TODO: end_date > start date constraints
#FIXME: when days change dates doesn't change
    _columns = {
        'name' :fields.char('Name', size=64 , readonly=True),
        'company_id' : fields.many2one('res.company', 'Company' , required=True , readonly=True),
        'mission_id': fields.many2one('hr.mission.category', "Destination", required=True),
	    'department_id':fields.many2one('hr.department', "Department",  required=True),           
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date", required=True),
        'mission_fee': fields.float("Mission Fee", digits_compute=dp.get_precision('Payroll')),
        'notes': fields.text("Comments"),
        'transport': fields.selection(tansport_type, "Transport Type"),
        'travel_path': fields.text("Travel Path"),
        'days': fields.integer('Number of Days'),
        'mission_line':fields.one2many('hr.employee.mission.line', 'emp_mission_id', "mission"),
        'state': fields.selection(mission_state, 'State', readonly=True),
        #'voucher_number' :fields.char('Accounting Number', size=64 , readonly=True),
        'voucher_number' :fields.many2one('account.voucher','Accounting Number', size=64 ),
        'percentage':fields.integer('Percentage(%)'),
        'validate': fields.related('mission_id', 'validate', type='boolean', relation='hr.mission.category', string='Apply Double Validation'),
    }

    _defaults = {
            'state': 'draft',
            'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee.mission', context=c),
            'name': '/',
    }

    _sql_constraints = [('Date_check',"CHECK (end_date>=start_date and days>=0.0 )",_("Start date must be before end date!")),
                        #('Fee_check_nagtive',"CHECK (mission_fee>=0.0)",_("Fee amount must be greater than Zero!"))
    ]
    def _check_limit(self, cr, uid, ids, context=None):
        for m in self.browse(cr, uid, ids, context=context):
            if m.state != 'draft' and not m.mission_id.limit_exceed and m.days > m.mission_id.limit:
                raise osv.except_osv(_('Error!'), _('You can not exceed the maximum days number for this mission'))
                return False
        return True

    _constraints = [
        (_check_limit, ' ', []),
    ]

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the mission by adding its sequence to the name.

        @param vals: Values that have been entered
        @return: super create method
        """
        if vals.get('mission_id'):
            mission = self.pool.get('hr.mission.category').browse(cr, uid, vals.get('mission_id'), context=context)
            vals.update({'name': mission.name + '/' + self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.mission')})
        return super(employee_mission, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Method thats overwrite the write method and updates the mission name by adding its sequence to the it.

        @param vals: Values that have been entered
        @return: Supper copy Method 
        """
        if vals.get('mission_id'):
            mission = self.pool.get('hr.mission.category').browse(cr, uid, vals.get('mission_id'), context=context)
            emp_mission = self.browse(cr, uid, ids, context=context)[0]
            vals.update({'name': mission.name + '/' + emp_mission.name.split('/',1)[1]})
        return super(employee_mission, self).write(cr, uid, ids, vals, context=context)

    def _get_number_of_days(self, start_date, end_date):
        """
        Returns a float equals to the timedelta between two dates given as string.

        @param start_date: Mission Start date
        @param end_date: Mission End date
        @return: Float that represents the days between two dates 
        """ 
        start_date = start_date + ' ' + '00:00:00'
        end_date = end_date + ' ' + '00:00:00'
        timedelta = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        return  (timedelta.days + float(timedelta.seconds) / 86400)+1

    def onchange_time_from(self, cr, uid, ids, start_date, end_date):
        """
        Onchange method to return the number of days between to dates when change start_date or end_date.

        @param start_date: Mission Start date
        @param end_date: Mission End date
        @return: dictionary contain the days
        """
        result = {}
        if end_date and start_date:
            result['value'] = {
                'days': self._get_number_of_days(end_date, start_date)
            }
        return result

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete an employee mission which is in %s state.')%(rec.state))
        return super(employee_mission, self).unlink(cr, uid, ids, context)

    def mission_approved(self, cr, uid, ids, context=None):
        """
        Workflow method change record state to 'approved' and 
        Transfer Mission amount to voucher

        @return: Boolean True
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        account_period_obj = self.pool.get('account.period')
        for mission in self.browse(cr, uid, ids, context=context):
            mission_amount = 0.0
            stamp = 0.0
            for emp_mission_amount in mission.mission_line:
                mission_amount += emp_mission_amount.mission_amounts
                stamp += emp_mission_amount.stamp
            if mission.mission_id.mission_account_id and mission.mission_id.journal_id and mission.mission_id.account_analytic_id:
                date = time.strftime('%Y-%m-%d')
                period = account_period_obj.find(cr, uid, dt=date, context={'company_id':mission.company_id.id})[0]
                voucher_dict = {
                    'company_id':mission.company_id.id,
                    'journal_id':mission.mission_id.journal_id.id,
                    'account_id':mission.mission_id.mission_account_id.id,
                    'period_id': period,
                    'name': mission.name + ' - ' + mission.start_date,
                    'amount':mission_amount-stamp,
                    'type':'purchase',
                    'date': date,
                    'reference':'HR/Mission/' + mission.name + ' - ' + mission.start_date,
 					'department_id': mission.department_id.id,
					'currency': mission.mission_id.fees_currency_id.id,
               }
                voucher = voucher_obj.create(cr, uid, voucher_dict, context=context)
                voucher_line_dict = {
                     'voucher_id':voucher,
                     'account_id':mission.mission_id.mission_account_id.id,
                     'account_analytic_id':mission.mission_id.account_analytic_id.id,
                     'amount':mission_amount,
                     'type':'dr',
                }
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                if stamp:
                    if mission.company_id.stamp_account_id.id:
                        fees_voucher_line = {
                            'voucher_id':voucher,
                            'account_id':mission.company_id.stamp_account_id.id,
                            'amount':-stamp,
                            'type':'dr',
                        }
                        voucher_line_obj.create(cr, uid, fees_voucher_line, context=context)
                    else:
                        raise osv.except_osv(_('Error!'),_("Please enter stamp account in HR settings"))
                vouch = voucher_obj.browse(cr, uid, voucher, context=context)
                return self.write(cr, uid, ids, {'state':'approved', 'voucher_number': vouch.number, })
            else:
                raise osv.except_osv(_('Error!'),_("Please enter mission accounting details"))
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)

    def recalcuate_days(self, cr, uid, ids, context=None):
        """
        Recalculate amount of mission if number of days changed.

        @return: True
        """
        employee_mission_line_obj = self.pool.get('hr.employee.mission.line')
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.mission_line:
                new_amount = employee_mission_line_obj.onchange_days(cr, uid, ids, line.days, line.employee_id.id, rec.mission_id.id)
                employee_mission_line_obj.write(cr, uid, [line.id], new_amount['value'], context=context)
        return True

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        this method duplicate record and update the lines by make it without values
        return super and duplicate record 
        """
        default.update({'mission_line': False})
        return super(employee_mission, self).copy(cr, uid, ids, default=default, context=context)


#----------------------------------------
# Mission Line
#----------------------------------------
class employee_mission_line(osv.osv):

    _name = "hr.employee.mission.line"

    _description = "Employee Mission Line"

    _rec_name = "emp_mission_id"

#TODO: update name_get & name search for employee to search by name & code
    _columns = {
        'emp_mission_id': fields.many2one('hr.employee.mission', "Mission", required=True, ondelete='cascade'),
        'employee_id' : fields.many2one('hr.employee', "Employee", required=True),
        'mission_amounts': fields.float("Mission Amount",digits_compute=dp.get_precision('Payroll'), required=True),
        #'mission_fees': fields.float("Mission Fee", digits_compute=dp.get_precision('Payroll')),
        'stamp': fields.float("Stamp", digits_compute=dp.get_precision('Payroll')),
        'days': fields.integer("Days"),
        'amount': fields.float("Amount", digits_compute=dp.get_precision('Payroll')),
        'start_date':fields.related('emp_mission_id', 'start_date', string='Start Date', type='date', 
                                    relation='hr.employee.mission', readonly=True, store=True),
        'end_date':fields.related('emp_mission_id', 'end_date', string='End Date', type='date', 
                                  relation='hr.employee.mission', readonly=True, store=True),
        'supervisor':fields.boolean('Supervisor'),
    }
    
    _defaults = {
        'employee_id': False, # To update employee_id domain by calling onchange_employee
    }

    _sql_constraints = [
       #('employee_mission_uniqe', 'unique (emp_mission_id,employee_id)', 'You can not enter the same employee!'),
       ('stamp_check_nagtive',"CHECK (stamp>=0.0)",_("Stamp amount should not be negative!"))
    ]

    def onchange_days(self, cr, uid, ids, days, employee_id, mission_id, context=None):
        """
        Compute missions amount for(Internal/External missions).
        
        @param days: integer no of days entered by user
        @param employee_id: ID of employee
        @param mission_id: ID of mission
        @return: Dictionary of mission amount to be updated
        """
        if not employee_id: 
            return {'value':{'mission_amounts':0,'amount':0}}
        payroll_obj = self.pool.get('payroll')
        mission_obj = self.pool.get('hr.mission.category')
        emp_obj = self.pool.get('hr.employee')
        allowance_id = mission_obj.browse(cr, uid, mission_id).allowance_id
        emp = emp_obj.browse(cr, uid, employee_id, context=context)
        date = time.strftime('%Y-%m-%d')
        total_payroll=payroll_obj.allowances_deductions_calculation(cr,uid,date,emp,{}, [allowance_id.id],False,[allowance_id.id])
        amount = total_payroll['total_allow'] * days
        emp_mission_dict = {
            'mission_amounts':amount,
            'amount':total_payroll['total_allow'],
            'stamp':allowance_id.stamp
        }
        return {'value': emp_mission_dict}

    def onchange_employee(self, cr, uid, ids, emp_id, days, mission_id, department_id, context=None):
        """
        Method returns the employee_type that missions is enabled for them.
        @param emp_id: ID of the employee
        @return: Dictionary contains the domain of the employee_type
        """
        #employee_type domain
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.mission_contractors
        employee = company_obj.mission_employee
        recruit = company_obj.mission_recruit
        trainee = company_obj.mission_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        employee_domain['employee_id'] += [('state', '=', 'approved'),('department_id','=',department_id)]
        domain = {'employee_id':employee_domain['employee_id']}
        res = self.onchange_days(cr, uid, ids, days, emp_id, mission_id, context=context)
        res.update({'domain': domain})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
