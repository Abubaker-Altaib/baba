# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import netsvc
import time


# ----------------------------------------------------
# Stock Location (Inherit)
# ----------------------------------------------------
class stock_location(osv.Model):
    _inherit= "stock.location"
    _columns={
	    'code': fields.char('Code', size=2),
        'valuation_account_id': fields.property('account.account',
            type='many2one', 
            relation='account.account',
            string='Stock Account', 
            method=True, 
            view_load=True,
            domain="[('type', '!=', 'view')]",
            help='his account will be used to value stock moves that have this location'),
	}
    _sql_constraints = [
       	    ('code_uniq', 'unique(code)', 'Location Code must be unique !'),
    ]

# ----------------------------------------------------
# Stock picking in (Inherit)
# ----------------------------------------------------
class stock_picking_in(osv.Model):
    _inherit = "stock.picking.in"
    _columns = {
        'department_id':fields.many2one('hr.department', 'Department'),
        'analytic_account_id':fields.many2one('account.analytic.account', 'Analytic Account'),
        'account_id': fields.many2one('account.account', 'Account',domain = [('type','=','other')]),
        'account_move_id':fields.many2one('account.move', 'Account Move', readonly = True,),     
	}


# ----------------------------------------------------
# Stock picking out (Inherit)
# ----------------------------------------------------
class stock_picking_out(osv.Model):
    _inherit = "stock.picking.out"
    _columns = {
        'department_id':fields.many2one('hr.department', 'Department'),
        'analytic_account_id':fields.many2one('account.analytic.account', 'Analytic Account'),
        'account_id': fields.many2one('account.account', 'Account',domain = [('type','=','other')]),
        'account_move_id':fields.many2one('account.move', 'Account Move', readonly = True,),     
	}

# ----------------------------------------------------
# Stock picking (Inherit)
# ----------------------------------------------------
class stock_picking(osv.Model):
    _inherit = "stock.picking"
    _columns = {
        'department_id':fields.many2one('hr.department', 'Department'),
        'analytic_account_id':fields.many2one('account.analytic.account', 'Analytic Account'),
        'account_id': fields.many2one('account.account', 'Account',domain = [('type','=','other')]),
        'account_move_id':fields.many2one('account.move', 'Account Move', readonly = True,),     
	}
    
    def action_done(self, cr, uid, ids, context=None):
        """
        Changes picking state to done and generate the appropriate accounting moves 
        if the product being moves is subject to real_time valuation tracking

        @return: True
        """
        super(stock_picking, self).action_done(cr, uid, ids, context=context)
        account_move_obj = self.pool.get('account.move')
        stock_move_obj = self.pool.get('stock.move')
        account_moves=[]
        moves=[]
        for pick in self.browse(cr, uid, ids, context=context):
            for move in pick.move_lines:
                if move.state=='cancel':
                    continue
                moves.append(move)
                account_moves += stock_move_obj._create_product_valuation_moves(cr, uid, move, pick.date,context=context)
            if account_moves:
                stock_journal = self.pool.get('res.users').browse(cr, uid, uid).company_id.stock_journal
                if not stock_journal:
                    raise osv.except_osv(_('No Stock Journal!'),_("There is no journal defined on your Company"))
                period =  self.pool.get('account.period').find(cr, uid, dt=pick.date, context=context)
                new_account_move = account_move_obj.create(cr, uid, {
                	'name': '/',
                 	'journal_id':stock_journal.id,
                    'line_id': account_moves,
                    'period_id':period[0],
                    'ref': pick.name,
				    'date':pick.date,
                })
                self.write(cr,uid,ids,{'account_move_id':new_account_move,})
                account_move_obj.completed(cr, uid, [new_account_move], context)
                account_move_obj.post(cr, uid, [new_account_move], context)

        return True



