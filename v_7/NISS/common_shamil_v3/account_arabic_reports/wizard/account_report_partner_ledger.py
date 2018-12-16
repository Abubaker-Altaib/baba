# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_partner_ledger(osv.osv_memory):
    """
    This wizard will provide the partner Ledger report by periods, between any two dates.
    """
    _inherit = 'account.partner.ledger'

    _columns = {
        'reconcil': fields.boolean('Include Reconciled Entries', help='Consider reconciled entries'),
        'account_ids': fields.many2many('account.account', 'report_account_partner_account_rel', 'report_account_id', 'account_id', 'Accounts'),
        'partner_ids': fields.many2many('res.partner', 'report_account_partner_rel', 'report_account_id', 'partner_id', 'Partners'),
        'cumulate_move': fields.boolean('Cumulate move balance'),

    }

    def _get_partner(self, cr, uid, context=None):
        return self.pool.get('res.partner').search(cr, uid, [])

    _defaults = {
       'reconcil': True,
       'cumulate_move':True,
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):

        res = super(account_partner_ledger, self)._print_report(cr, uid, ids, data, context=context)
        data = res['datas']
        data['form'].update(self.read(cr, uid, ids, ['reconcil', 'account_ids', 'partner_ids','cumulate_move'])[0])
        #if data['form']['page_split']:
            #res.update({'report_name': 'account.third_party_ledger.arabic'})
        #else:
        res.update({'report_name': 'account.partner.ledger.other.arabic'})
        res.update({'datas':data})
        return res

account_partner_ledger()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
