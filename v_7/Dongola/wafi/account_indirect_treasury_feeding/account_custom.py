# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, orm
from openerp.tools.translate import _

#----------------------------------------------------------
# Voucher (Inherit)
#----------------------------------------------------------
class account_voucher(osv.Model):

    _inherit = "account.voucher"

    def onchange_operation_type(self, cr, uid, ids, operation_type, partner_id, context=None):
        """
        Method that call when changing operation_type value, when operation is treasury feeding:
            * Reset line_dr_ids field
            * Make voucher with writeoff
            * Make voucher pay later
        
        @return: dictionary of fields values
        """
        val = {'pay_now': operation_type == 'treasury' and 'pay_later' or 'pay_now',
               'payment_option': operation_type == 'treasury' and 'with_writeoff' or 'without_writeoff'}
        if operation_type == 'treasury':
            val.update({'line_dr_ids': False})
            account = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context).property_account_receivable
            if not account:
                raise orm.except_orm(_('Configuration Error!'), _("Please make sure the default receivable account for the selected partner has been set!"))
            val.update({'writeoff_acc_id': account.id})
        return {'value': val}

    def receive_voucher(self, cr, uid, ids, context=None):
        """
        Inherit receive_voucher method to create journal entry when the operation is treasury feeding
        
        @return: change state to 'receive'
        """
        super(account_voucher, self).receive_voucher(cr, uid, ids, context=context)
        if self.browse(cr, uid, ids, context=context)[0].operation_type == 'treasury':
            self.action_move_line_create(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'receive'}, context=context)

    def test_paid(self, cr, uid, ids, *args):
        """
        Method to check if Voucher payed or not
        
        @return: boolean True if payed
        """
        res = self.move_line_id_payment_get(cr, uid, ids)
        if not res: 
            return False
        ok = True
        for id in res:
            cr.execute('SELECT reconcile_id FROM account_move_line WHERE id=%s', (id,))
            ok = ok and bool(cr.fetchone()[0])
        return ok

    def move_line_id_payment_get(self, cr, uid, ids, *args):
        '''
        @return: list of voucher's move lines
        '''
        if not ids: 
            return []
        result = self.move_line_id_payment_gets(cr, uid, ids, *args)
        return result.get(ids[0], [])

    def move_line_id_payment_gets(self, cr, uid, ids, *args):
        ''' 
        Method for getting list of all move lines for each voucher
        
        @return: dictionary move lines list for each voucher  
        '''
        res = {}
        if not ids: 
            return res
        cr.execute("SELECT i.id, l.id \
                   FROM account_account a \
                   INNER JOIN account_move_line l ON (a.id=l.account_id) \
                   INNER JOIN account_voucher i ON (i.move_id=l.move_id) \
                   WHERE i.id IN %s AND a.type IN ('payable','receivable')",
                   (tuple(ids),))
        for r in cr.fetchall():
            res.setdefault(r[0], [])
            res[r[0]].append(r[1])
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
