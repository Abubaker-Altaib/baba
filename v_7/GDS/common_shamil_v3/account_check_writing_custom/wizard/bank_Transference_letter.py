# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time

from openerp.osv import osv, fields
from openerp.tools.translate import _

class wizard_bank_transference_letter(osv.osv_memory):
    _name = 'wizard.bank.transference.letter'
    _description = 'Bank Transference Letter'    

    _columns = {
        'name1': fields.char('First Segniture', size=300, required=True),
        'name2': fields.char('Second Segniture', size=300, required=True),
        'bank': fields.char('Bank Name & Number', size=300, required=True),
        #'seq_id': fields.many2one('ir.sequence', 'Bank Letter Sequence ', help="Bank Letter Sequence Number.", required=True),
        #'seq': fields.related('sequence','seq' , type='char', relation='ir.sequence', string='Bank Letter Number' ,readonly=True),
        #'bank_letter_seq': fields.char('Letter Number', size=64, readonly=True , help="Bank Letter Sequence Number."),
        }
  

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}    


    def act_bank_letter(self, cr, uid, ids, context={}):
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['name1','name2','bank'])[0]
        

        # v.chk_seq =' ' happens when delete check no  
        return { 'type': 'ir.actions.report.xml', 'report_name': 'account.bank.transference.letter', 'datas': data}

wizard_bank_transference_letter()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

