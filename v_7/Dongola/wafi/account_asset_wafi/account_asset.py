# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
##############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class account_asset_category(osv.osv):

    _inherit = 'account.asset.category'

    _columns = {
        'account_rehabilitation_id': fields.many2one('account.account', 'Rehabilitation Account'),
    }


class account_asset_history(osv.osv):

    _inherit = 'account.asset.history'

    _rec_name = 'type'

    def onchange_type(self, cr, uid, ids, asset_id, type,category_id=False,  context=None):
        """
        onchange Method used to change the account of the asset  when select operation set it according to operations account in categories. 
        
        @return: dic
        """
        user_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        account_id = False
        res = {}
        if asset_id:
            category = category_id and self.pool.get('account.asset.category').browse(cr, uid, category_id, context=context) or \
                        self.pool.get('account.asset.asset').browse(cr, uid, asset_id, context=context).category_id
            account_id = type=='reval' and category.account_reval_id  and  category.account_reval_id.id or \
                         type=='rehabilitation' and category.account_rehabilitation_id  and  category.account_initial_id.id or \
                         type=='initial' and category.account_initial_id  and  category.account_initial_id.id or \
                         type=='sale' and category.account_sale_id  and  category.account_sale_id.id or False
        res = {'account_id':account_id,'auto_move':user_obj.company_id.auto_move,}
        if type == 'abandon': res.update({'amount':0})
        return {'value': res}

    _columns = {
        'type': fields.selection([
                ('rehabilitation', 'Rehabilitation'),
                ('initial', 'Initial Value'),
                ('reval', 'Revaluation'),
                ('abandon','Abandonment'),
                ('sale','Sale')] , 'Type' ), 
        'rehab_type': fields.selection([
                ('part_rehab', 'Partial Rehab'),  
                ('total_rehab', 'Total Rehab ') ] , 'Rehab Type'),
    }

    def create_operation_move(self, cr, uid, ids, context={}):
        '''
        Method is used to post Asset sale, revaluation, rehabilitation, abandon and initial values (initial can create 4 lines move)
        '''
        move_obj=self.pool.get('account.move')
        asset_obj=self.pool.get('account.asset.asset')
        moves = []
        for history in self.browse(cr, uid, ids, context):
            if history.auto_move==True:
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

    ##History type and 
    #             for asset in asset_obj.browse(cr, uid, ids, context):
                if history.type =='initial':
                    line_name = 'Initial value for: ' + str(asset.serial_no)
                    if not asset.serial_no:
                        seq = asset_obj.seq(cr, uid, [asset.id], context)
                        line_name = 'Initial value for:'+u' '.join((seq)).encode('utf-8').strip()
                if history.type =='abandon' :
                    line_name = 'Abandon Asset: ' + u' '.join((asset.serial_no)).encode('utf-8').strip()
                if history.type =='reval' :
                    line_name = 'Revlue Asset: ' + u' '.join((asset.serial_no)).encode('utf-8').strip()
                if history.type =='sale' :
                    line_name = 'Sale Asset: ' + u' '.join((asset.serial_no)).encode('utf-8').strip()
                if history.type =='rehabilitation' :
                    line_name = 'Rehabilitation Asset: ' + u' '.join((asset.serial_no)).encode('utf-8').strip()
                line_data = {
                    'journal_id': asset.category_id.journal_id.id,
                    'period_id': period_id,
                    'date': history.date,
                    'name': line_name,
                    'asset_id':asset.id,
                    'ref': asset.name,
                    'move_id':move_id,
                    'history_id':history.id
                    }
                residual = 0
                accum =  0
                pl_amount = 0
                amount =  history.type in ('initial','rehabilitation') and history.amount or history.type=='reval' and history.amount-history.asset_value or -(asset.purchase_value)
                if history.type in ('initial','rehabilitation'):
                    residual = -history.amount
                elif history.type=='reval':
                    residual = history.asset_value - history.amount
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
                    elif history.type == 'rehabilitation' and asset.category_id.account_rehabilitation_id:
                        account_id = asset.category_id.account_rehabilitation_id.id    
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
            else:
                history.write({'state': 'posted'})

        return [m['id'] for m in moves]


class account_move(osv.osv):
    _inherit = 'account.move'

    def revert_move(self, cr, uid, ids, journal, period, date, reconcile=True, context=None):
        """ 
        Inherit revert move to reverse depreciation asset and constrains to asset history move 
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
                    if h.type in ('initial','reval','sale','abandon','rehabilitation'):
                        raise osv.except_osv(_('Error!'), _('You cannot reverse move for %s asset'%(h.type,)))
        return True

class product_template(osv.osv):

    _inherit = 'product.template'

    _columns = {
        'asset_track'      : fields.selection([('asset','Asset'),('asset_part','Asset Part')], 'Asset Track'),
        'asset_category_id': fields.many2one('account.asset.category','Asset Category'),
        'asset_id'         : fields.many2one('account.asset.asset','Asset'),
    }
class product_product(osv.osv):

    _inherit = 'product.product'    
    def onchange_asset_track(self, cr, uid, ids,asset_id):
        return {'value':{'asset_id'         : False,
                         'asset_category_id': False,}}

class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'

    _columns = {
        'asset_track': fields.selection([('asset','Asset'),('asset_part','Asset Part')], 'Asset Track'),
        'asset_id'   : fields.many2one('account.asset.asset','Asset'),
    }

    def onchange_asset_track(self, cr, uid, ids,asset_id):
        return {'value':{'asset_id'         : False,
                         'asset_category_id': False,}}

    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context, company_id) 
        template = self.pool.get('product.product').browse(cr,uid,product, context=context)

        if template :
            res['value']['asset_id']          = template.asset_id.id or False
            res['value']['asset_track']       = str(template.asset_track) or False
            res['value']['asset_category_id'] = template.asset_category_id.id or False
        return res


    def asset_create(self, cr, uid, lines, context=None):
        context = context or {}
        asset_obj = self.pool.get('account.asset.asset')
        account_asset_history = self.pool.get('account.asset.history')
        for line in lines:
            if line.asset_id:
                vals = {
                    'name': line.name,
                    'type': 'rehabilitation',
                    'amount': line. price_subtotal ,
                    'account_id': line.asset_id.category_id.account_rehabilitation_id.id,
                    'asset_id':line.asset_id.id,
                    'company_id': line.invoice_id.company_id.id,
                    'period_id': line.invoice_id.period_id.id,
                    'date' : line.invoice_id.date_invoice,
                }
                account_asset_history_id = account_asset_history.create(cr, uid, vals, context=context)

            if line.asset_category_id:
                vals = {
                    'name': line.name,
                    'code': line.invoice_id.number or False,
                    'category_id': line.asset_category_id.id,
                    'purchase_value': line.price_subtotal,
                    'period_id': line.invoice_id.period_id.id,
                    'partner_id': line.invoice_id.partner_id.id,
                    'company_id': line.invoice_id.company_id.id,
                    'currency_id': line.invoice_id.currency_id.id,
                    'purchase_date' : line.invoice_id.date_invoice,
                }
                changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
                vals.update(changed_vals['value'])
                asset_id = asset_obj.create(cr, uid, vals, context=context)
                if line.asset_category_id.open_asset:
                    asset_obj.validate(cr, uid, [asset_id], context=context)
               
        return True
