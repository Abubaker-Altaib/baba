# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _
from openerp import netsvc

class stock_picking(osv.Model):

    _inherit = "stock.picking"

    _columns = {
        'purchase_requisition_id' : fields.many2one('purchase.requisition' , 'Requisition ID'),   
        'state': fields.selection([
            ('draft', 'Draft'),
            ('complete', 'Waiting Department Manager'),
            ('validated' , 'Waiting General Department Manager'),
            ('auto', 'Waiting Another Operation'),
            ('in_progress', 'Purchase Order In Progress'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Waiting General HR Department Manager'),
            ('cancel', 'Cancelled'),
            ('approve_gm','Waiting Availability'),
            ('approve_ghrm','Ready to Deliver'),
            ('sign','Waiting Section Manager'),
            ('done', 'Delivered'),],
             'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: not confirmed yet and will not be scheduled until confirmed\n
            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability of products\n
            * Ready to Transfer: products reserved, simply waiting for confirmation.\n
            * Transferred: has been processed, can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore""" ),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):

        res = super(stock_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                            context=context, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            # Set all fields read only when state is close.
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field"):
                node_name = node.get('name')
                if node_name != 'move_lines':
                    node.set('attrs', "{'readonly': [('state', 'not in', ('draft','complete','validated'))]}")
                    setup_modifiers(node, res['fields'][node_name])

            res['arch'] = etree.tostring(doc)

        return res
#     def action_assign_wkf(self, cr, uid, ids, context=None):
#         """ Changes picking state to assigned if the category is technical.
#         and to approve_ghrm is not technical
#         @return: True
#         """
#         pick = self.browse(cr,uid,ids[0],context=context)
#         if pick.type not in ['in' , 'out']:
#                if pick.category_id.technical:
#                 self.write(cr, uid, ids, {'state': 'approve_ghrm'})
#                else:
#                 self.write(cr, uid, ids, {'state': 'assigned'})
#         return True



class stock_picking_in(osv.Model):

    _inherit = "stock.picking.in"

    def fields_view_get(self, cr, uid, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):

        res = super(stock_picking_in, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                            context=context, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            # Set all fields read only when state is close.
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field"):
                node_name = node.get('name')
                if node_name != 'move_lines':
                    node.set('attrs', "{'readonly': [('state', '!=', 'draft')]}")
                    setup_modifiers(node, res['fields'][node_name])

            res['arch'] = etree.tostring(doc)

        return res

        
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
    
    
    
    
    
    
        
    
        
        
        
        
    _columns = {
        'purchase_requisition_id' : fields.many2one('purchase.requisition' , 'Requisition ID'),   
        'state': fields.selection(
            [('draft', 'Draft'),
            ('complete', 'Waiting Department Manager'),
            ('validated' , 'Waiting General Department Manager'),
            ('auto', 'Waiting Another Operation'),
            ('in_progress', 'Purchase Order In Progress'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Waiting General HR Department Manager'),
            ('cancel', 'Cancelled'),
            ('approve_gm','Waiting Availability'),
            ('approve_ghrm','Ready to Deliver'),
            ('sign','Waiting Section Manager'),
            ('done', 'Delivered'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Deliver: products reserved, simply waiting for confirmation.\n
                 * Delivered: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }


    def fields_view_get(self, cr, uid, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):

        res = super(stock_picking_out, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                            context=context, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            # Set all fields read only when state is close.
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field"):
                node_name = node.get('name')
                if node_name not in ['move_lines', 'backorder_id'] :
                    #node.set('attrs', "{'readonly': [('state', 'not in', ('draft','complete','validated'))]}")
                    setup_modifiers(node, res['fields'][node_name])

            res['arch'] = etree.tostring(doc)

        return res


    def action_process(self, cr, uid, ids, context=None):

        if self.browse(cr, uid, ids[0], context=context).state == 'in_progress':
            raise osv.except_osv(_("ValidateError"),_('Purchase Requisition already sent!'))

        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.partial.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }
    


    class stock_location(osv.Model):
  
      

      _inherit = "stock.location"

      _columns = {

       'location_spec_type' : fields.selection([('admin','Administrive') ,('tech','Techincal') , ('multi','Multi')] , 'Location Specification Type' ,),


                 }

      



class product_product(osv.Model):
      _inherit = "product.product"
      
      
      
      
      
      

        
      _columns = {

       'it_product' : fields.boolean('IT Product' , help="When You Check this field that means this product will hide from employees and appears to IT User"),
       
                 }
 
 
 
 
 
 
    
class product_category(osv.osv):
    _inherit = "product.category"
    _columns={
        'technical':fields.boolean('technical'),
    }
#class stock_partial_picking_line(osv.TransientModel):




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
