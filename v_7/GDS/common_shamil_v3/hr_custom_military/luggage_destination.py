from tools.translate import _
from osv import osv
from osv import fields
import decimal_precision as dp
import netsvc
import time
from datetime import datetime


class luggage_destination_map(osv.osv):
    _name = "luggage.destination.map"
    _description = "Payment Term"
    _columns = {
        'name': fields.char('Destination', size=512, required=True),
        'active': fields.boolean('Active'),
        'amount': fields.float('Amount', required=True),
    }
    _defaults = {
        'active': 1,
    }



class hr_additional_allowance_line(osv.osv):

    _name = "hr.additional.allowance.line"
    _inherit ="hr.additional.allowance.line"

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
                if rec.type == 'default':
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
                if rec.type == 'luggage_transfer':
                    allow_dict= self.pool.get('payroll').allowances_deductions_calculation(cr,uid,rec.period_id.date_start,rec.employee_id,{'no_sp_rec':True},[allow.id], False,[])
                    tax = allow_dict['result'][0]['tax'] * rec.week_hours
                    gross = rec.week_hours * rec.type_amount
                    result[rec.id] = {'amounts_hours': rec.type_amount,
                                    'no_hours': rec.week_hours,
                                    'tax': tax,
                                    'imprint': allow.stamp ,
                                    'gross_amount': gross,
                                    'amounts_value': gross - tax - allow.stamp
                    }

        return result

    def _get_line_ids(self, cr, uid, ids, context=None, args=None):
        """
        Method that gets the id of additional allowance line.

        @return: list that contains additional_allowance_id
        """
        return self.pool.get('hr.additional.allowance.line').search(cr, uid, [('additional_allowance_id', 'in', ids)], context=context)


    _columns = {
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
        'type': fields.selection([('default', 'Default'), ('luggage_transfer', 'Luggage Transfer')], 'State'),
        'type_amount': fields.float('Amount'),
    }

    _defaults = {
        'type': 'default',
    }
