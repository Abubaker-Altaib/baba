# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_move(osv.Model):
    """ 
	Inherit account move object to update object line by correct moves 
    when update move state.
    Changing in move should update the budget by add/delete move line from corresponding
    budget line.
	"""

    _inherit = 'account.move'

    def write(self, cr, uid, ids, vals, context={}):
        """
        The Completed, Closed and Posted Moves must be added to move_line_ids field 
        of the effected budget line

        @return: Update Move values
        """
        budget_line_obj = self.pool.get('account.budget.lines')
        for acc_move in self.browse(cr, uid, ids, context=context):
                for line in acc_move.line_id:
                    line_ids = budget_line_obj.search(cr, uid, [('general_account_id','=',line.account_id.id),
                                                                       ('analytic_account_id', '=', line.analytic_account_id.id),
                                                                       ('period_id', '=', line.period_id.id)],
                                                                       context=context)
                    budget_line_vals = (vals.get('state','') in ['completed','closed','posted'] and  \
                                       {'move_line_ids':[(1,line.id,{'budget_line_id':line_ids and line_ids[0]})]}) or \
                                       (line.budget_line_id and {'move_line_ids':[(3,line.id)]}) or {}
                    budget_line_obj.write(cr, uid, line_ids and line_ids[0] or [], budget_line_vals,context=context)
        return super(account_move,self).write(cr, uid, ids, vals, context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
