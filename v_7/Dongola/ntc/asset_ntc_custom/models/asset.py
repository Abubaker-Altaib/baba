# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from tools.translate import _
from lxml import etree


class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    
    def check_asset_age(self, cr, uid, context=None):
            asset_obj = self.pool.get("account.asset.asset")
            asset_ids = asset_obj.search(cr ,uid ,[('state','=','open'),])
            recipient_partners = []
            recipient_partners.append((4, uid))
            for asset in asset_obj.browse(cr, uid, asset_ids, context=context):
                asset_age = int(1/asset.category_id.depreciation_rate)
                months_befor_notifi = asset_age - asset.notification_period

                purchase_date = datetime.strptime(asset.purchase_date , '%Y-%m-%d')
                day = purchase_date.day
                month = purchase_date.month
                year = purchase_date.year

                notifi_date = (purchase_date+relativedelta(months=+months_befor_notifi)).date()
                notifi_date = datetime.strptime(str(notifi_date) , '%Y-%m-%d')
                current_date = datetime.strptime(time.strftime('%Y-%m-%d') , '%Y-%m-%d')
                if current_date == notifi_date :
                    post_vars = {'subject': "Asset Life Span Notification ",
                                     'body': _("Warning ! \n This asset %s will be reach the life span after %s month")%(asset.name, asset.notification_period),
                                     'partner_ids': recipient_partners,} # Where "4" adds the ID to the list 
                                               # of followers and "3" is the partner ID 
                    thread_pool = self.pool.get('mail.thread')
                    thread_pool.message_post(
                            cr, uid, False,
                            type="notification",
                            subtype="mt_comment",
                            context=context,
                            **post_vars)
            return True
    
        
    _columns = {
        'depreciation_rate': fields.float('Depreciation Rate', readonly=True, states={'draft':[('readonly',False)]}),
        'purchase_value': fields.float('Gross Value', readonly=True, digits=(16,2)),
        'value_residual': fields.float('Current (book) Value', readonly=True,digits=(16,2)),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ Returns views and fields for current model.
        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param view_id: list of fields, which required to read signatures
        @param view_type: defines a view type. it can be one of (form, tree, graph, calender, gantt, search, mdx)
        @param context: context arguments, like lang, time zone
        @param toolbar: contains a list of reports, wizards, and links related to current model

        @return: Returns a dictionary that contains definition for fields, views, and toolbars
        """
        if not context:
            context = {}
        user_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = super(account_asset_asset, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        #grop_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase_wafi', 'group_committee_user')
        doc = etree.XML(res['arch'])
        if user_obj.company_id.auto_move != False:
            for node in doc.xpath("//page[@string='Move Lines']"):
                parent = node.getparent()
                parent.remove(node)
            for node in doc.xpath("//button[@name='open_entries']"):
                parent = node.getparent()
                parent.remove(node)
            res['arch'] = etree.tostring(doc)

            
        return res

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        res = {'value':{}}
        asset_categ_obj = self.pool.get('account.asset.category')

        if category_id:
            category_obj = asset_categ_obj.browse(cr, uid, category_id, context=context)
            res['value'] = {
                            'method': category_obj.method,
                            'method_number': category_obj.method_number,
                            'method_time': category_obj.method_time,
                            'method_period': category_obj.method_period,
                            'method_progress_factor': category_obj.method_progress_factor,
                            'method_end': category_obj.method_end,
                            'prorata': category_obj.prorata,
                            'cat_depreciable':category_obj.depreciable,
                            'depreciation_rate':category_obj.depreciation_rate
            }
            self.write(cr, uid, ids, res['value'], context=context)
        return res

    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, purchase_date, context=None):
        #by default amount = 0
        amount = 0
        #purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
        amount = amount_to_depr * asset.depreciation_rate
        days = total_days - float(purchase_date.strftime('%j'))
        if i == 1:
            amount = (amount_to_depr * asset.depreciation_rate) / total_days * days
        elif i == undone_dotation_number:
            amount = (amount_to_depr * asset.depreciation_rate) / total_days * (total_days - days)
        return amount

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        
        for asset in self.browse(cr, uid, ids, context=context):
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if asset.value_residual == 0.0:
                if old_depreciation_line_ids:
                    depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)
                continue
            tt = 0
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            #old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual

            purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
            depreciation_date = datetime(purchase_date.year, 12, 31)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366
            tt = int(1/asset.category_id.depreciation_rate)
            rr = tt+1
            for x in range(len(posted_depreciation_line_ids), rr):
                i = x + 1
                amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, rr, posted_depreciation_line_ids, total_days, purchase_date, context=context)
                
                residual_amount -= amount
                vals = {
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount,
                     'depreciated_value': asset.value_residual - (residual_amount + amount),
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (datetime(year, month, day) + relativedelta(months=+12))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True


class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'
    
    _columns = {
        'depreciation_rate': fields.float('Depreciation Rate'),
    }
    _defaults = {
        'depreciation_rate': 0.5,
    }


class account_asset_history(osv.osv):

    _inherit = 'account.asset.history'

    _rec_name = 'type'

    def  _check_history_lines(self, cr, uid, ids, context=None): 
        """ Constrain fucntion to prohibit user from making teo operation at a time and 
        prohibit user to make any operation on zero value asset.

        @return: True or raise message
        """
        for hst in self.browse(cr, uid, ids, context=context):
            if hst.type=='abandon' and hst.state=='draft':
                if hst.amount > hst.asset_id.value_residual:
                    raise orm.except_orm(_('Warrning'), _('The abandon value Must be lower than book value') )
            intial=self.search(cr, uid, [('asset_id','=',hst.asset_id.id),('type','=','initial'),('id','!=',hst.id)], context=context)
            if hst.type=='initial':
                if intial:
                    raise orm.except_orm(_('Warrning'), _('Sorry the Intial value has already been intered you can not repeat this process!') )
                return True
            else:
                msg=not intial and 'Sorry no intial value for this asset please set it first to complate this process !' or \
                    self.search(cr, uid, [('asset_id','=',hst.asset_id.id),('state','=','draft'),('id','!=',hst.id)], context=context) and\
                    hst.state not in  ('reversed','posted') and 'Sorry you need to post draft prosess first to complate this process !' or ''
                if msg :
                    raise orm.except_orm(_('Warrning'), msg )
                return True

    _constraints = [
        (_check_history_lines, _('Sorry!'), ['type']),
    ]


    def create_operation_move(self, cr, uid, ids, context={}):
        '''
        Method is used to post Asset sale, revaluation, rehabilitation, abandon and initial values (initial can create 4 lines move)
        '''
        move_obj=self.pool.get('account.move')
        asset_obj=self.pool.get('account.asset.asset')
        moves = []
        for history in self.browse(cr, uid, ids, context):
		asset = history.asset_id
		if history.type in ('initial'):
		    asset.write({'purchase_value': history.amount, 'value_residual': history.amount})
		if history.type in ('rehabilitation'):
		    asset.write({'value_residual': asset.value_residual + history.amount})
		if history.type in ('reval'):
		    asset.write({'value_residual': history.amount})
		if history.type=='sale': 
		        asset.write({'value_residual': 0.0})   
		        asset.write({'state':'sold'})
		if history.type=='abandon': 
		        asset.write({'value_residual': asset.value_residual - history.amount})
		        if (asset.value_residual - history.amount) == 0.0 :
		            asset.write({'state':'abandon'})
		
		history.write({'state': 'posted'})
		self.pool.get('account.asset.asset').compute_depreciation_board(cr,uid, [asset.id],{})

        return True


class account_asset_depreciation_line(osv.Model):
    """
    A depreciation object to calculate and store the depreciation amount based on configured terms.
    """
    _inherit = 'account.asset.depreciation.line'

    def create_move(self, cr, uid, ids, context=None):
        """
        create_move, over write the original create_move to create one move for a group of depreciation lines .
        """
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
        for line in self.browse(cr, uid, ids, context=context):
            move_vals = {
                'name': 'Depreciation Of/ ',
                'date': depreciation_date,
                'ref': context.get('reference') or '',
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            
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
            vals = line.asset_id.value_residual - amount
            line.asset_id.write({'value_residual':vals})
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

