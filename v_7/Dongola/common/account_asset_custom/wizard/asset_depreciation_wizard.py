# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

#----------------------------------------
#asset_depreciation
#----------------------------------------

class asset_depreciation(osv.osv_memory):
    _name = "asset.depreciation"

    def _check_date(self, cr, uid, ids):
        """ Constrain method the check the date from should be less than the date to .

        @return: Boolean True or False
        """
        for rec in self.browse(cr, uid, ids):
            if rec.date_to < rec.date_from :
                return False
        return True

    _columns = {
	    'company_id': fields.many2one('res.company','Company', required=True),
	    'category_ids': fields.many2many('account.asset.category','depreciation_category_rel','depreciation_id','category_id','Category'),
	    'asset_ids': fields.many2many('account.asset.asset','depreciation_asset_rel','depreciation_id','asset_id','Asset'),
	    'date_from': fields.date('From', required=True),
	    'date_to': fields.date('TO', required=True),
   		 }

    _constraints = [
        (_check_date, 'Sorry date to must be bigger than data from!', ['date_from','date_to']),
                  ] 
 
    def deprecate_asset(self, cr, uid, ids, context={}):
        """ Method to deprecate_asset , deprecate a group of assets based on the category.

        @return: Boolean True 
        """
        self_obj=self.browse(cr, uid, ids, context = context)
        category_obj=self.pool.get('account.asset.category')
        asset_obj=self.pool.get('account.asset.asset')
        depreciation_line_obj=self.pool.get('account.asset.depreciation.line')
        period_obj=self.pool.get('account.period')
        ctx = dict(context, company_id=self_obj[0].company_id.id)
        ctx['account_period_prefer_normal'] = True
        frst_prd = period_obj.find(cr, uid, self_obj[0].date_from, context=ctx)
        lst_prd = period_obj.find(cr, uid, self_obj[0].date_to, context=ctx)
        if frst_prd != lst_prd :
            period_ids = period_obj.search(cr, uid, [('id','>=',frst_prd[0]),('id','<=',lst_prd[0])], context=ctx)
        else:
           period_ids=frst_prd
        for rec in self_obj:
            if rec.category_ids :
                category_recs=rec.category_ids
            else:
                category_ids=category_obj.search(cr,uid,[('company_id','=',rec.company_id.id)])
                if not  category_ids:
                    raise orm.except_orm(_('Warrning'), _('Sorry the company %s has no categories ') % (rec.company_id.name))
                category_recs=category_obj.browse(cr,uid,category_ids)
            for cat in category_recs :
                for period in period_obj.browse(cr, uid, period_ids, context=ctx) :
                    domain=[('company_id','=',rec.company_id.id),
                            ('state','=','open'),              
                            ('depreciation_line_ids.depreciation_date','>=',period.date_start),
                            ('depreciation_line_ids.depreciation_date','<=',period.date_stop),
                            ('depreciation_line_ids.move_check','=',False),('category_id','=',cat.id)]
                    domain+=rec.asset_ids and [('id','in',[ass.id for ass in rec.asset_ids])] 
                    asset_ids=asset_obj.search(cr,uid,domain)
                    if not asset_ids:
                        continue
                    #asset_obj.compute_depreciation_board(cr, uid, asset_ids, context=context)
                    domain=[('depreciation_date','>=',period.date_start),('depreciation_date','<=',period.date_stop),
                            ('move_check','=',False),('asset_id','in',asset_ids)]
                    depreciation_line_ids=depreciation_line_obj.search(cr,uid,domain)
                    if not depreciation_line_ids:
                        continue
                    ctx = dict(context, reference=cat.name)
                    ctx = dict(context, depreciation_date=period.date_start)
                    depreciation_line_obj.create_move(cr, uid, depreciation_line_ids, context=ctx)
        return True
