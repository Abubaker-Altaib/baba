# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_move(osv.Model):
    """ 
    Inherit account move object to update object line by correct moves 
    when update move state.
    Changing in move should update the budget by add/delete move line from corresponding
    budget line.
    """

    _inherit = 'account.move'

    def write(self, cr, uid, ids, vals, context=None):
        """
        The Completed, Closed and Posted Moves must be added to move_line_ids field 
        of the effected budget line

        @return: Update Move values
        """
        new_accounts = {}
        deleted = []
        if 'line_id' in vals:
                for val in vals['line_id']:
                    #the line changed
                    if val[2]:
                        if 'analytic_account_id' in val[2] or 'account_id' in val[2]:
                            new_accounts[val[1]] = val[2]
                    if val[0] == 2:
                        #for delete case
                        deleted.append(val[1])
        budget_line_obj = self.pool.get('account.budget.lines')

        analytic_obj = self.pool.get('account.analytic.account')
        account_obj = self.pool.get('account.account')
        for acc_move in self.browse(cr, uid, ids, context=context):
            for line in acc_move.line_id:
                account_id = line.account_id.id
                analytic_account_id = line.analytic_account_id.id
                budget = line.analytic_account_id.budget
                analytic_required = line.account_id.user_type.analytic_required 
                if line.id in deleted:
                    continue
                if line.id in new_accounts:
                    if 'analytic_account_id' in new_accounts[line.id]:
                        if new_accounts[line.id]['analytic_account_id']:
                            analytic_account_id = new_accounts[line.id]['analytic_account_id']
                            analytic_account = analytic_obj.browse(cr,uid,analytic_account_id,context=context)
                            budget = analytic_account.budget
                        else:
                            #empty analytic account entered
                            budget = analytic_account_id = False

                    if 'account_id' in new_accounts[line.id]:
                        account_id = new_accounts[line.id]['account_id']
                        account_rec = account_obj.browse(cr,uid,account_id,context=context)
                        analytic_required = account_rec.user_type.analytic_required
                line_ids = budget_line_obj.search(cr, uid, [('general_account_id','=',account_id),
                                                                   ('analytic_account_id', '=', analytic_account_id),
                                                                   ('period_id', '=', line.period_id.id)],
                                                                   context=context)
                if not analytic_account_id and analytic_required:
                    raise orm.except_orm(_('Warning!'), _('Analytic Account Required!'))

                if not line_ids and budget:
                    raise orm.except_orm(_('Warning!'), _('This account has noo budget!'))
                budget_line_vals = (vals.get('state','') in ['completed','closed','posted'] and  \
                                   {'move_line_ids':[(1,line.id,{'budget_line_id':line_ids and line_ids[0]})]}) or \
                                   (line.budget_line_id and {'move_line_ids':[(3,line.id)]}) or {}
                budget_line_obj.write(cr, uid, line_ids and line_ids[0] or [], budget_line_vals,context=context)
        return super(account_move,self).write(cr, uid, ids, vals, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
