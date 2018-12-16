# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
from openerp.osv import fields, osv, orm
import decimal_precision as dp
from openerp.tools.translate import _
import netsvc
import time



class account_voucher(osv.Model):
    """ Inherit the voucher object to calculate payment term
        and to allow voucher to calculate more the tax in the voucher.
        It change tax_id type from many2one to many2many.
    """

    _inherit = 'account.voucher'

    def _total_amount_check(self, cr, uid, ids, context=None):
         return True

    def _get_state(self, cr, uid, context=None):

       res = list(super(account_voucher, self)._columns['state'].selection)
       res.append(('paid','Paid'))
       return res


    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        """
        Method for computing purchase/sale voucher residual unpayed yet amount.
            
        @param char name: functional field name,
        @param list args: additional arguments,
        @return: dictionary residual amount for each voucher 
        """
        result = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            result[voucher.id] = 0.0
            if voucher.pay_now == 'pay_now': return result
            if voucher.move_id:
                lines = [m.amount_residual_currency or 0.0 for m in voucher.move_id.line_id \
                        if ((voucher.journal_id.type == 'purchase' and m.account_id.type == 'payable' ) or \
                         (voucher.journal_id.type == 'sale' and m.account_id.type == 'receivable' ))]
                
                if lines :
                  result[voucher.id] = lines and reduce(lambda x, y: x+y, lines) 
                else:
                  result[voucher.id] = voucher.amount
            else:
                result[voucher.id] = voucher.amount
        return result


    def _compute_lines(self, cr, uid, ids, name, args, context=None):
        '''
        Method for getting all payments lines for each purchase/sale voucher.
                    
        @param char name: functional field name,
        @param list args: additional arguments,
        @return: dictionary list of payment lines for each voucher 
        '''
        if context is None: 
            context = {}
        result = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            src,lines = [],[]
            if voucher.move_id and voucher.type=='purchase':
                for m in voucher.move_id.line_id:
                    temp_lines = []
                    if m.reconcile_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_id.line_id)
                    elif m.reconcile_partial_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
                    lines += [x for x in temp_lines if x not in lines]
                    src.append(m.id)

            lines = filter(lambda x: x not in src, lines)
            result[voucher.id] = lines
        return result

    def _check_date(self, cr, uid, ids, context=None):
        """Constrain method to check whether the selected date is within the period start/end date.
    
        @return: Boolean True or False
        """

        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.allow_date and voucher.period_id:
                if not time.strptime(voucher.date[:10],'%Y-%m-%d') >= time.strptime(voucher.period_id.date_start, '%Y-%m-%d') or not time.strptime(voucher.date[:10], '%Y-%m-%d') <= time.strptime(voucher.period_id.date_stop, '%Y-%m-%d'):
                    return False
        return True

    _columns = {
        'state':fields.selection(selection=[('draft','Draft'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('reversed','Reversed'),
             ('paid','Paid'),
             ('posted','Posted')
            ], string='Status', readonly=True, size=32, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Budget Not Appoved\' when at least one of budget confirmations related to this voucher didn\'t approve . \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Reversed\' when voucher\'s move reversed automatically reversed it\'s voucher. \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),

        'tax_id': fields.many2many('account.tax', 'account_voucher_tax_rel', 'voucher_id', 'tax_id', '   ', readonly=True,
                                       states={'draft':[('readonly', False)], 'approve':[('readonly', False)]}, domain=[('parent_id', '=', False)]),
        'payment_ids': fields.function(_compute_lines, method=True, relation='account.move.line', type="many2many", string='Payments'),
        'date':fields.date('Date', readonly=True, select=True, states={'draft':[('readonly',False)]}, help="Effective date for accounting entries"),
        'residual': fields.function(_amount_residual, method=True, digits_compute=dp.get_precision('Account'),
                                    string='Residual', help="Remaining amount due."),

    }
    _constraints = [
        (_total_amount_check, "Operation is not completed, Total amount shouldn't be zero!", []), 
        (_check_date, 'The date of your Journal Entry is not in the defined period! You should change the date or remove this constraint from the journal.', ['date']),]

    _defaults = {
        'tax_id':False,
        'pay_now':'pay_now',
    }
    def write(self, cr, uid, ids, vals, context={}):
        ''' overwrite write method to calc. sum of voucher line amount in payment type'''
        amount_line=0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.type =='payment' and voucher.line_ids:
               for line in voucher.line_ids:
                   amount_line+=line.amount
               vals.update({'amount': amount_line })
        return super(account_voucher, self).write(cr, uid, ids, vals, context=context)

    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context={}): #NEED TO TEST
        """
        Method call when changing Voucher Lines and/or Voucher Taxs, recalculate voucher amount 
        before taxs, taxs amount and voucher total amount.   
        @param line_ids: list of voucher line ids
        @param tax_id: IDs of voucher taxes
        @param partner_id: partner_id
        @return: dictionary of values     
        """
        if isinstance(ids, int):
            ids = [ids]
        voucher=self.browse(cr,uid,ids,context=context)
        tax_id = isinstance(tax_id, int) and [tax_id] #or (not isinstance(tax_id[0], list) and tax_id or tax_id[0][2])
        if tax_id:
           for tax in tax_id:
               res=super(account_voucher,self).onchange_price(cr, uid, ids, line_ids, tax, partner_id=partner_id, context=context)
        else :
               res=super(account_voucher,self).onchange_price(cr, uid, ids, line_ids, False, partner_id=partner_id, context=context)
        res['value'].update({'amount':voucher and voucher[0].amount or 0.0 , 'tax_amount':voucher and voucher[0].tax_amount or 0.0})
        return res

    def test_paid(self, cr, uid, ids, *args):
        """
        Method to check if Voucher payed or not
        @return Boolean True if payed
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
        ''' @return: list of voucher's move lines '''
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
        cr.execute('SELECT i.id, l.id '\
                   'FROM account_move_line l '\
                   'LEFT JOIN account_voucher i ON (i.move_id=l.move_id) '\
                   'WHERE i.id IN %s '\
                   'AND l.account_id=i.account_id',
                   (tuple(ids),))
        for r in cr.fetchall():
            res.setdefault(r[0], [])
            res[r[0]].append(r[1])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 943
