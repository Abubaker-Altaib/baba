# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class customs_fee_letter_report(osv.osv_memory):
    _name = "customs.fee.letter.report"
    _description = "Customs Fee Letter Report"
    
    
    _columns = {
        'type' : fields.selection([('development','Development'),('emeregency','Emeregency')],'Account'),
        'document_type' : fields.selection([('bill_of_lading','Bill Of Lading'),('invoice','Invoice'),('certf_customs','customs Certifite'),('abdication_certificate','Abdication Certificate')],'Type Of Document'),
        'request_clearance_ids': fields.many2many('purchase.clearance','customs_fee_letter_wizard_rel','counter','request_id', string='Requests'), 



    }


    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]

        datas = {
             'ids': [],
             'model': 'purchase.clearance',
             'form': data,
            }
        if not datas['form']['request_clearance_ids']:
           raise osv.except_osv( _('No Selected Data !'), _('Please make sure you selected at least one request..'))
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'customs_fee_letter_report',
            'datas': datas,
            }

    
