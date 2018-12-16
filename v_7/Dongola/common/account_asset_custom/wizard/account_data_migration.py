# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv, orm
from tools.translate import _

class account_post_move(osv.osv_memory):
    """
    Account move line reconcile wizard, it checks for the write off the reconcile entry or directly reconcile.
    """
    _name = 'account.post.move'

    _columns = {
        'move_date': fields.date('Move date', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'init_account':fields.many2one('account.account', 'Initial Account'),
        'reval_account':fields.many2one('account.account', 'Revalue Account'),
    }

    def trans_rec_reconcile_full(self, cr, uid, ids, context=None):
        """Method to post data migration to the asset by:
            creating new asset, 
            create new opertion of initial then calling post method
            create new opertion of revalue then calling post method.

        @return: True
        """
        if context is None:
            context = {}
        context.update({'group':True})
        account_data = self.pool.get('account.data.move')
        location_obj=self.pool.get('account.asset.location')
        category_obj=self.pool.get('account.asset.category')
        asset_obj=self.pool.get('account.asset.asset')
        history_obj=self.pool.get('account.asset.history')
        depreciation_line_obj=self.pool.get('account.asset.depreciation.line')
        period_obj = self.pool.get('account.period')
        wiz_obj = self.browse(cr, uid, ids, context)[0]
        asset_ids = []
        dprc_line_ids=[]
        context.update({'company_id':wiz_obj.journal_id.company_id.id})
        pids = period_obj.find(cr, uid, wiz_obj.move_date, context=context)
        if not pids:
            raise osv.except_osv(_('Warning !'), _('Check the date'))
        if 'active_ids' in context and context['active_ids']:
            data = account_data.browse(cr, uid, context['active_ids'], context)
            for rec in data:        
                cat_id = category_obj.search(cr, uid, [('code', '=', rec.categ_code), ('company_id','=',wiz_obj.journal_id.company_id.id) ],context=context)  
                loc_id = location_obj.search(cr, uid, [('code', '=', rec.location_code) ],context=context) 
                if not loc_id:
                    account_data.write(cr, uid, rec.id, {'status': 'No location'}, context=context)
                    continue   
                if location_obj.browse(cr, uid, loc_id, context)[0].company_id.id != wiz_obj.journal_id.company_id.id:
                    account_data.write(cr, uid, rec.id, {'status': 'Different company and asset location Journals'}, context=context)  
                    continue    
                if not cat_id:
                    account_data.write(cr, uid, rec.id, {'status': 'No category'}, context=context)  
                    continue     
                if rec.book_value < 0 :
                    account_data.write(cr, uid, rec.id, {'status': 'Book value less than zero'}, context=context) 
                    continue 
                asset_id = asset_obj.create(cr,uid,{
                                                     'name':rec.description,
                                                     'category_id':cat_id[0],
                                                     'date_start': rec.comm_date ,
                                                     'period_id':pids, 
                                                     'quantity':rec.quantity,
                                                     'location':loc_id},context)
                asset_ids.append(int(asset_id)) 
                history_id=history_obj.create(cr,uid,{
                                                     'type':'initial',
                                                     'name':rec.description,
                                                     'quantity':rec.quantity,
                                                     'amount': rec.book_value ,
                                                     'account_id':wiz_obj.init_account.id,
                                                     'user_id':uid,
                                                     'date': wiz_obj.move_date,
                                                     'period_id': pids[0],
                                                     'asset_id':asset_id,
                                                    },context)
                history_obj.create_operation_move(cr,uid,[history_id],context)
                if rec.revalue_amount >  0:
                    history_id=history_obj.create(cr,uid,{
                                                     'type':'reval',
                                                     'name':rec.description,
                                                     'quantity':rec.quantity,
                                                     'amount': rec.revalue_amount ,
                                                     'account_id':wiz_obj.reval_account.id,
                                                     'user_id':uid,
                                                     'date': wiz_obj.move_date,
                                                     'period_id': pids[0],
                                                     'asset_id':asset_id,
                                                    },context)
                    history_obj.create_operation_move(cr,uid,[history_id],context)
                asset_obj.validate(cr,uid,[asset_id],context)
                if rec.total_depreciation > 0:
                    dprc_line_id=depreciation_line_obj.create(cr, uid,{'amount':rec.total_depreciation,
                                                      'name':rec.description,
                                                      'asset_id':asset_id,
                                                      'sequence':asset_id,
                                                      'depreciated_value':0.0,
                                                      'depreciation_date':wiz_obj.move_date,
                                                      'remaining_value':rec.book_value-rec.total_depreciation,
                                                       },context)
                    dprc_line_ids.append(dprc_line_id)
            if asset_ids:
                depreciation_line_obj.create_move( cr, uid, dprc_line_ids, context={})
                asset_obj.compute_depreciation_board(cr,uid,asset_ids,context)
                cr.execute('delete  FROM account_data_move WHERE id = %s ', (rec.id,))
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
