# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import netsvc
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
        'max_hours' :fields.float("Maximum Hours", digits_compute=dp.get_precision('Payroll')),
    }

    _defaults = {
        'week_factor': 1,
        'holiday_factor':1,
     }
    def _positive(self, cr, uid, ids, context=None):
        for fact in self.browse(cr, uid, ids, context=context):
          if fact.week_factor<0 or fact.holiday_factor<0 or fact.max_hours<0 :
               return False
        return True 
    _constraints = [
        (_positive, 'The value  must be more than zero!', ['factors or max_hours']),
    ]
#----------------------------------------
# Additional Allowance
#----------------------------------------
class hr_additional_allowance(osv.Model):

    _name = "hr.additional.allowance"

    _description = 'additional Allowance'

    _rec_name = 'allowance_id'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=False),
        'department_id': fields.many2one('hr.department', 'Department', required=True , readonly=False, domain="[('company_id','=',company_id)]"),
        'allowance_id': fields.many2one('hr.allowance.deduction', 'Allowance', required=True, readonly=True,
                                       domain=[('allowance_type', '=', 'in_cycle'), ('in_salary_sheet', '=', False), ('name_type', '=', 'allow')],),
        'period_id': fields.many2one('account.period', 'Period', domain=[('special', '=', False)], readonly=False),
        'date': fields.date('Date', required= True,readonly= True,states={'draft':[('readonly',False)]},),
        'line_ids': fields.one2many('hr.additional.allowance.line', 'additional_allowance_id', "Employees", readonly=True, states={'draft':[('readonly', False)]}),
        'voucher_number': fields.many2one('account.voucher','Voucher Number',readonly=True),
         'work_need': fields.text("Work Need after working hours"),
        'work_resons': fields.text("Work Reasons after working hours "),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'),
                                   ('refuse', 'Refused'), ('validate', 'Waiting Second Approval'),
                                   ('second_validate', 'Waiting Third Approval'), ('approved', 'Approved'),
                                   ('cancel', 'Canceled')], 'State', readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True ,),
        'perpous': fields.char("Perpous"),
        'number': fields.char("Number", required=True),
        }
    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.additional.allowance', context=ctx),
        'period_id': lambda self, cr, uid, ctx: self.pool.get('account.period').find(cr, uid, context=dict(ctx or {}, account_period_prefer_normal=True))[0],
    }

    _sql_constraints = [
      # ('department_allowance_period_uniqe', 'unique (department_id,allowance_id,period_id)', 'You can enter the same allowance in the same period to the same department more than once!'),
       ('name_uniqe', 'unique (number)', 'you can not create same number!')
    ]

    def onchange_period_id(self, cr, uid, ids, line_ids ,period_id,  context=None):
        line_pool = self.pool.get('hr.additional.allowance.line')
        line_ids = line_pool.search(cr, uid, [('additional_allowance_id','in',ids),('allowance_detail_ids','<>',False),('department_id','<>',False)], context=context)
        if line_ids :
            for line in line_ids:
                overtime = line_pool.write(cr, uid, line, {'additional_allowance_id':False}, context=context)
        else :   
            lines_id = line_pool.search(cr, uid, [('additional_allowance_id','in',ids),('allowance_detail_ids','=',False)], context=context)
            if lines_id :
                for lines in lines_id:
                    change = line_pool.write(cr, uid, lines, {'state':'draft'}, context=context)
                delete = line_pool.unlink(cr, uid,lines_id ,context=context)
        return {'value': {'line_ids': False}}

    def onchange_allowance_id(self, cr, uid, ids, line_ids ,allowance_id,  context=None):
        line_pool = self.pool.get('hr.additional.allowance.line')
        line_ids = line_pool.search(cr, uid, [('additional_allowance_id','in',ids),('allowance_detail_ids','<>',False),('department_id','<>',False)], context=context)
        if line_ids :
            for line in line_ids:
                overtime = line_pool.write(cr, uid, line, {'additional_allowance_id':False}, context=context)
        else :   
            lines_id = line_pool.search(cr, uid, [('additional_allowance_id','in',ids),('allowance_detail_ids','=',False)], context=context)
            if lines_id :
                for lines in lines_id:
                    change = line_pool.write(cr, uid, lines, {'state':'draft'}, context=context)
                delete = line_pool.unlink(cr, uid,lines_id ,context=context)
        return {'value': {'line_ids': False}}

    def onchange_department_id(self, cr, uid, ids, line_ids ,department_id,  context=None):
        line_pool = self.pool.get('hr.additional.allowance.line')
        line_id = line_pool.search(cr, uid, [('additional_allowance_id','in',ids),('allowance_detail_ids','<>',False),('department_id','<>',False)], context=context)
        if line_id :
            for line in line_id:
                overtime = line_pool.write(cr, uid, line, {'additional_allowance_id':False}, context=context)
        else :   
            lines_id = line_pool.search(cr, uid, [('additional_allowance_id','in',ids),('allowance_detail_ids','=',False)], context=context)
            if lines_id :
                for lines in lines_id:
                    change = line_pool.write(cr, uid, lines, {'state':'draft'}, context=context)
                delete = line_pool.unlink(cr, uid,lines_id ,context=context)
        return {'value': {'line_ids': False}}

    def onchange_company_id(self, cr, uid, ids, line_ids ,company_id,  context=None):
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
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.voucher_number :
                    if rec.voucher_number.state == 'draft' :
                        self.pool.get('account.voucher').unlink(cr,uid,[rec.voucher_number.id])
                    elif rec.voucher_number.state == 'cancel' :
                        self.write(cr,uid,ids,{'voucher_number':False})
                    else : 
                        raise osv.except_osv(_('warning') , _('There is a voucher releted to this record, you must cancel it before set the record to draft'))
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
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)

    def approved(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'approved' and 
        Transfer additional allowances amount to voucher

        @return: boolean True    
        """
        if not context:
            context = {}
        payroll_obj = self.pool.get('payroll')
        for rec in self.browse(cr, uid, ids):
            employees_dic = {}
            total_amount = tax_amount = stamp_amount = 0.0
            for line in rec.line_ids:
                total_amount += line.gross_amount
                tax_amount += line.tax
                stamp_amount += line.imprint
                employees_dic[line.employee_id] = line.gross_amount

            lines = self.pool.get('hr.employee').get_emp_analytic(cr, uid, employees_dic,  {'allow_deduct_id': rec.allowance_id.id})
            reference = 'HR/Additional Allowance/' + rec.allowance_id.name + '  /  ' + rec.period_id.name + '  /  ' + rec.company_id.name
            narration = 'HR/Additional Allowance/' + rec.allowance_id.name + '  /  ' + '  /  ' + rec.company_id.name
            voucher = payroll_obj.create_payment(cr, uid, ids, {'reference':reference, 'lines':lines,
                                                                'tax_amount':tax_amount, 'stamp_amount':stamp_amount,
                                                                 'narration':narration,'department_id':rec.department_id.id,'salary_name' : '/',}, context=context)
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",voucher
            self.write(cr, uid, rec.id, {'state':'approved', 'voucher_number':voucher}, context=context)
        return True

    def recompute_lines(self, cr, uid, ids, context=None):
        """ 
        Method that recalculates the additional allowance lines amount

        @return: boolean True
        """
        line_pool = self.pool.get('hr.additional.allowance.line')
        line_ids = line_pool.search(cr, uid, [('additional_allowance_id','in',ids)], context=context)
        print">>>>>>>>>>line_ids>>>>>>>>>>>>",line_ids
        return line_pool.write(cr, uid, line_ids, {}, context=context)

    def import_lines(self, cr, uid, ids, context=None):
        lines_pool = self.pool.get('hr.additional.allowance.line')
        for r in self.browse(cr, uid, ids, context=context):
            lines = lines_pool.search(cr, uid, [('allowance_id', '=', r.allowance_id.id),
                                              ('period_id', '=', r.period_id.id),
                                              ('department_id', '=', r.department_id.id),
                                              ('state', '=', 'confirm')], context=context)
            if lines:
                lines_pool.write(cr, uid, lines, {'additional_allowance_id':r.id, 'state':'implement'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
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
            if rec.additional_allowance_id:
                allow = rec.additional_allowance_id.allowance_id
                allow_dict= self.pool.get('payroll').allowances_deductions_calculation(cr,uid,rec.period_id.date_start,rec.employee_id,{'no_sp_rec':True},[allow.id], False,[])
                no_hours = rec.holiday_hours * allow.holiday_factor + rec.week_hours * allow.week_factor
                if allow.max_hours and no_hours > allow.max_hours:
                    no_hours = allow.max_hours
                tax = allow_dict['result'][0]['tax'] * no_hours
                gross = no_hours * allow_dict['total_allow']
                result[rec.id] = {'amounts_hours': allow_dict['total_allow'],
                                'no_hours': no_hours,
                                'tax': tax,
                                'imprint': allow.stamp ,
                                'gross_amount': gross,
                                'amounts_value': gross - tax -allow.stamp
                }
            print">>>>>>>>>result>>>>>>>>>>>>>",result
        return result

    def _get_line_ids(self, cr, uid, ids, context=None, args=None):
        """
        Method that gets the id of additional allowance line.

        @return: list that contains additional_allowance_id
        """
        return self.pool.get('hr.additional.allowance.line').search(cr, uid, [('additional_allowance_id', 'in', ids)], context=context)

    _columns = {
        'additional_allowance_id': fields.many2one('hr.additional.allowance', "additional Allowance", ondelete='cascade'),
        'employee_id' : fields.many2one('hr.employee', "Employee", required=True),
        'holiday_hours': fields.float("Holiday Hours", digits_compute=dp.get_precision('Payroll')),
        'week_hours': fields.float("Working Hours", digits_compute=dp.get_precision('Payroll')),
        'amounts_hours': fields.function(_calculate, string='Amount/Hours', method=True,
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.additional.allowance': (_get_line_ids, ['allowance_id'], 10),
                                                'hr.additional.allowance.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'no_hours': fields.function(_calculate, method=True, digits_compute=dp.get_precision('Payroll'),
                                    string='Total Hours', store=True, multi='amount'),
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
        'date': fields.date('Date',),
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.additional.allowance', context=ctx),
        'period_id': lambda self, cr, uid, ctx: self.pool.get('account.period').find(cr, uid, context=dict(ctx or {}, account_period_prefer_normal=True))[0],
    }

    _sql_constraints = [
       ('employee_uniqe', 'unique (employee_id,period_id)', 'You can not selected the same employee!'),
       ('employee_allowance_period_uniqe', 'unique (employee_id,allowance_id,period_id)', 'You can not give the employee same allowance in the same period more than once!'),
       #('amounts_value_check', 'check (amounts_value>0)', 'The final amount of employee additional allowance should be greater then Zero!')
    ]

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method that duplicats the defaults and set the period_id and additional_allowance_id to False.
    
        @return: super copy method
        """
        default.update({'period_id': False, 'additional_allowance_id':False})
        return super(hr_additional_allowance_line, self).copy(cr, uid, ids, default=default, context=context)


    def create(self, cr, uid, vals, context=None):
        if '__copy_data_seen' in context:
            vals.update({'period_id':False})
        print">>>>>>>>>result222>>>>>>>>>>>>>",vals
        return super(hr_additional_allowance_line, self).create(cr, uid, vals, context=context)

    def onchange_department_id(self, cr, uid, ids ,department_id,  context=None):
        return {'value': {'employee_id': False}}

    def onchange_allowance_id(self, cr, uid, ids ,allowance_id,  context=None):
        return {'value': {'employee_id': False,'department_id': False}}

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
        return {'value': {'holiday_hours': 0.0, 'week_hours': 0.0}}

    def onchange_hour(self, cr, uid, ids, detail_ids, employee_id, context=None):
        """
        Recalculate the holiday and working days hours.

        @param allowance_id: Id of the allowance
        @param employee_id:  Id of the employee 
        @return: dictionary contains holiday_hours and week_hours
        """
        context = context or {}
        detail_pool = self.pool.get('hr.additional.allowance.detail')
        if not detail_ids:
            detail_ids = []
        res = {
            'week_hours': False,
            'holiday_hours': False,
        }
        detail_ids = resolve_o2m_operations(cr, uid, detail_pool, detail_ids, ['hour', 'dayofweek', 'date'], context)
        emp_holiday_obj = self.pool.get('hr.holidays')
        emp_events_obj = self.pool.get('hr.public.events')
        holiday_hours = week_hours = 0.0
        for detail in detail_ids:
            detail_hour = detail.get('hour', 0.0)
            dayofweek = detail.get('dayofweek', 1)
            date = detail.get('date', False)
            holiday = emp_holiday_obj.search(cr, uid, [('date_to', '>=', date), ('date_from', '<=', date),
                                                       ('employee_id', '=', employee_id), ('state', '=', 'validate')])
            if not holiday:
                holiday= emp_events_obj.search(cr, uid, ['|','&',('end_date', '>=', date),('start_date', '<=', date),('dayofweek', '=', dayofweek)])
            if holiday:
                holiday_hours += detail_hour
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

class hr_additional_allowance_detail(osv.Model):

    _name = "hr.additional.allowance.detail"
    _description = "Working days and the holiday days detailes"
    _columns = {
        'allowance_line_id' : fields.many2one("hr.additional.allowance.line", "Allowance Line", required=True,ondelete='cascade'),
        'dayofweek': fields.selection([(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'),
                                            (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], 'Day of Week', required=True),
        'date' : fields.date('Date', required=True),
        'hour' : fields.float("Hours", required=True),
    }
    _sql_constraints = [
       ('date_uniqe', 'unique (allowance_line_id,date)', 'You can not selected the same Date for the same employee!'),
       ('hour_check', 'check (hour>0 and hour <25 )', 'The number of hours should be between (1 - 24)!'),
    ]
    def onchange_date(self, cr, uid, ids, date, context=None):
        """
        Return day of the week as number where monday is the first day

        @return: dictionary of the value to be updated 
        """
        if not date:
            return {}
        return {'value': {'dayofweek': datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).weekday()+1}}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
