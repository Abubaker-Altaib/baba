# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm

#----------------------------------------------------------
#  Bank Statement (Inherit)
#----------------------------------------------------------
class account_bank_statement(osv.Model):

    _inherit = "account.bank.statement"

    def view_reconciled_moves(self, cr, uid, ids, context=None):

        '''
        This function returns an action that display reconciled moves of given Bank Statement.
        '''
        mod_obj = self.pool.get('ir.model.data')
        for record in self.browse(cr, uid, ids, context=context):

            action_model, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'account', 'action_account_moves_all_a'))
            action = self.pool.get(action_model).read(cr, uid, action_id, context=context)
            ctx = eval(action['context'])
            form_view_ids = [view_id for view_id, view in action['views'] if view == 'form']
            view_id = form_view_ids and form_view_ids[0] or False
            action.update({
                'views': [],
                'view_mode': 'tree',
                'view_id': view_id,
                'domain':[('statement_id','=',ids[0])],
            })

        action.update({
            'context': ctx,
        })
        return action
