# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

class account_invoice(osv.Model):
   
    _inherit = 'account.invoice'

    def action_move_create(self, cr, uid, ids, context=None):
       """
       Set invoice reference as name in each move line.
       @return: boolean True
       """
       move_line_obj = self.pool.get('account.move.line')
       invoices = self.browse(cr, uid, ids, context=context)
       super(account_invoice, self).action_move_create(cr, uid, ids, context=context)
       for inv in invoices: 
            for line in inv.move_id.line_id:
                if inv.account_id == line.account_id: 
                  self.pool.get('account.move.line').write(cr, uid, [line.id], {'name':inv.origin or '/'}, context=context)
       return True

    def _convert_ref(self, cr, uid, ref):
        return (ref or '')

    def _get_journal(self, cr, uid, context=None):
        """
        Method to get the default ID of journal based on the invoice type
        excluding the journals of special type

        @return: ID of the journal
        """
        if context is None:  
            context = {}
        type_inv = context.get('type', 'out_invoice')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}
        journal_obj = self.pool.get('account.journal')
        # add condition  special to search
        res = journal_obj.search(cr, uid, [('special','=',False),('type', '=', type2journal.get(type_inv, 'sale')),
                                            ('company_id', '=', company_id)], context=context, limit=1)
        return res and res[0] or False
    
    _columns = {
        'state': fields.selection([('draft','Draft'), ('completed','Complete'), ('closed','Close'), ('open','Open'),
                                   ('paid','Done'), ('cancel','Cancelled')],'State', select=True, readonly=True)
    }

    _defaults = {
        'journal_id': _get_journal,
    }

    def invoice_complete(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'completed', 
        check if line's account must has analytic account or not.
        @return: boolean True    
        """
        for inv in self.browse(cr, uid, ids):
            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                raise orm.except_orm(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))
            for inv_line in inv.invoice_line:
                if inv_line.account_id.user_type.analytic_required and not inv_line.account_analytic_id:
                    raise orm.except_orm(_('Error!'), _('You must add analytic account for %s accounts!'%(inv_line.account_id.user_type.report_type,)))
        self.write(cr, uid, ids, {'state': 'completed'},context=context)
        return True

    def onchange_date(self, cr, uid, ids, date_invoice, context=None):
        '''
        Method for getting account period of selected date
        
        @param date date_invoice: Invoice Date,
        @return: dictionary update view values 
        '''
        if context is None: 
            context = {}
        period_pool = self.pool.get('account.period')
        res = {}
        if context.get('invoice_id', False):
            company_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context).company_id.id
            context.update({'company_id': company_id})
        pids = period_pool.find(cr, uid, date_invoice, context=context)
        if pids:
            if not 'value' in res:
                res['value'] = {}
            res['value'].update({'period_id':pids[0]})
        return res

account_invoice() 


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 943
