# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from docutils.nodes import Part









class res_partner_category(osv.Model):

      _inherit = 'res.partner.category'
      _columns = {


      'related_product_category_id' : fields.many2one('product.category' , 'Product Category' ),

                }

    


class purchase_requisition(osv.Model):
    
   
    _inherit = ['mail.thread', 'ir.needaction_mixin','purchase.requisition']
    _name = 'purchase.requisition'

    _columns = {
        
        'quotation_created' : fields.boolean('Quotation Created' ,readonly=True),
        'suppliers_qualifications': fields.selection([('qualified', 'Qualified'),
                                                      ('not_qualified', 'Not Qualified'),
                                   
                                   ], 'Suppliers Qualifications',),
        
        
                }



    _defaults = {
         
         'suppliers_qualifications': 'not_qualified',
         
         
         }






    def action_request_quotation(self, cr, uid, ids, context=None):
        
        """ This Function create quotations for selected partners """

        res = {}
        for rec in self.browse(cr,uid,ids):
            if not rec.supplier_ids:
               raise osv.except_osv(_('Error!'), _('Please Add The Suppliers First .... '))
        
            for partner in rec.supplier_ids:
                res = self.make_purchase_order(cr, uid, ids, partner.id)
            self.write(cr,uid,ids,{'quotation_created' : True })
        
        return True
        
    def action_create_quotations(self, cr, uid, ids, context=None):
        
        """ This Function create quotations for selected partners """

#         for rec in self.browse(cr,uid,ids):
#             if not rec.supplier_ids:
#                raise osv.except_osv(_('Error!'), _('Please Add The Suppliers First .... '))
#                   for partner in rec.supplier_ids:
        partner_obj = self.pool.get('res.partner')
        rec = self.browse(cr,uid,ids)[0]
        partner_ids = self.get_partner_ids(cr, uid, ids, rec, context=context)
        if partner_ids:
           for partner in partner_obj.browse(cr,uid,partner_ids):
                res = self.make_purchase_order(cr, uid, ids, partner.id)
           self.write(cr,uid,ids,{'quotation_created' : True })
        
        return True
    
    
    
      
    def get_partner_ids(self, cr, uid, ids, requesition, context=None):
        
        """ Method For Get The Partners Whom Supply these Products """
        
        partner_categ_ids = []
        partner_ids = []
        
        partner_categ_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        

        
        partner_categ_ids = partner_categ_obj.search( cr, uid, [('related_product_category_id' , '=' , requesition.category_id.id)])
        
        if partner_categ_ids :
           partner_ids = partner_obj.search(cr,uid,[('category_id' , 'in' , partner_categ_ids),('supplier' , '=' , True)])
        else :
           raise osv.except_osv(_('Warning!'), _('There are No Partners Assigned For Purchase Order Category . Please Make Sure You assigned category in Partner Category Form'))
       
        return partner_ids

    def action_rfq_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'purchase_send_email_quotation', 'email_template_edi_purchase_requisition')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'purchase.requisition',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        
                
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
       
       
        





    
