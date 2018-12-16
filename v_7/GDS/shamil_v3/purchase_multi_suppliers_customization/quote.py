# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from tools.translate import _
from osv import osv
from osv import fields
import time
import netsvc

class multi_quote(osv.osv):
    """ class to add fields to purchase quote to check the products for more than one supplier """

    _inherit = 'pur.quote'
           
    def cancel(self, cr, uid, ids, context=None):
        """
        To modify the utomatic cancelling 
        """ 
        wf_service = netsvc.LocalService("workflow")        
        super(multi_quote, self).cancel(cr, uid, ids, context)
        multi_po = self.browse(cr, uid, ids)[0].pq_ir_ref.multi
        if multi_po in ['multiple']:
            qoute_obj = self.browse(cr, uid, ids)[0]
            requisition = self.pool.get('ireq.m').browse(cr, uid, qoute_obj.pq_ir_ref.id)
            requisition_qoute = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=', requisition.id)])
            count1=0
            count2=0
            for qoute in self.pool.get('pur.quote').browse(cr, uid, requisition_qoute):
                count1 += 1
                if qoute.state in ['done','cancel']:
                    count2 += 1
            if count1 == count2 :
                notes = self.pool.get('ireq.m').browse(cr, uid, qoute.pq_ir_ref.id).notes or ''
                self.pool.get('ireq.m').write(cr, uid, qoute.pq_ir_ref.id, {'state':'completed_quote','notes':notes})
                wf_service.trg_validate(uid, 'ireq.m', qoute.pq_ir_ref.id, 'completed_quote', cr) 
       
 

    def done(self,cr, uid, ids, context=None): 
        wf_service = netsvc.LocalService("workflow") 
        record = self.browse(cr, uid, ids)[0]
        req = self.pool.get('ireq.m').browse(cr, uid, record.pq_ir_ref.id)
        internal_products = self.pool.get('ireq.products')
        if not req.multi in ['multiple']:
            super(multi_quote, self).done(cr, uid, ids, context)
        else:
            all_qoutes = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=',req.id)])
            for product in self.pool.get('pur.quote').browse(cr, uid, all_qoutes):
                name1=''
                name2=''
                if product.id != record.id :
                    for pro in record.pq_pro_ids :
                        if pro.chosen :
                            name1 = pro.name
                            count = 0
                            for quots in product.pq_pro_ids :
                                if quots.chosen and record.state not in ['cancel']:
                                    name2=quots.name
                                    if name1==name2:
                                        count += 1
                                if count != 0:
                                    raise osv.except_osv(('Product is already chosen !'), ('The Product %s must be chosen just ones ...')%(name1,))
        self.write(cr, uid, ids, {'state':'done'})
        # For updating the internal requestion products prices
        quote = self.browse(cr, uid, ids)[0]
        for product in quote.pq_pro_ids:
            if product.req_product:
                internal_products_ids = product.req_product.id
            else: 
                internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
            internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
            internal_products.write(cr, uid, internal_products_ids, {'price_unit': product.price_unit })
        multi_po=self.browse(cr,uid,ids)[0].pq_ir_ref.multi
        #TODO check when to close the quote state 
        all_qoutes = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=',req.id)])
        count1=0
        count2=0
        for product in self.pool.get('pur.quote').browse(cr, uid, all_qoutes):
            count1 += 1
            if product.state in ['done','cancel']:
                count2 += 1
        if count1 == count2 :
            self.pool.get('ireq.m').write(cr, uid, product.pq_ir_ref.id, {'state':'completed_quote'})
            wf_service.trg_validate(uid, 'ireq.m', quote.pq_ir_ref.id, 'completed_quote', cr) 
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
