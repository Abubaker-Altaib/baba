# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class intial_request_summation(osv.osv_memory):
    _name = "intial.request.summation"
    _description = "Intial Request Summation Report"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    
    _columns = {
        'purchase_purposes': fields.char('Purchase purposes', size=256 ,required=True, ),
        'request_ids': fields.many2many('ireq.m','intial_request_summation_wizard_rel','counter','request_id', string='Requests'), 
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),


    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'request.financial.ratification', context=c),
                'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        
        datas = {
             'ids': [],
             'model': 'ireq.m',
             'form': data,
            }
        ireq_m_obj = self.pool.get('ireq.m')
                                                                                                   
        if not datas['form']['request_ids']:
           raise osv.except_osv( _('No Selected Data !'), _('Please make sure you selected at least one request..'))
          
        if len(datas['form']['request_ids']) != 1:
            first_rec_department_id = ireq_m_obj.browse(cr,uid,datas['form']['request_ids'])[0].department_id.id
           
            for record in ireq_m_obj.browse(cr,uid,datas['form']['request_ids']):
                if first_rec_department_id != record.department_id.id :
                   raise osv.except_osv( _('Bad Action !'), _('You Must Select Requests for Same Department..'))
                   
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'intial_request_summation',
            'datas': datas,
            }

    
