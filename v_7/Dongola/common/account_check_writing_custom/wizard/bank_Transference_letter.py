# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields

class wizard_bank_transference_letter(osv.osv_memory):
    """
    Model to print bank transfer letter from payment
    """
    _name = 'wizard.bank.transference.letter'

    _description = 'Bank Transference Letter'

    _columns = {
        'name1': fields.char('First Signature', size=300, required=True),
        'name2': fields.char('Second Signature', size=300, required=True),
        'bank': fields.char('Bank Name & Number', size=300, required=True),
    }

    def act_bank_letter(self, cr, uid, ids, context=None):
        """
        Action button method that send wizard data to the report service
        
        @return: dictionary report service
        """
        return { 'type': 'ir.actions.report.xml', 
                'report_name': 'account.bank.transference.letter', 
                'datas': { 'ids': context.get('active_ids', []),
                            'model': context.get('active_model', 'ir.ui.menu'),
                            'form': self.read(cr, uid, ids, ['name1','name2','bank'])[0]
                        } 
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

