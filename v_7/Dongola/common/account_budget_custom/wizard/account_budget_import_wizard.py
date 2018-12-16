# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class account_budget_import(osv.osv_memory):
    """
    Model that allow budget accountant importing percentage of fiscalyear budget amounts from any fiscalyear budget in the system
    """
    _name = "account.budget.import"
    
    _description = 'Budget import'


    def _fy_budget_id(self, cr, uid, context=None):
        """
        Method return the current active fiscalyear budget if the wizard run from inside fiscalyear record
        """
        if context is None: 
            context = {}
        if context.get('active_model',False) == 'account.fiscalyear.budget' and context.get('active_id',False) and \
            self.pool.get('account.fiscalyear.budget').browse(cr, uid, context.get('active_id'), context=context).state != 'draft':
            raise orm.except_orm(_('Warning!'), _("You cann't modify not draft budget!"))
        return context.get('active_model',False) == 'account.fiscalyear.budget' and context.get('active_id',False)
    
    _columns = {
        'from_fy_budget_id': fields.many2one('account.fiscalyear.budget', 'From Fiscal Year Budget', required=True),
        'to_fy_budget_id': fields.many2one('account.fiscalyear.budget', 'To Fiscal Year Budget', required=True),
        'percent': fields.float('Percent', required=True, help='The percentage that use when import prev budget amount.\nExample:\n-100: To import budget amount as it is.\n-80: To import 80 perc of budget amount.\n-120: To import budget amount plus 20 perc of it\'s amount.', digits_compute=dp.get_precision('Account')),
        'fy_budget_line_ids': fields.many2many('account.fiscalyear.budget.lines', 'account_budget_import_rel', 'budget_import_id', 'budget_line_id', 'Budget Lines', required=True),
    }

    _defaults = {
        'percent': 100,
        'to_fy_budget_id':_fy_budget_id,
    }

    def import_budget(self, cr, uid, ids, context=None):
        ids = not isinstance(ids, list) and [ids] or ids
        fy_budget_line_pool = self.pool.get('account.fiscalyear.budget.lines')
        wiz = self.browse(cr, uid, ids, context=context)[0]
        fy_budget_line = wiz.fy_budget_line_ids
        for line in fy_budget_line:
            current_id = fy_budget_line_pool.search(cr, uid, [('general_account_id','=',line.general_account_id.id),('account_fiscalyear_budget_id','=',wiz.to_fy_budget_id.id)], context=context)
            if current_id:
                fy_budget_line_pool.write(cr, uid, current_id, {'planned_amount': line.planned_amount*wiz.percent/100}, context=context)
            else:
                fy_budget_line_pool.create(cr, uid, {'account_fiscalyear_budget_id': wiz.to_fy_budget_id.id,
                                                 'general_account_id': line.general_account_id.id,
                                                 'planned_amount': line.planned_amount*wiz.percent/100}, context=context)
        return {'type':'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
