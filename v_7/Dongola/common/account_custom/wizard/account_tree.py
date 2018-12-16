# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_tree(osv.osv_memory):
    """
    This model to update consolidation chart of account and validate the account not belong in consolidate accounts
    """
    _name = "account.tree"

    _description = "Validate Account Move"

    _columns = {
        'type': fields.selection([('match', 'matches'), ('diff', 'difference')], 'Type'),
        'chart_account_id': fields.many2one('account.account', 'Chart of account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
    }

    _defaults = {
        'type':'diff',
    }

    def uniq( self,cr, uid, ids):
        """
        Get account id from all charts of account 
        
        @return: List of account ids
        """
        output = []
        accounts = []
        for x in ids:
            if x not in accounts:
                accounts.append(x)
            else:
                output.append(x)
        return output

    def validate_move(self, cr, uid, ids, context=None):
        """
        Validate all accounts belong in consolidation account or not
        
        @return: dictionary of values
        """
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        obj_account = self.pool.get('account.account')
        child_ids = obj_account._get_children_and_consol(cr, uid, [data['chart_account_id'][0]], context)
        consild = []
        for acc in obj_account.browse(cr, uid, child_ids, context=context):
            if acc.type in ('other','receivable','payable','closed','liquidity'):
                consild.append(acc.id)
        all_accounts = obj_account.search(cr, uid, [('type', 'in', ('other','receivable','payable','closed','liquidity'))], context=context)
        if data['type'] == 'diff':
            account_ids =  list(set(all_accounts) - set(consild))
        else:
            chart = obj_account.browse(cr, uid, data['chart_account_id'][0], context)
            consoli = obj_account.search(cr, uid, [('type', '=', 'consolidation'),('company_id', '=', chart.company_id.id)], context=context)
            account_ids = []
            for acc in obj_account.browse(cr, uid, consoli, context=context):
                cons = obj_account._get_children_and_consol(cr, uid, [acc.id], context)
                account_ids += cons
            account_ids = self.uniq(cr, uid, account_ids)#should be: account_ids  = list(set(account_ids)) 
        return {
                'domain': "[('id','in',%s)]" % account_ids,
                'name': 'Accounts',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'account.account',
                'type': 'ir.actions.act_window'
        }

    def update_consil(self, cr, uid, ids, context=None):
        """
        Update the consolidation account by add accounts from different chart of account to consolidate account 
        depend on code of account
        
        @return: dictionary of values
        """
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        obj_account = self.pool.get('account.account')
        chart = obj_account.browse(cr, uid, data['chart_account_id'][0], context)
        consoli = obj_account.search(cr, uid, [('type', '=', 'consolidation'),('company_id', '=', chart.company_id.id)], context=context)
        for acc in obj_account.browse(cr, uid, consoli, context=context):
            new_child_ids = obj_account.search(cr, uid, [('code', '=', acc.code),('company_id', '<>', acc.company_id.id)], context=context)
            obj_account.write(cr, uid, acc.id, {'child_consol_ids':[(6, 0, new_child_ids)]}, context=context)
        return {}


#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  

