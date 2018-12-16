# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class request_financial_ratification(osv.osv_memory):
    _name = "request.financial.ratification"
    _description = "Request Financial Ratification Report"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    report_type = [
            ('with_items', 'With Items'),
            ('without_items', 'Without Items'),
            ('suppliers_only' , 'Suppliers Only')

            

                      ]

    _columns = {
        'request_financial_ids': fields.many2many('ireq.m','request_financial_wizard_rel','counter','request_id', string='Requests'), 
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'report_type' : fields.selection(report_type ,'Report Type ',select=True,required=True),
        'purchase_purposes': fields.char('Purchase purposes', size=256 ,required=True, ),


    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'request.financial.ratification', context=c),
                'report_type' : 'without_items',  
                'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]

        datas = {
             'ids': [],
             'model': 'ireq.m',
             'form': data,
            }
        if not datas['form']['request_financial_ids']:
           raise osv.except_osv( _('No Selected Data !'), _('Please make sure you selected at least one request..'))
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'request_financial_ratification',
            'datas': datas,
            }

    
