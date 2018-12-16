# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import netsvc
from tools.translate import _

class qoute(osv.osv):
    _inherit = 'pur.quote'

    def done(self, cr, uid, ids, n='',context=None): 
        wf_service = netsvc.LocalService("workflow") 
        super(qoute, self).done(cr, uid, ids, context=context)
        for quote in self.browse(cr, uid, ids):
           self.pool.get('ireq.m').write(cr, uid, quote.pq_ir_ref.id, {'state':'completed_quote'})
           wf_service.trg_validate(uid, 'ireq.m', quote.pq_ir_ref.id, 'completed_quote', cr) 
        return True
    
    
    def action_cancel_draft(self, cr, uid, ids, context=None): 
        """ 
        Changes order state to Draft.

        @return: True
        """
        for quote in self.browse(cr,uid,ids):
            rec_state = quote.pq_ir_ref.state
            print "rec_staterec_staterec_staterec_state",rec_state
        if rec_state in ["confirmed","in_progress_quote"] :
            if not len(ids):
                return False
            self.write(cr, uid, ids, {'state':'draft'}, context=context)
            wf_service = netsvc.LocalService("workflow")
            for s_id in ids:
                # Deleting the existing instance of workflow for PO
                wf_service.trg_delete(uid, 'pur.quote', s_id, cr)            
                wf_service.trg_create(uid, 'pur.quote', s_id, cr)
        else :
             raise osv.except_osv(_("Error"), _("You Can't Reset Quote After Approved The Winner Quote"))
        
        return True
    
    
    _columns = {

                'delivery_period': fields.integer('Delivery period', readonly=True, states={'draft':[('readonly', False)]},), 
                'delv_plan': fields.char('Delivery Plan', size=256 , readonly=True, states={'draft':[('readonly', False)]},), 
                'vat_supp': fields.boolean('VAT Legal Statement', states={'done':[('readonly', True)],'confirm':[('readonly', False)]},), 
                'pq_pro_ids':fields.one2many('pq.products', 'pr_pq_id' , 'Items', states={'cancel':[('readonly', True)],'done':[('readonly', True)]},), 
                 }
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
