# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import netsvc
import mx
from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations
from tools import DEFAULT_SERVER_DATE_FORMAT


#----------------------------------------
# Allowance & Deduction (Inherit)
#----------------------------------------
class hr_allowance_deduction(osv.Model):
    """ 
    Inherits hr.allowance.deduction an add new 3 fields to be used for the additional allowances
    """
    _inherit = "hr.allowance.deduction"

    _columns = {
        'week_factor': fields.float("Week Factor", digits_compute=dp.get_precision('Payroll')),
        'holiday_factor': fields.float("Holiday Factor", digits_compute=dp.get_precision('Payroll')),
        'days' : fields.boolean('Days'),
    }

    _defaults = {
        'week_factor': 1,
        'holiday_factor':1,
     }
    def _positive(self, cr, uid, ids, context=None):
        """
        constrain method to check value of week_factor,holiday_factor and max_hours more than zero
        return True or False
        """
        for fact in self.browse(cr, uid, ids, context=context):
            if fact.week_factor<0 or fact.holiday_factor<0 or fact.maximum<0 :
                return False
        return True 
    _constraints = [
        (_positive, 'The value  must be more than zero!', ['factors or maximum']),
    ]
#----------------------------------------
# Additional Allowance
#----------------------------------------
class hr_additional_allowance(osv.Model):

    _name = "hr.additional.allowance"
    _inherit = ['mail.thread']

    _description = 'additional Allowance'

    _rec_name = 'allowance_id'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=False),
        'department_id': fields.many2one('hr.department', 'Department', required=True , readonly=False, domain="[('company_id','=',company_id)]"),
        'allowance_id': fields.many2one('hr.allowance.deduction', 'Allowance', required=True, readonly=True,
                                       domain=[('allowance_type', '=', 'in_cycle'), ('in_salary_sheet', '=', False), ('name_type', '=', 'allow')],),
        'period_id': fields.many2one('account.period', 'Period', domain=[('special', '=', False)], readonly=False),
        'line_ids': fields.one2many('hr.additional.allowance.line', 'additional_allowance_id', "Employees", readonly=True, states={'draft':[('readonly', False)]}),
        'voucher_number': fields.many2one('account.voucher', 'Voucher Number', readonly=True),
         'work_need': fields.text("Work Need after working hours"),
        'work_resons': fields.text("Work Reasons after working hours "),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'),
                                   ('refuse', 'Refused'), ('validate', 'Waiting Second Approval'),
                                   ('second_validate', 'Waiting Third Approval'), ('approved', 'Approved'),
                                   ('cancel', 'Canceled')], 'State', readonly=True),
        'month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                   (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')],
                                    'Month'),
        'reasons' :fields.text("Reasons"),
        }
        
    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.additional.allowance', context=ctx),
        'period_id': lambda self, cr, uid, ctx: self.pool.get('account.period').find(cr, uid, context=dict(ctx or {}, account_period_prefer_normal=True))[0],
    }

    '''_sql_constraints = [
       ('department_allowance_period_uniqe', 'unique (department_id,allowance_id,period_id)', 'You can enter the same allowance in the same period to the same department more than once!'),
    ]'''
    def onchange_data(self, cr, uid, ids, line_ids ,period_id, allowance_id, department_id, month,field, context=None):
        """
        Method that retrieves the false value if additional_allowance_id selected.
        @return: Dictionary of value 
        """
        line_pool = self.pool.get('hr.additional.allowance.line')
        '''for line in line_ids:
            state=line[1] and line_pool.read(cr, uid, line[1], ['state'], context=context)['state'] or 'draft'
            if state=='draft':
                if field=='department_id':                     
                    line[0]=2
                else:
                    if not line[2] :
                        line[2]={}
                        line[0]=1
                    line[2].update({'period_id':period_id,'month':month,'allowance_id':allowance_id})
            else:
                line_ids.remove(line)
                line_pool.write(cr, uid, line[1], {'additional_allowance_id':False}, context=context)'''
        if field=='department_id' or field=='allowance_id' or field=='period_id' or field=='month':
            line_ids=[]
        if period_id and allowance_id and department_id and month:
            lines = line_pool.search(cr, uid, [('allowance_id', '=', allowance_id), ('period_id', '=', period_id),
                                               ('department_id', '=', department_id),('state', '=', 'confirm'),
                                               ('month', '=', month), 
                                               ('additional_allowance_id', '=', False)], context=context)
            for i in lines:
                line_ids.append([4,i,False]) 
        return {'value': {'line_ids': line_ids } }

    def onchange_company_id(self, cr, uid, ids, line_ids ,company_id,  context=None):
        """
        Method that retrieves the false value if for department_id 
        @return: Dictionary of false value 
        """           
        return {'value': {'department_id': False}}

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method that duplicats the defaults and set the period_id to False.
    
        @return: super copy method
        """
        default.update({'period_id': False , 'voucher_number':None})
        return super(hr_additional_allowance, self).copy(cr, uid, ids, default=default, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
        Workflow function that set the record to the draft state.

        @return: boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.additional.allowance', id, cr)
            wf_service.trg_create(uid, 'hr.additional.allowance', id, cr)
        return True

    def confirm(self, cr, uid, ids, context=None):
        """
        Workflow function that change the record to the 'confirm' state
        and set a constrain that the amount must be greater than zero.

        @return: boolean True
        """
        for r in self.browse(cr, uid, ids, context=context):
            if not r.line_ids:
                raise orm.except_orm(_('Warning'), _('The employees should be entered!'))
            for l in r.line_ids:
                if l.amounts_value <= 0:
                    raise orm.except_orm(_('Warning'), _('The final amount for employee should be greater than Zero; kindly check the red lines!'))
                if l.state == 'draft':
                    raise orm.except_orm(_('Warning'), _('The state of additional allowance details for employee should be in the confirm state!'))
                l.write({'state':'implement'}, context=context)
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        if not self.browse(cr, uid, ids, context=context)[0].reasons:
            raise osv.except_osv(_('Warning!'), _('Please Enter Reasons For Rejection'))
        self.write(cr, uid, ids, {'state':'cancel'}, context=context)
        return True

    def approved(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'approved' and 
        Transfer additional allowances amount to voucher

        @return: boolean True    
        """
        payroll_obj = self.pool.get('payroll')
        emp_obj = self.pool.get('hr.employee')
        for rec in self.browse(cr, uid, ids):
            employees_dic = {}
            total_amount = tax_amount = stamp_amount = 0.0
            for line in rec.line_ids:
                total_amount += line.gross_amount
                tax_amount += line.tax
                stamp_amount += line.imprint
                employees_dic[line.employee_id] = line.gross_amount

            lines = emp_obj.get_emp_analytic(cr, uid, employees_dic,  {'allow_deduct_id': rec.allowance_id.id})
            for line in lines:
                line['allow_deduct_id'] = rec.allowance_id.id
            reference = 'HR/Additional Allowance/' + rec.allowance_id.name + '  /  ' + rec.period_id.name + '  /  ' + rec.company_id.name
            narration = 'HR/Additional Allowance/' + rec.allowance_id.name + '  /  ' + '  /  ' + rec.company_id.name
            voucher = payroll_obj.create_payment(cr, uid, ids, {'reference':reference, 'lines':lines,
                                                                'tax_amount':tax_amount, 'stamp_amount':stamp_amount,
                                                                 'narration':narration,'department_id':rec.department_id.id,
                                                                 'model':'account.voucher'}, context=context)
            self.write(cr, uid, ids, {'state':'approved', 'voucher_number':voucher}, context=context)
        return True

    def create_lines(self, cr, uid, ids, context=None):
        """ 
        Method that recalculates the additional allowance lines amount

        @return: boolean True
        """
        line_pool = self.pool.get('hr.additional.allowance.line')
        for r in self.browse(cr, uid, ids, context=context):
            lines = line_pool.create(cr, uid, {'allowance_id': r.allowance_id.id,
                                                'period_id': r.period_id.id,
                                                'department_id': r.department_id.id,
                                                'state': 'draft','additional_allowance_id': r.id,
                                                'month':r.month}, context=context)
            
        return True


    def recompute_lines(self, cr, uid, ids, context=None):
        """ 
        Method that recalculates the additional allowance lines amount

        @return: boolean True
        """
        line_pool = self.pool.get('hr.additional.allowance.line')
        line_ids = line_pool.search(cr, uid, [('additional_allowance_id','in',ids)], context=context)
        return line_pool.write(cr, uid, line_ids, {}, context=context)

    def import_lines(self, cr, uid, ids, context=None):
        lines_pool = self.pool.get('hr.additional.allowance.line')
        for r in self.browse(cr, uid, ids, context=context):
            lines = lines_pool.search(cr, uid, [('allowance_id', '=', r.allowance_id.id),
                                                ('period_id', '=', r.period_id.id),
                                                ('department_id', '=', r.department_id.id),
                                                ('state', '=', 'confirm'),('additional_allowance_id', '=', False),
                                                ('month','=',r.month)], context=context)
            if lines:
                lines_pool.write(cr, uid, lines, {'additional_allowance_id':r.id}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        prevent deletion of employee additional allowance record if its not in draft state
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete an employee additional allowance which is in %s state.')%(rec.state))
        return super(hr_additional_allowance, self).unlink(cr, uid, ids, context)



#----------------------------------------
# Additional Allowance Line
#----------------------------------------
class hr_additional_allowance_line(osv.Model):

    _name = "hr.additional.allowance.line"

    _description = 'additional Allowance Line'

    def _calculate(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        Method that calculate the overtime hours, gross amount, tax, imprint and the net.

        @return: dictionary that contains amounts_hours,no_hours,tax,imprint,gross_amount,amounts_value
        """
       
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = {'amounts_hours': 0.0,
                            'no_hours': 0.0,
                            'tax': 0.0,
                            'imprint': 0.0,
                            'gross_amount': 0.0,
                            'amounts_value': 0.0,
            }
            if rec.additional_allowance_id and rec.employee_id:
                allow = rec.additional_allowance_id.allowance_id
                allow_dict= self.pool.get('payroll').allowances_deductions_calculation(cr,uid,rec.period_id.date_start,rec.employee_id,{'no_sp_rec':True},[allow.id])
                no_hours = rec.holiday_hours * allow.holiday_factor + rec.week_hours * allow.week_factor
                exceeding = False
                if not allow.days and allow.maximum and no_hours > allow.maximum and rec.allow_exceeding == False:
                    no_hours = allow.maximum
                    exceeding = True
                res = allow_dict.get('result',[])
                tax = res and round(res[0].get('tax',0) * no_hours ,2)
                gross = no_hours * (res and round(res[0].get('amount',0),2) or 0)
                result[rec.id] = {'amounts_hours': res and res[0].get('amount',0),
                                'no_hours': no_hours,
                                'tax': tax,
                                'imprint': res and res[0].get('imprint',0),
                                'gross_amount': gross,
                                'amounts_value': gross - tax - (res and res[0].get('imprint',0) or 0),
                                'exceed_max_hrs' : exceeding,
                }
        return result

    def _get_line_ids(self, cr, uid, ids, context=None, args=None):
        """
        Method that gets the id of additional allowance line.

        @return: list that contains additional_allowance_id
        """
        return self.pool.get('hr.additional.allowance.line').search(cr, uid, [('additional_allowance_id', 'in', ids)], context=context)

    _columns = {
        'additional_allowance_id': fields.many2one('hr.additional.allowance', "additional Allowance", ondelete='cascade'),
        'employee_id' : fields.many2one('hr.employee', "Employee"),
        'holiday_hours': fields.float("Holiday Hours/Days", digits_compute=dp.get_precision('Payroll')),
        'week_hours': fields.float("Working Hours/Days", digits_compute=dp.get_precision('Payroll')),
        'amounts_hours': fields.function(_calculate, string='Amount/Hours or Days', method=True,
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'no_hours': fields.function(_calculate, method=True, digits_compute=dp.get_precision('Payroll'),
                                    string='Total Hours/Days', store=True, multi='amount'),
        'tax': fields.function(_calculate, string='Taxes', method=True,
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'imprint':fields.function(_calculate, string='imprint', method=True,
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'gross_amount': fields.function(_calculate, string='Gross Amount', method=True,
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'amounts_value': fields.function(_calculate, string='Amount', method=True,
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'department_id': fields.many2one('hr.department', 'Department', domain="[('company_id','=',company_id)]"),
        'allowance_id': fields.many2one('hr.allowance.deduction', 'Allowance',
                                       domain=[('allowance_type', '=', 'in_cycle'), ('in_salary_sheet', '=', False), ('name_type', '=', 'allow')],),
        'period_id': fields.many2one('account.period', 'Period', domain=[('special', '=', False)]),
        'state': fields.selection([('draft', 'Draft'), ('complete', 'Complete'),
                                   ('confirm', 'Confirm'), ('implement', 'Implement'),
                                   ('cancel', 'Canceled')], 'State'),
        'allowance_detail_ids': fields.one2many('hr.additional.allowance.detail', 'allowance_line_id', "Detail"),
        'allow_exceeding' : fields.boolean('Allow Exceeding'),
        'exceed_max_hrs':fields.function(_calculate, method=True, type='boolean', string='Exceed Max Hours',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                   (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')],
                                    'Month'),
        
        
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.additional.allowance', context=ctx),
        'period_id': lambda self, cr, uid, ctx: self.pool.get('account.period').find(cr, uid, context=dict(ctx or {}, account_period_prefer_normal=True))[0],
    }

    _sql_constraints = [
       #('employee_uniqe', 'unique (employee_id,period_id)', 'You can not selected the same employee!'),
       ('employee_allowance_period_uniqe', 'unique (employee_id,allowance_id,period_id,month)', 'You can not give the employee same allowance in the same period more than once!'),
       #('amounts_value_check', 'check (amounts_value>0)', 'The final amount of employee additional allowance should be greater then Zero!')
    ]

    def copy_data(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method that duplicats the defaults and set the period_id and additional_allowance_id to False.
    
        @return: super copy method
        """
        
        default.update({'period_id': False, 'state':'draft'})
        return super(hr_additional_allowance_line, self).copy_data(cr, uid, ids, default=default, context=context)


    
    def onchange_department_id(self, cr, uid, ids ,department_id,  context=None):
        """
        onchange method make employee_id without value
        """
        return {'value': {'employee_id': False}}

    def onchange_allowance_id(self, cr, uid, ids ,allowance_id,  context=None):
        """
        onchange method make employee_id & department_id without value
        """        
        return {'value': {'employee_id': False,'department_id': False}}

    def onchange_allowance_id_2(self, cr, uid, ids ,department_id,  context=None):
        """
        onchange method make employee_id & department_id without value
        """        
        return {'value': {'employee_id': False,'department_id': department_id}}

    def onchange_period(self, cr, uid, ids, department_id ,allowance_id,  context=None):
        """
        Method that retrieves the false value if for department_id 
        @return: Dictionary of false value 
        """           
        return {'value': {'department_id': department_id,'allowance_id':allowance_id}}

    def onchange_period_2(self, cr, uid, ids, department_id ,allowance_id,month, context=None):
        """
        Method that retrieves the false value if for department_id 
        @return: Dictionary of false value 
        """
        return {'value': {'department_id': department_id,'allowance_id':allowance_id,'month':month}}


    def onchange_employee_id(self, cr, uid, ids, employee_id, allowance_id, context=None):
        """
        Check if the employee's degree allowed it to take the allowance or not.

        @param employee_id:  Id of the employee 
        @param allowance_id: Id of the allowance
        @return: dictionary if employee can take the allowance raise exception if not
        """
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            allow_ids = self.pool.get('hr.salary.allowance.deduction').search(cr, uid, [('allow_deduct_id', '=', allowance_id),
                                                                                    ('degree_id', '=', employee.degree_id.id)], context=context)
            if not allow_ids:
                raise orm.except_orm(_('ERROR'), _('The employee degree has no allowances amount'))
                return {'value': {'employee_id': False}}
            
            # Modify onchange_employee_id to check if employee categories in allowance categories  
            #allowance = self.pool.get('hr.allowance.deduction').browse(cr, uid, allowance_id, context=context)            
            #categories= allowance.category_ids            
            #cat_ids = self.pool.get('hr.employee').search(cr, uid, [('category_ids', 'in', [categ.id for categ in categories])], context=context)            
            #if  not cat_ids:
                #raise orm.except_orm(_('ERROR'), _('The employee categories not in allowances categories'))

        return {'value': {'holiday_hours': 0.0, 'week_hours': 0.0}}

    def onchange_hour(self, cr, uid, ids, detail_ids, employee_id,allowance_id, context=None):
        """
        Recalculate the holiday and working days hours.

        @param allowance_id: Id of the allowance
        @param employee_id:  Id of the employee 
        @return: dictionary contains holiday_hours and week_hours
        """
        context = context or {}
        detail_pool = self.pool.get('hr.additional.allowance.detail')
        allowance_pool=self.pool.get('hr.allowance.deduction')
        if not detail_ids:
            detail_ids = []
        res = {
            'week_hours': False,
            'holiday_hours': False,
        }
        days = allowance_id and allowance_pool.browse(cr, uid, allowance_id, context=context).days or False
        maximum = allowance_id and allowance_pool.browse(cr, uid, allowance_id, context=context).maximum or 0
        detail_ids = resolve_o2m_operations(cr, uid, detail_pool, detail_ids, ['hour', 'dayofweek', 'date'], context)
        emp_holiday_obj = self.pool.get('hr.holidays')
        emp_events_obj = self.pool.get('hr.public.events')
        holiday_hours = week_hours = 0.0
        for detail in detail_ids:
            detail_hour = detail.get('hour', 0.0)
            dayofweek = detail.get('dayofweek', 1)
            date = detail.get('date', False)
            flage = detail.get('flage')
            holiday = emp_holiday_obj.search(cr, uid, [('date_to', '>=', date), ('date_from', '<=', date),
                                                       ('employee_id', '=', employee_id), ('state', '=', 'validate')])
            if not holiday:
                holiday= emp_events_obj.search(cr, uid, ['|','&',('end_date', '>=', date),('start_date', '<=', date),('dayofweek', '=', dayofweek)])
            if flage:
                if days:
                    if detail_hour >= maximum:
                        holiday_hours += 1
                else:
                    holiday_hours += detail_hour
            else:
                if days:
                    if detail_hour >= maximum:
                        week_hours += 1
                else:
                    week_hours += detail_hour
        res.update({
            'week_hours': week_hours,
            'holiday_hours': holiday_hours,
        })
        return {
            'value': res
        }

    def unlink(self, cr, uid, ids, context=None):
        """
        method to prevent record deletion if its not in draft state
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete an employee overtime which is in %s state.')%(rec.state))
            #if rec.allowance_detail_ids:
                #raise osv.except_osv(_('Warning!'),_('You cannot delete an employee overtime which is have details'))
        return super(hr_additional_allowance_line, self).unlink(cr, uid, ids, context)

    def complete(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'complete'.

        @return: method that update state
        """
        return self.write(cr, uid, ids, {'state':'complete'}, context=context)

    def confirm(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'confirm'.

        @return: method that update state
        """
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def implement(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'implement'.

        @return: method that update state
        """
        return self.write(cr, uid, ids, {'state':'implement'}, context=context)

    def cancel(self, cr, uid, ids, context=None):
        """
        Workflow function that change the state to 'cancel'.

        @return: method that update state
        """
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        """
        Workflow function that set the record to the draft state.

        @return: boolean True
        """
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        additional_id = super(hr_additional_allowance_line, self).write(cr, uid, ids, vals, context=context)
        holiday_pool = self.pool.get('hr.holidays.status')
        for rec in self.browse(cr, uid, ids, context=context):
           if not rec.allowance_detail_ids:
                raise osv.except_osv(_('Warning!'),_('The additional allowance hours details must be entered for the employee %s.')%(rec.employee_id.name))
           if rec.allowance_detail_ids:
                print rec.allowance_detail_ids
                for line in rec.allowance_detail_ids:
                    date = mx.DateTime.Parser.DateTimeFromString(line.date)
                    if date.month != rec.month:
                        raise osv.except_osv(_('Warning!'),_('The Date of the additional allowance details must be at the  month of the overtime for the employee %s.')%(rec.employee_id.name))
        return additional_id


    '''_constraints = [
        (_check_date, 'The Date of the additional allowance details must be at the  month of the overtime!', []),
        (_check_allowance_details, 'The additional allowance hours details must be entered for each employee', []),
    ]'''

class hr_additional_allowance_detail(osv.Model):

    _name = "hr.additional.allowance.detail"

    _description = "Working days and the holiday days detailes"

    _columns = {
        'allowance_line_id' : fields.many2one("hr.additional.allowance.line", "Allowance Line", required=True,ondelete='cascade'),
        'dayofweek': fields.selection([(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'),
                                            (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], 'Day of Week', required=True),
        'date' : fields.date('Date', required=True),
        'hour' : fields.float("Hours", required=True),
        'flage': fields.boolean('Is holiday Day'),
    }
    _sql_constraints = [
       ('date_uniqe', 'unique (allowance_line_id,date)', 'You can not selected the same Date for the same employee!'),
       ('hour_check', 'check (hour>0 and hour <25 )', 'The number of hours should be between (1 - 24)!'),
    ]

    _defaults = {
        'flage' : False
    
    }
    def onchange_date(self, cr, uid, ids, date, context=None):
        """
        Return day of the week as number where monday is the first day

        @return: dictionary of the value to be updated 
        """
        if not date:
            return {}
        return {'value': {'dayofweek': datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).weekday()+1}}


class employees_salary_report(osv.osv_memory):
    _name = "employee.additional.report"

    def _get_period(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(cr,uid,context['active_id'])
        period_id = additional_rec.period_id.id
     
        return period_id

    def _get_month(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(cr,uid,context['active_id'])
        month = additional_rec.month
     
        return month

    _columns = {
        'period_id': fields.many2one('account.period', 'Period', domain=[('special', '=', False)]),
        'month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                           (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')],
                                            'Month'),
        }

    _defaults ={
        'month': _get_month,
        'period_id': _get_period,
        
    }

   


    def print_report(self, cr, uid, ids, context=None):
        datas = {}

        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(cr,uid,context['active_id'])

        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.additional.allowance',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'additional_wage',
            'datas': datas,
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
