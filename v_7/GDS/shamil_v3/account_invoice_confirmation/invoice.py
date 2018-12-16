# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
#This module add confirmation to invoice 
from openerp.osv import osv
from openerp.osv import fields
import time

class account_invoice(osv.Model):
    
    _inherit = 'account.invoice'

    def _get_analytic_lines(self, cr, uid, id, context=None):
        """
        Add budget_confirm_id field to result dictionary.

	@return: dictionary of values to be updated
        """
        inv = self.browse(cr, uid, id, context=context)
    	res = super(account_invoice, self)._get_analytic_lines( cr, uid, id)
    	for r in res:
    	    r.update({'budget_confirm_id':inv.budget_confirm_id.id})
    	return res

    def line_get_convert(self, cr, uid, line, part, date, context=None):
        """
        Add budget_confirm_id field to result dictionary

        @param part: partner_id
        @param date: date of invoice
	@return: dictionary of values to be updated
        """
        res = super(account_invoice, self).line_get_convert(cr, uid, line, part, date, context)
        res.update({
               'budget_confirm_id':line['price']>0 and line.get('budget_confirm_id', False),
        })
        return res

    _columns = {
        'budget_confirm_id': fields.many2one('account.budget.confirmation', 'Confirmation', ondelete="restrict"),
    }
account_invoice() 


class account_invoice_tax(osv.Model):

    _inherit = "account.invoice.tax"

    def move_line_get(self, cr, uid, invoice_id):
        """
        Check the budget_confermation_id in particular invoice and update
        tax line move by it or set False.

        @param invoice_id : id for invoice
	@return: dictionary of values to be updated
        """
        inv_tax = self.browse(cr, uid, invoice_id)
        inv_obj= self.pool.get('account.invoice').browse(cr, uid, invoice_id)
	res = super(account_invoice_tax, self).move_line_get( cr, uid, invoice_id)
	for r in res:
            if inv_obj.budget_confirm_id:
               if r['price']>0 and r['account_id']==inv_obj.budget_confirm_id.general_account_id.id :
                  r.update({'budget_confirm_id' :inv_obj.budget_confirm_id.id and inv_obj.budget_confirm_id.id or False },)
	return res

    def compute(self, cr, uid, invoice_id, context=None):
        """
        Inherit taxes compute method to add the analytic account in the taxes line and write vals
        depend on tax configration.

        @param invoice_id: id for invoice
	@return: dictionary of values to be updated
        """
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity,  line.product_id, inv.partner_id)['taxes']:
                tax['price_unit'] = cur_obj.round(cr, uid, cur, tax['price_unit'])
                val={
                    'invoice_id': inv.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': tax['price_unit'] * line['quantity'],

                }
                if inv.type in ('out_invoice','in_invoice'):
                    val.update({'base_code_id': tax['base_code_id'], 
                                      'tax_code_id': tax['tax_code_id'],
                                      'base_amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                                      'tax_amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                                      'account_id': tax['account_collected_id'] or line.account_id.id,
                                      'account_analytic_id': line.account_analytic_id.id or tax['account_analytic_paid_id'] or ( not tax['account_collected_id'] and line.account_analytic_id.id and line.account_analytic_id.id or False )})
                else: 
                    val.update({'base_code_id': tax['ref_base_code_id'],
                                      'tax_code_id': tax['ref_tax_code_id'],
                                      'base_amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                                      'tax_amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False),
                                      'account_id': tax['account_paid_id'] or line.account_id.id,
                                      'account_analytic_id': line.account_analytic_id.id or tax['account_analytic_paid_id'] or (not tax['account_paid_id'] and line.account_analytic_id.id and line.account_analytic_id.id or False)})

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'],val['account_analytic_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped
        
account_invoice_tax()

