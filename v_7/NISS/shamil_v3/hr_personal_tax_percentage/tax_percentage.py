# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import datetime
import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import mx
from dateutil.relativedelta import relativedelta

class hr_tax(osv.Model):
    """
    To prepare personal salary percentage"""

    def _check_personal_tax(self, cr, uid, ids, context=None):
        """
        Constrain method that check digit you insert.

        @return: Boolean True or False
        """
        for tax in self.browse(cr, uid, ids): 
            if tax.personal_tax < 0 :
               return False    	
        return True
    _inherit = 'hr.tax'
    _columns = {
        'personal_tax': fields.float('personal salary percentage',digits = (16,2),help="represents the percentage of salary that the tax will be taken from"),
    }
    _constraints = [
        (_check_personal_tax, 'Please insert the right digit',
            ['personal tax']),
    ]


class hr_payroll_main_archive(osv.Model):
    _inherit = 'hr.payroll.main.archive'
    def total_allow_deduct(self, cr, uid, ids, name, args, context=None):
        """Method that caluclates the totals of employee's allowances, deductions, taxes and gets the net.
	       @return: Dictionary of values
        """
        tax = self.pool.get('hr.tax')
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            taxable_amount = 0.0
            total_allowance = rec.basic_salary
            allowances_tax = 0.0
            income_tax = 0.0
	    new_taxable_amount = 0.0
            total_deduction = 0.0
            for line in rec.allow_deduct_ids:
                if line.type == 'allow':
                    total_allowance += line.amount
                    allowances_tax += line.tax_deducted
                    if line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
                        taxable_amount += line.amount - line.allow_deduct_id.exempted_amount
                else:
                    total_deduction += line.amount
                    if line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
                        taxable_amount -= line.amount - line.allow_deduct_id.exempted_amount
            if not rec.employee_id.tax_exempted:
                taxable_amount += rec.basic_salary
                tax_id = tax.search(cr, uid, [('taxset_min', '<=', taxable_amount), ('taxset_max', '>=', taxable_amount)], context=context)
            if tax_id:
                tax_rec = tax.browse(cr, uid, tax_id)[0]
		new_taxable_amount = abs(taxable_amount * tax_rec.personal_tax / 100)
                income_tax = (((new_taxable_amount - tax_rec.taxset_min) * tax_rec.percent) / 100) + tax_rec.previous_tax
            result[rec.id] = {
                'tax':income_tax,
                'total_allowance':total_allowance,
                'allowances_tax': allowances_tax,
                'total_deduction': total_deduction + allowances_tax + income_tax,
                'net':(total_allowance - allowances_tax - total_deduction - income_tax),
            }
        return result

    _columns = {
         'total_allowance' :fields.function(total_allow_deduct, multi='sum', string='Total Allowance', type='float',
                                               digits_compute=dp.get_precision('Payroll') , readonly=True, store=True),
         'tax' :fields.function(total_allow_deduct, string='Income Tax', type='float', digits_compute=dp.get_precision('Payroll'),
                                     multi='sum', readonly=True, store=True),
         'allowances_tax' :fields.function(total_allow_deduct, string='allowance Taxes', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
         'total_deduction' :fields.function(total_allow_deduct, multi='sum', string='Total Deduction', type='float',
                                                digits_compute=dp.get_precision('Payroll'), required=True , readonly=True, store=True),
         'net' :fields.function(total_allow_deduct, string='Salary Net', multi='sum', type='float',
                                                    digits_compute=dp.get_precision('Payroll'),
                                   required=True , readonly=True, store=True),
		}
    _defaults = {
        'total_allowance': 0.0,
        'tax' : 0.0,
        'allowances_tax' : 0.0,
        'total_deduction': 0.0,
        'net' : 0.0
    }
    

