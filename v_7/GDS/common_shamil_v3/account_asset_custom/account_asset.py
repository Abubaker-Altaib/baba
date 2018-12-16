# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import tools
from osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _



class account_asset_asset(osv.osv):
    """
    Asset record including basic information of the asset."""

    _inherit = 'account.asset.asset'

    def suspend(self, cr, uid, ids, context=None):
        """
        This Method used to change the state of the asset to 'suspend'. 
        
        @return: write function (True)
        """ 
        return self.write(cr, uid, ids, {'state': 'suspend'}, context=context)

    def resume(self, cr, uid, ids, context=None):
        """
        This Method used to change the state of the asset to 'open'. 
        
        @return: write function (True)
        """ 
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def _amount_total(self, cr, uid, ids, name, args, context={}):
        """
        This Method used to calculate the two functional fields value_residual and purchase_value
        based on configured accounts of the category. 

        @param char name: the name of the functional field to be calculated,        
        @param list arg: other arguments,
        @return: float of value_residual or purchase_value
        """ 
        if not ids:
            return {}
        res = {}
        for id in ids:
            res[id] = {}
            asset=self.browse(cr,uid,id,context=context)
            salvage= asset.salvage_value or 0
            account_id = asset.category_id.account_asset_id.id
            account_depr = asset.category_id.account_depreciation_id.id
            cr.execute("SELECT SUM(m.debit-m.credit) AS asset_value \
                            FROM account_asset_asset a \
                            LEFT JOIN account_move_line m \
                                ON (a.id=m.asset_id) \
                            WHERE a.id = %s AND m.account_id = %s \
                            " % (id, account_id, ))
            asset_value = cr.fetchone()[0] or 0.0
            if account_id == account_depr:
                if name=='purchase_value':res[id] = asset_value
                else:res[id]= asset_value-salvage
            else:        
                cr.execute("SELECT SUM(ml.debit-ml.credit) AS asset_depr \
                            FROM account_asset_asset a \
                            LEFT JOIN account_move_line ml \
                                ON (a.id=ml.asset_id) \
                            WHERE a.id = %s AND (ml.account_id = %s )" % (id,account_depr,   ))
                asset_depr = cr.fetchone()[0] or 0.0
                if name=='purchase_value':
                    res[id] = asset_value 
                else: res[id] = asset_value + asset_depr -salvage >0 and  asset_value + asset_depr -salvage or 0
            #if asset.value_residual != res[id]:
                #self.compute_depreciation_board(cr, uid, [asset.id], context=context)
            if  name=='value_residual' and res[id] > 0 and asset.state=='close':
                asset.write({'state':'open'})
            return res


    _columns = {
        'location_id'   :fields.many2one('account.asset.location','Location'),
        'purchase_value':fields.function(_amount_total, method=True, digits_compute=dp.get_precision('Account'), string='Gross Value', 
                        store={
                            'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['account_move_line_ids','salvage_value'], 10),
                        }),   

        'value_residual': fields.function(_amount_total, method=True, digits_compute=dp.get_precision('Account'), string='Current (book) Value', 
                        store={
                            'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['account_move_line_ids','salvage_value'], 20),
                        }),
        'state': fields.selection([('draft','Draft'),('open','Running'),('close','Close'),
                                   ('suspend','suspend'),('sold','Sold'),('abandon','Abandon')],
                                    'Status', required=True,
                                  help="When an asset is created, the status is 'Draft'.\n" \
                                       "If the asset is confirmed, the status goes in 'Running' and "\
                                        "the depreciation lines can be posted in the accounting.\n" \
                                       "You can manually close an asset when the depreciation is over. "\
                                        "If the last line of depreciation is posted, the asset automatically goes in that status."),

        'history_ids': fields.one2many('account.asset.history', 'asset_id', 'History'),
        'serial_no': fields.char('Code', size=4,help="Serial Number the Asset"),
        'custody_type': fields.char('custody type',readonly=1 , size=64,help="Custody Type"),

    }
    _sql_constraints = [
                   ('serial_no', 'unique(serial_no)', 'Serial Number must be unique !'),

    ]
