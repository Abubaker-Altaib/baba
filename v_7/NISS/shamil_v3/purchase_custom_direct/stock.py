# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv
#
# Model definition
#
class stock_picking(osv.osv):
    """
    Add budget confirmation accounts to picking """

    _inherit = 'stock.picking'

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ 
        This Function inherits the main fuction to adding company and budget confirmation id and the currency of user 
	    company and builds the dict containing these values for the invoice

        @param company_id: user company id
        @param budget_confirm_idr: confirmation id
        @param cur_id: the currency of company which the user belongs to
        @return: dict that will be used to create the invoice object
        """
        result = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)
        if picking.purchase_id and picking.purchase_id.ir_id and picking.purchase_id.ir_id.budget_confirm_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            budget_confirm_id = picking.purchase_id.ir_id.budget_confirm_id.id
            cur_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
            result.update({
                           'company_id': company_id,
                           'budget_confirm_id':budget_confirm_id,
                           'currency_id': cur_id or False,
                           })
        return result

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        """
        This Function inherits the main fuction to add account_id, price_unit, invoice_line_tax_id and account_analytic_id 
	    then builds the dict containing these values for the invoice line.

        @param price_unit: the purchase line unit price
        @param analytic_account_from_budget: the analytic account gets from budget confirmation. 
        @param account_id: the general account gets from buget confirmation.
        @return: dict that will be used to create the invoice line
        """
        res = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context)
        price_unit = move_line.purchase_line_id.price_unit
        if picking.purchase_id and picking.purchase_id.ir_id and picking.purchase_id.ir_id.budget_confirm_id and picking.purchase_id.ir_id.budget_confirm_id.analytic_account_id:
            analytic_account_from_budget = picking.purchase_id.ir_id.budget_confirm_id.analytic_account_id.id
            tax_ids = self._get_taxes_invoice(cr, uid, move_line, invoice_vals)
            account_id = picking.purchase_id.ir_id.budget_confirm_id.general_account_id.id
            if not account_id:
                account_id = res['account_id']
            #to be modify
            partner = picking.partner_id 
            if invoice_vals['fiscal_position']:
                account_id = self.pool.get('account.fiscal.position').\
                map_account(cr, uid, partner.property_account_position, account_id)
            res.update({
                           'account_id': account_id,
                           'price_unit': price_unit,
                           'invoice_line_tax_id': [(6, 0, tax_ids)],
                           'account_analytic_id': analytic_account_from_budget,
                           })
        return res
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        """
        Creates invoice based on the invoice state selected for picking.

        @return: IDS of created invoices for the pickings 
        """
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