# ----------------------------------------------------
# Stock Move (Inherit)
# ----------------------------------------------------
class stock_move(osv.Model):
    _inherit= "stock.move"

    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Method to get the accounts use to post Journal Entries for the real-time
        valuation of the move.

        @param context: context dictionary that can explicitly mention the company 
                        to consider via the 'force_company' key
        @return: ID of input account, ID of output account
        """
        product_obj=self.pool.get('product.product')
        accounts = product_obj.get_product_accounts(cr, uid, move.product_id.id, context)
        if move.location_id.valuation_account_id:
            acc_src = move.location_id.valuation_account_id.id
        else:
            acc_src = accounts['stock_account_input']
        if move.location_dest_id.valuation_account_id:
            acc_dest = move.location_dest_id.valuation_account_id.id
        else:
            acc_dest = accounts['stock_account_output']
        return  acc_src, acc_dest

    def _create_product_valuation_moves(self, cr, uid, move,date, context=None):
        """
        Method to get the appropriate accounting moves if the product being moves is 
        subject to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.

        @raise: osv.except_osv() is any mandatory account is not defined.
        """
        account_moves = []
        if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?

            if context is None:
                context = {}
            src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)

            # Outgoing moves (or cross-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage not in ['internal','transit']):
                acc_src, acc_dest = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                if move.picking_id.account_id:
                    acc_dest=move.picking_id.account_id.id
                if (not acc_src) or (not acc_dest):
                    raise osv.except_osv(_('Error!'), _('There is no Accounts defined ' ))

                account_moves = self._create_account_move_line(cr, uid, move,date, acc_src, acc_dest, reference_amount, reference_currency_id, context)         
            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage not in ['internal','transit'] and move.location_dest_id.usage == 'internal'):
                acc_src, acc_dest = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                if move.picking_id.account_id:
                    acc_src=move.picking_id.account_id.id
                if (not acc_src) or (not acc_dest):
                    raise osv.except_osv(_('Error!'), _('There is no Accounts defined ' ))
                account_moves = self._create_account_move_line(cr, uid, move,date, acc_src, acc_dest,  reference_amount, reference_currency_id, context)
            # Internal moves
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal'\
                    and move.location_id.company_id == move.location_dest_id.company_id):
                acc_src, acc_dest  = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                if (not acc_src) or (not acc_dest):
                    raise osv.except_osv(_('Error!'), _('There is no Accounts defined ' ))
                account_moves = self._create_account_move_line(cr, uid, move ,date, acc_src, acc_dest, reference_amount, reference_currency_id, context)

            # Outgoing moves ( multi-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage in ['internal','supplier'] and move.location_dest_id.usage =='transit'):
                acc_src, acc_dest= self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                if (not acc_src) or (not acc_dest):
                    raise osv.except_osv(_('Error!'), _('There is no Accounts defined ' ))
                account_moves = self._create_account_move_line(cr, uid, move, date, acc_src, acc_dest ,reference_amount, reference_currency_id, context)

            # Outgoing moves ( multi-company output part)
            if move.location_id.usage == 'transit' and move.location_dest_id.usage =='transit':
                acc_src, acc_dest= self._get_accounting_data_for_valuation(cr, uid, move, context)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, context)
                if (not acc_src) or (not acc_dest):
                    raise osv.except_osv(_('Error!'), _('There is no Accounts defined ' ))
                account_moves = self._create_account_move_line(cr, uid, move, date, acc_src, acc_dest ,reference_amount, reference_currency_id, context)

            # Incoming moves ( multi-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage =='transit' and move.location_dest_id.usage == 'internal'):
                acc_src, acc_dest = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, dest_company_ctx)
                if (not acc_src) or (not acc_dest):
                    raise osv.except_osv(_('Error!'), _('There is no Accounts defined ' ))
                account_moves = self._create_account_move_line(cr, uid, move,date, acc_src, acc_dest, reference_amount, reference_currency_id, context)

        return account_moves

    def action_done(self, cr, uid, ids, context=None):
        """ 
        Makes the move done and if all moves are done, it will finish the picking.
        @return: Boolean True
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                #cr.execute('insert into stock_move_history_ids (parent_id,child_id) values (%s,%s)', (move.id, move.move_dest_id.id))
                if move.move_dest_id.state in ('waiting', 'confirmed'):
                    self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                    if move.move_dest_id.picking_id:
                        wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                    if move.move_dest_id.auto_validate:
                        self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            #self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed','done','assigned'):
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        for id in move_ids:
             wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True       

    def _create_account_move_line(self, cr, uid, move,date, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given stock move.

        @param move : dict of stock move values
        @param date : date of stock move
        @param src_account_id : account_id of stock in move
        @param dest_account_id : account_id of destination stock in stock move 
        @param reference_amount : amount of stock move that is will be creating in account move line
        @param reference_currency_id : currency_id of stock move
        @return: account move lines
        """

        # prepare default values considering that the destination accounts have the reference_currency_id as their main currency
        partner_id = (move.picking_id and move.picking_id.partner_id and move.picking_id.partner_id.id) or False
        period = self.pool.get('account.period').find(cr, uid, dt=date, context=context)

        debit_line_vals = {
					'name': move.name,
					'product_id': move.product_id and move.product_id.id or False,
					'quantity': move.product_qty,
					'ref': move.picking_id and move.picking_id.name or False,
					'date': date,
					'partner_id': partner_id,
					'stock_move_id': move.id,
					'debit': reference_amount,
					'account_id': dest_account_id,
					'analytic_account_id':move.picking_id and move.picking_id.analytic_account_id.id or False, 
					'period_id':period[0], 
		}
        credit_line_vals = {
					'name': move.name,
					'product_id': move.product_id and move.product_id.id or False,
					'quantity': move.product_qty,
					'ref': move.picking_id and move.picking_id.name or False,
					'date': date,
					'partner_id': partner_id,
					'stock_move_id': move.id,
					'credit': reference_amount,
					'account_id': src_account_id,
					'period_id':period[0], 
		}
        
        if move.picking_id and move.picking_id.type=='in':
            debit_line_vals.update({'analytic_account_id':False})
            credit_line_vals.update({'analytic_account_id':move.picking_id and move.picking_id.analytic_account_id.id or False})
    
        account_obj = self.pool.get('account.account')
        src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], context=context)
        src_main_currency_id = src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.company_id.currency_id.id
        cur_obj = self.pool.get('res.currency')
        if reference_currency_id != src_main_currency_id:
            # fix credit line:
            credit_line_vals['credit'] = cur_obj.compute(cr, uid, reference_currency_id, src_main_currency_id, reference_amount, context=context)
            if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
                credit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)
        if reference_currency_id != dest_main_currency_id:
            # fix debit line:
            debit_line_vals['debit'] = cur_obj.compute(cr, uid, reference_currency_id, dest_main_currency_id, reference_amount, context=context)
            if (not dest_acct.currency_id) or dest_acct.currency_id.id == reference_currency_id:
                debit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]


    _columns = {
        'account_move_line_ids': fields.one2many('account.move.line', 'stock_move_id', 'Move lines', readonly = True,), 

               }


# ----------------------------------------------------
# Stock Inventory (Inherit)
# ----------------------------------------------------
class stock_inventory(osv.Model):
    _inherit= "stock.inventory"

    def _get_amount_difference(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            for move in inv.move_ids:
                if move.location_id.usage == 'internal':
                    amount -= (move.product_qty * move.product_id.standard_price )
                else:
                    amount += (move.product_qty * move.product_id.standard_price )
            return amount

    def action_done(self, cr, uid, ids, context=None):
        """ 
        Finish the inventory and  generate the appropriate accounting moves 
        if the product being moves is subject to real_time valuation tracking

        @return: boolean True
        """
        if context is None:
            context = {}
        account_move_obj = self.pool.get('account.move')
        stock_move_obj = self.pool.get('stock.move')
        account_moves=[]
        for inv in self.browse(cr, uid, ids, context=context):
            inventory_move_ids = [x.id for x in inv.move_ids]
            stock_move_obj.action_done(cr, uid, inventory_move_ids, context=context)
            # ask 'stock.move' action done are going to change to 'date' of the move,
            # we overwrite the date as moves must appear at the inventory date.
            stock_move_obj.write(cr, uid, inventory_move_ids, {'date': inv.date}, context=context)
            self.write(cr, uid, [inv.id], {'state':'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
            for move in inv.move_ids:
                account_moves += stock_move_obj._create_product_valuation_moves(cr, uid, move,inv.date,context=context)
            if account_moves:
                stock_journal = self.pool.get('res.users').browse(cr, uid, uid).company_id.stock_journal
                if not stock_journal:
                    raise osv.except_osv(_('No Stock Journal!'),_("There is no journal defined on your Company"))
                period = self.pool.get('account.period').find(cr, uid, dt=inv.date, context=context)
                new_account_move = account_move_obj.create(cr, uid, {
                    'name': '/',
                  	'journal_id':stock_journal.id,
                	'line_id': account_moves,
                	'ref': inv.sequence,
                	'period_id':period[0],
                	'date':inv.date,
                })
                account_move_obj.completed(cr, uid, [new_account_move], context)
                account_move_obj.post(cr, uid, [new_account_move], context)
                amount = self._get_amount_difference(cr, uid, ids,context=context)
                self.write(cr, uid, [inv.id], {'move_id':new_account_move, 'amount':amount}, context=context)  
        return True



# ----------------------------------------------------
# res company(Inherit)
# ----------------------------------------------------
class res_company(osv.Model):
    _inherit= "res.company"
    _columns={
        'stock_journal': fields.many2one('account.journal', 'Stock journal',help="When doing real-time inventory valuation, this is the Accounting Journal in which entries will be automatically posted when stock moves are processed."),
	}

#----------------------------------------------------------
# Stock Piching in (Inherit)
#

class account_move(osv.osv):
    """ 
	Inherit account move object to change reverse function.
    """
    _inherit = 'account.move'
    
    def revert_move(self, cr, uid, ids, journal, period, date, reconcile=True, context=None):

        """ inherit revert move to prohibit user from reversing move of asset
            @param journal: ID of the move journal to be reversed
            @param journal: ID of the period of the reversing move 
            @param date: date of the reversing move 
            @param reconcile: boolean partner reconcilation
            @return: ID of the new reversing move
        """
        move_line_obj=self.pool.get('account.move.line')
        res = super(account_move, self).revert_move(cr, uid, ids, journal, period, date, reconcile=True, context=context)
        for move in self.browse(cr,uid,ids,context):
            move_line_ids=move_line_obj.search(cr,uid,[('move_id','=',move.id),('debit','>',0)],context=context)
            for line in move_line_obj.browse(cr,uid,move_line_ids,context):
                if line.product_id:
                    raise osv.except_osv(_('Error!'), _('You cannot reverse move for %s product'%(line.product_id.name,)))                    
        return res
    
    def unlink(self, cr, uid, ids, context=None, check=True):
        """ inherit method to add constrain when delete move line that contain product_id
        @param check: if true, to check
        @return: super unlink method of object
        """
        for move in self.browse(cr, uid, ids, context=context):
            for line in move.line_id:
                if line.product_id:
                    raise osv.except_osv(_('Sorry!'), _('You cannot delete move for %s product'%(line.product_id.name,)))                    
        return super(account_move, self).unlink(cr, uid, ids, context=context)

#----------------------------------------------------------
# Account Move Line(Inherit)
#----------------------------------------------------------
class account_move_line(osv.Model):

    """ Inherit model to add new feild """

    _inherit = 'account.move.line'

    _columns = {

        'stock_move_id' : fields.many2one('stock.move', 'Stock Move'),




        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