class account_asset_category(osv.Model):
    _inherit = 'account.asset.category'
    _columns = {
        'code': fields.char('Code', size=64, required=True),
        'account_reval_id': fields.many2one('account.account', 'Revalue Account'),
        'account_sale_id': fields.many2one('account.account', 'Sale Account'),
        'account_initial_id': fields.many2one('account.account', 'Initial Account'),
        'account_pl_id': fields.many2one('account.account', 'P/L Account',
                                        help="This account is used for book value in the abandon and sale operation."),

    }


class account_asset_depreciation_line(osv.Model):
    """
    A depreciation object to calculate and store the depreciation amount based on configured terms.
    """

    _inherit = 'account.asset.depreciation.line'
    
    def check_depreciation(self, cr, uid, line):
        """
        Constrain method to control whether to allow user skip posting depreciation and post recent depreciation
        based on configuration.

        @param line: object record of the depreciation line
        @return: True or raise message
        """

        if not line.asset_id.company_id.skip_depr:
            cr.execute(" select id from account_asset_depreciation_line where asset_id=%s and \
                                    depreciation_date < %s and move_check=False limit 1 ",(line.asset_id.id, line.depreciation_date))
            depreciation = cr.fetchone()   
            if depreciation:
                raise orm.except_orm(_('Warrning'), _('You cannot skip depreciation!') )
        return True        


    def create_move(self, cr, uid, ids, context=None):
        """
        create_move, over write the original create_move to create one move for a group of depreciation lines .
        """
        can_close = False
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        asset_ids = []
        depreciation_date = context.get('depreciation_date') or time.strftime('%Y-%m-%d')
        ctx = dict(context, account_period_prefer_normal=True)
        period_ids = period_obj.find(cr, uid, depreciation_date, context=ctx)
        move_vals = {
                'name': 'Depreciation Of/ ',
                'date': depreciation_date,
                'ref': context.get('reference') or '',
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': 1,
                }
        move_id = move_obj.create(cr, uid, move_vals, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            if line.move_check:
                continue    
            self.check_depreciation(cr, uid, line)
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
            asset_name = line.asset_id.name
            reference = line.name
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            move_line_id1=move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_curaccount_pl_idrency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_id2=move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_idaccount_pl_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': line.asset_id.id
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            asset_ids.append(line.asset_id.id)
            line.asset_id.write( {'account_move_line_ids': [(4, move_line_id1, False), (4, move_line_id2, False)]})

        if not asset_ids:
            move_obj.unlink(cr, uid, [move_id], context=context)
            return False 
        if not context.get('reference'): 
            cr.execute('''update account_move_line  set ref=%s WHERE  id in %s''',(reference,(move_line_id1,move_line_id2)))
        move_obj.write(cr, uid, [move_id], {'ref':reference,'journal_id': line.asset_id.category_id.journal_id.id}, context=context)
        move_obj.completed(cr, uid, [move_id], context)
        move_obj.post(cr, uid, [move_id], context)
        for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
            if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                asset.write({'state': 'close'})
        return move_id

     
class account_asset_history(osv.osv):
    """Object to record all operation (initial, revalue, abandon and sale) to asset. 
    """

    _inherit = 'account.asset.history'
    _rec_name = 'type'

    def unlink(self, cr, uid, ids, context=None):
        """ Inherit unlink to  prohibit user from deleting reversed or posted operation.

        @return: supre unlink function
        """

        for history in self.browse(cr, uid, ids, context=context):
            if history.state in ('posted','reversed'): 
                raise osv.except_osv(_('Error!'), _('You cannot delete  %s history line '%(history.state,)))
        return super(account_asset_history, self).unlink(cr, uid, ids, context=context)

    def  _check_history_lines(self, cr, uid, ids, context=None): 
        """ Constrain fucntion to prohibit user from making teo operation at a time and 
        prohibit user to make any operation on zero value asset.

        @return: True or raise message
        """
        for hst in self.browse(cr, uid, ids, context=context):
            intial=self.search(cr, uid, [('asset_id','=',hst.asset_id.id),('type','=','initial'),('id','!=',hst.id)], context=context)
            if hst.type=='initial':
                if intial:
                    raise orm.except_orm(_('Warrning'), _('Sorry the Intial value has already been intered you can not repeat this process!') )
                return True

            else:
                msg=not intial and 'Sorry no intial value for this asset please set it first to complate this process !' or \
                    self.search(cr, uid, [('asset_id','=',hst.asset_id.id),('state','=','draft'),('id','!=',hst.id)], context=context) and\
                    hst.state not in  ('reversed','posted') and 'Sorry you need to post draft prosess first to complate this process !' or\
                    hst.asset_id.purchase_value==0.0 and hst.asset_id.value_residual==0.0  and \
                    'Sorry you can not undergone any process over this asset '  or ''
                if msg :
                    raise orm.except_orm(_('Warrning'), msg )
                return True

    def onchange_type(self, cr, uid, ids, asset_id, type, context=None):
        """Onchange method to return fill the account of the operation based on the
        configuration of the category of the asset.

        @param asset_id: id of the asset
        @param type: char type of the operation on the asset 
        @return: dictionary contain the id of the account
        """
        account_id = False
        res = {}
        if asset_id:
            category = self.pool.get('account.asset.asset').browse(cr, uid, asset_id, context=context).category_id
            account_id = type=='reval' and category.account_reval_id  and  category.account_reval_id.id or \
                         type=='initial' and category.account_initial_id  and  category.account_initial_id.id or \
                         type=='sale' and category.account_sale_id  and  category.account_sale_id.id or False
        res = {'account_id':account_id}
        if type == 'abandon': res.update({'amount':0})
        return {'value': res}

    _columns = {
        'type': fields.selection([
                ('initial', 'Initial Value'),  
                ('reval', 'Revaluation'),      
                ('abandon','Abandonment'),
                ('sale','Sale')],     
        'History Type', required=True , readonly=True, states={'draft':[('readonly',False)]}),
        'quantity': fields.float('Quantity', readonly=True, states={'draft':[('readonly',False)]}),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
        'current_value': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'state': fields.selection([('draft','Draft'), 
                                    ('posted','Posted'),
                                    ('reversed','Reversed')], 'state', 
                                required=True , readonly=True),
        'account_id': fields.many2one('account.account', 'Depreciation Account', required=False
                                                    , readonly=True, states={'draft':[('readonly',False)]}),
        'name': fields.char('Description', size=64, select=1, readonly=True, states={'draft':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'User', required=True, readonly=True),
        'date': fields.date('Date', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'asset_id': fields.many2one('account.asset.asset', 'Asset', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'method_time': fields.selection([('number','Number of Depreciations'),('end','Ending Date')], 'Time Method',
                                  help="The method to use to compute the dates and number of depreciation lines.\n"\
                                       "Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.\n" \
                                       "Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond.",      
                                    readonly=True, states={'draft':[('readonly',False)]}),
        'method_number': fields.integer('Number of Depreciations', help="The number of depreciations needed to depreciate your asset", 
                                readonly=True, states={'draft':[('readonly',False)]}),
        'method_period': fields.integer('Period Length', help="Time in month between two depreciations", 
                                readonly=True, states={'draft':[('readonly',False)]}),
        'method_end': fields.date('Ending date', readonly=True, states={'draft':[('readonly',False)]}),
        'note': fields.text('Note', readonly=True, states={'draft':[('readonly',False)]}),
        'period_id': fields.many2one('account.period', 'Period'),

        'status': fields.char('Status', readonly=True, size=164),
    }
    _defaults = {
        'state': 'draft'
                }

    _constraints = [
        (_check_history_lines, _('Sorry!'), ['type']),
                   ]

    def _get_period(self, cr, uid, date, context={}):
        """Method to search corresponding period based on datec called by 
        create_operation_move method.

        @param date: date 
        @return: period ID
        """

        period_obj = self.pool.get('account.period')
        pids = period_obj.find(cr, uid, date, context=context)
        if pids: return pids[0] 
        return False

    def create_operation_move(self, cr, uid, ids, context={}):
        """
        Inherit method is used to post Asset sale, revaluation, abandon and initial values (initial can create 4 lines move)

        @return: list of account_move ids created by posted operation
        """

        move_obj=self.pool.get('account.move')
        moves = []
        for history in self.browse(cr, uid, ids, context):
            entries =[]
            move_id = False
            move_line_obj = self.pool.get('account.move.line')
            asset = history.asset_id
            period_id = self._get_period(cr, uid,history.date)
            if not period_id:
                history.write({'status':'No period for this operation'})
                continue
            for move in moves:
                if move['perion_id'] == period_id and  move['category_id'] == asset.category_id.id:
                    move_id = move['id']
                    break
            if not move_id:
                move_data = {
                    'journal_id': asset.category_id.journal_id.id,
                    'period_id': period_id,
                    'date': history.date,
                    'name': '/',
                    'history_id':history.id
                    }
                move_id = move_obj.create(cr, uid, move_data)   
                moves.append({ 'perion_id': period_id, 'category_id': asset.category_id.id, 'id':move_id })
            history.write({'current_value': asset.value_residual})

            line_data = {
                'journal_id': asset.category_id.journal_id.id,
                'period_id': period_id,
                'date': history.date,
                'name': '/',
                'asset_id':asset.id,
                'ref': asset.name,
                'move_id':move_id,
                'history_id':history.id
                }
            residual = 0
            accum =  0
            pl_amount = 0
            amount =  history.type in ('initial','reval') and history.amount or -(asset.purchase_value)
            if history.type in ('initial','reval'):
                residual = -history.amount
            else:
                if history.type=='sale': 
                    residual = history.amount   
                    asset.write({'state':'sold'})
                else: asset.write({'state':'abandon'})
                accum = asset.purchase_value - asset.value_residual - asset.salvage_value
                pl_amount =  asset.value_residual - residual + asset.salvage_value
            #for amount  in (residual,accum,pl_amount,amount):create move line
            line_data.update({
                'account_id': asset.category_id.account_asset_id.id,
                'debit': amount > 0 and amount or 0.0,
                'credit': amount < 0 and -amount or 0.0,
                'history_id':history.id 
                })
            line_id = move_line_obj.create(cr, uid, line_data)
            entries.append([(4, line_id, False)])
            if accum!=0:
                line_data.update({
                    'account_id': asset.category_id.account_depreciation_id.id,
                    'debit': accum > 0 and accum or 0.0,
                    'credit': accum < 0 and -accum or 0.0,
                    'history_id':history.id 
                    })
                line_id = move_line_obj.create(cr, uid, line_data)
                entries.append([(4, line_id, False)])
            if pl_amount!=0:
                if not asset.category_id.account_pl_id: 
                    raise osv.except_osv(_('Invalid action !'), _('Please configure p/l account for the category %s!')%(asset.category_id.name,))
                line_data.update({
                    'account_id': asset.category_id.account_pl_id.id,
                    'debit': pl_amount > 0 and pl_amount or 0.0,
                    'credit': pl_amount < 0 and -pl_amount or 0.0, 
                    'history_id':history.id
                    })
                line_id = move_line_obj.create(cr, uid, line_data)
                entries.append([(4, line_id, False)])

            if  residual != 0: 
                if history.account_id:
                    account_id = history.account_id.id 
                elif history.type == 'reval' and asset.category_id.account_reval_id:
                    account_id = asset.category_id.account_reval_id.id
                elif history.type == 'initial' and asset.category_id.account_initial_id:
                    account_id = asset.category_id.account_initial_id.id
                else:
                    raise osv.except_osv(_('Invalid action !'),
                         _('Please configure operation account for the category %s!')%(asset.category_id.name,))
                line_data.update({
                    'account_id':  account_id,
                    'debit': residual > 0 and residual or 0.0,
                    'credit': residual < 0 and -residual or 0.0, 
                    'history_id':history.id
                    })
                line_id = move_line_obj.create(cr, uid, line_data)
                entries.append([(4, line_id, False)])
            move_obj.completed(cr, uid, [move_id], context)
            move_obj.post(cr, uid, [move_id], context)  
            history.write({'state': 'posted'})        
            asset.write( {'account_move_line_ids': entries})
            self.pool.get('account.asset.asset').compute_depreciation_board(cr,uid, [asset.id],{})
        return [m['id'] for m in moves]  


class account_move_line(osv.osv):
    """Object to add history id in the asset move line object."""

    _inherit = 'account.move.line'
    _columns = {
        'history_id': fields.many2one('account.asset.history', 'Asset History'),

    }
account_move_line()

class account_asset_depreciation_line(osv.osv):
    _name = 'account.asset.depreciation.line'
    _description = 'Asset depreciation line'
    _inherit = 'account.asset.depreciation.line'

    def unlink(self, cr, uid, ids, context=None):
        """ Inherit unlink to  prohibit user from deleting reversed or posted depreciation line.

        @return: super unlink function
        """
        if not 'reverse_move' in context.keys():
           for board in self.browse(cr, uid, ids, context=context):
               if board.move_check: 
                  raise osv.except_osv(_('Error!'), _('You cannot delete posted depreciation line'))
        return super(account_asset_depreciation_line, self).unlink(cr, uid, ids, context=context)

class account_move(osv.osv):
    """ 
	Inherit account move object to change reverse function.
    """
    _inherit = 'account.move'
    
    def revert_move(self, cr, uid, ids, journal, period, date, reconcile=True, context=None):

        """ inherit revert move to reverse depreciation when reversing depreciation move
             and prohibit user of reversing move of operation

        @param journal: ID of the move journal to be reversed
        @param journal: ID of the period of the reversing move 
        @param date: date of the reversing move 
        @param reconcile: boolean partner reconcilation
        @return: ID of the new reversing move

        """

        asset_obj=self.pool.get('account.asset.asset')
        history_obj=self.pool.get('account.asset.history')
        move_line_obj=self.pool.get('account.move.line')
        depreciation_obj=self.pool.get('account.asset.depreciation.line')
        res = super(account_move, self).revert_move(cr, uid, ids, journal, period, date, reconcile=True, context=context)
        assets=[]
        history=[]
        for move in self.browse(cr,uid,ids,context):
            move_line_ids=move_line_obj.search(cr,uid,[('move_id','=',move.id),('debit','>',0)],context=context)
            for line in move_line_obj.browse(cr,uid,move_line_ids,context):
                asset_ids =asset_obj.search(cr,uid,[('id','=',line.asset_id.id)],context=context)
                history_ids =history_obj.search(cr,uid,[('id','=',line.history_id.id)],context=context)
                if asset_ids :assets.append(asset_ids[0])
                if history_ids :history.append(history_ids[0])
            if assets and not history :
               depreciation_ids=depreciation_obj.search(cr,uid,[('move_id','=',move.id),('asset_id','in',assets)],context=context)
               for depr in depreciation_obj.browse(cr,uid,depreciation_ids,context):
                   depreciation_obj.unlink(cr, uid, depr.id, context=context)
                   asset_obj.compute_depreciation_board(cr, uid,assets, context=context)
            elif history :
                 for h in history_obj.browse(cr,uid,history,context):
                     if h.type in ('initial','reval','sale','abandon'):
                        raise osv.except_osv(_('Error!'), _('You cannot reverse move for %s asset'%(h.type,)))
                      
        return res
    

class res_company(osv.Model):
    """
    Inherit company object to add field to allow user to conigure allow/disallow of skiping deprication.
    """

    _inherit = 'res.company'

    _columns = {
        'skip_depr':fields.boolean('Skip deprication'),
        
    }

class account_data_move(osv.Model):
    """
    object of data integration to create asset and intial, revlaue values.
    """

    _name = "account.data.move"

    _columns = {
        'comm_date': fields.date('Date'),
        'no_of_months': fields.integer('no of months'),
        'categ_code': fields.char('Category code', size=154),
        'location_code': fields.char('Location code', size=154),
        'total_depreciation': fields.float('Accumlative depreciation', digits_compute=dp.get_precision('Account')),
        'revalue_amount': fields.float('Revalue amount',digits_compute=dp.get_precision('Account')),
        'book_value': fields.float('Book value'),
        'quantity': fields.integer('Quantity'),
        'description': fields.char('Description', size=154),
        'status': fields.char('Status', size=154,readonly=True),
   
               }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
